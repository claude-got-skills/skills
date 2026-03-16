#!/usr/bin/env python3
"""Freshness check orchestrator — main entry point.

Scrapes Anthropic documentation sources, detects changes via SHA-256 hashing,
generates markdown change reports, and notifies via macOS notifications.

Usage:
    python -m pipeline.freshness_check              # Full check
    python -m pipeline.freshness_check --dry-run     # Check without updating checkpoint
    python -m pipeline.freshness_check --source URL  # Check single source
    python -m pipeline.freshness_check --force       # Re-check all (ignore recency)
    python -m pipeline.freshness_check --quiet       # Suppress notifications
    python -m pipeline.freshness_check --classify    # Classify changes by actionability
    python -m pipeline.freshness_check --classify --update-kb  # Classify + auto-update KB
    python -m pipeline.freshness_check --classify --update-kb --propose-edits  # Full pipeline
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    SOURCES,
    RUN_HISTORY_FILE,
    LOG_DIR,
    load_env,
    get_source_by_url,
)
from .scrape import extract_content
from .detect import (
    load_checkpoint,
    save_checkpoint,
    detect_change,
    update_checkpoint_entry,
    get_previous_content,
    record_scrape_failure,
    clear_failure_count,
)
from .report import CheckReport, SourceResult, save_report, save_classified_report
from .notify import notify_changes, notify_errors, notify_no_changes
from .classify import classify_results, get_api_client
from .update_kb import update_kb_files, format_update_summary
from .propose_edits import propose_skill_edits, format_proposal_summary

logger = logging.getLogger(__name__)

# Alert threshold for consecutive scrape failures
FAILURE_ALERT_THRESHOLD = 3


def setup_logging(verbose: bool = False) -> None:
    """Configure logging to stdout and log file."""
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / "freshness-check.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Clear existing handlers
    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)


def record_run_history(
    started_at: str,
    finished_at: str,
    changed: int,
    errors: int,
    total: int,
    dry_run: bool,
    report_path: str | None,
) -> None:
    """Append a run entry to the run-history file."""
    history = []
    if RUN_HISTORY_FILE.exists():
        try:
            with open(RUN_HISTORY_FILE) as f:
                history = json.load(f)
        except (json.JSONDecodeError, OSError):
            history = []

    history.append({
        "started_at": started_at,
        "finished_at": finished_at,
        "changed": changed,
        "errors": errors,
        "total": total,
        "dry_run": dry_run,
        "report_path": report_path,
    })

    # Keep last 100 runs
    history = history[-100:]

    try:
        with open(RUN_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except OSError as e:
        logger.warning("Failed to write run history: %s", e)


def run_check(
    sources: list,
    dry_run: bool = False,
    force: bool = False,
    quiet: bool = False,
    classify: bool = False,
    update_kb: bool = False,
    propose_edits: bool = False,
) -> CheckReport:
    """Run the freshness check against all specified sources.

    Args:
        sources: List of Source objects to check.
        dry_run: If True, do not update the checkpoint.
        force: If True, re-check all sources regardless of recency.
        quiet: If True, suppress macOS notifications.
        classify: If True, classify detected changes by actionability.
        update_kb: If True (requires classify), auto-update KB files for
            CRITICAL and HIGH changes.
        propose_edits: If True (requires update_kb), generate edit proposals
            for SKILL.md and reference files based on KB updates.

    Returns:
        CheckReport with all results.
    """
    report = CheckReport(
        started_at=datetime.now(timezone.utc).isoformat(),
        dry_run=dry_run,
    )

    checkpoint = load_checkpoint()

    logger.info("Checking %d source(s)%s", len(sources), " (dry run)" if dry_run else "")
    logger.info("=" * 60)

    for source in sources:
        logger.info("")
        logger.info("--- %s ---", source.name)
        logger.info("URL: %s", source.url)
        logger.info("Type: %s | Priority: %s", source.page_type, source.priority)

        # Extract content
        start_time = time.time()
        content, extraction_method = extract_content(source.url, source.page_type)
        elapsed = time.time() - start_time

        if content is None:
            # Scrape failed
            consecutive = record_scrape_failure(checkpoint, source.url)
            logger.error(
                "Scrape FAILED (%.1fs) — %d consecutive failure(s)",
                elapsed, consecutive,
            )
            result = SourceResult(
                source=source,
                status="error",
                error_message=f"Extraction failed using {extraction_method}",
                consecutive_failures=consecutive,
            )
            report.results.append(result)
            continue

        logger.info("Extracted %d chars via %s (%.1fs)", len(content), extraction_method, elapsed)

        # Clear failure count on success
        clear_failure_count(checkpoint, source.url)

        # Detect changes
        previous_content = get_previous_content(checkpoint, source.url)
        has_changed, new_hash, old_hash = detect_change(source.url, content, checkpoint)

        if has_changed:
            status = "new" if old_hash is None else "changed"
            logger.info("CHANGE DETECTED (status: %s)", status)
        else:
            status = "unchanged"
            logger.info("No change")

        result = SourceResult(
            source=source,
            status=status,
            new_hash=new_hash,
            old_hash=old_hash,
            content=content,
            previous_content=previous_content or "",
            extraction_method=extraction_method,
        )
        report.results.append(result)

        # Update checkpoint entry (even for unchanged, to update last_checked)
        if not dry_run:
            update_checkpoint_entry(
                checkpoint, source.url, new_hash, content, extraction_method,
            )

    # Save checkpoint
    if not dry_run:
        save_checkpoint(checkpoint)

    report.finished_at = datetime.now(timezone.utc).isoformat()

    # Generate and save report
    report_path = save_report(report)

    # Classify changes if requested
    classifications = []
    kb_update_results = []
    client = None
    if classify and report.has_changes:
        logger.info("")
        logger.info("--- Classification ---")
        client = get_api_client()
        if client:
            classifications = classify_results(report.changed, client)
            # Save an updated report with classification data
            classified_path = save_classified_report(report, classifications)
            if classified_path:
                logger.info("Classified report: %s", classified_path)

            # Auto-update KB files if requested
            if update_kb and classifications:
                logger.info("")
                logger.info("--- KB Auto-Update ---")
                kb_update_results = update_kb_files(classifications, report, client)
                if kb_update_results:
                    summary = format_update_summary(kb_update_results)
                    logger.info("\n%s", summary)
            elif update_kb and not classifications:
                logger.info("No classifications to update KB from")
        else:
            logger.warning("Skipping classification — no API client available")
    elif classify and not report.has_changes:
        logger.info("No changes to classify")
    elif update_kb and not classify:
        logger.warning("--update-kb requires --classify — skipping KB update")

    # Generate edit proposals if requested (Sprint 4)
    proposal_result = None
    if propose_edits and kb_update_results:
        logger.info("")
        logger.info("--- Edit Proposals ---")
        proposal_result = propose_skill_edits(kb_update_results, client)
        if proposal_result.changes:
            summary = format_proposal_summary(proposal_result)
            logger.info("\n%s", summary)
    elif propose_edits and not kb_update_results:
        logger.info("No KB updates to generate proposals from")
    elif propose_edits and not update_kb:
        logger.warning("--propose-edits requires --update-kb — skipping proposals")

    # Record run history
    record_run_history(
        started_at=report.started_at,
        finished_at=report.finished_at,
        changed=len(report.changed),
        errors=len(report.errors),
        total=len(report.results),
        dry_run=dry_run,
        report_path=report_path,
    )

    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("  Changed:   %d", len(report.changed))
    logger.info("  Unchanged: %d", len(report.unchanged))
    logger.info("  Errors:    %d", len(report.errors))
    if classifications:
        from .classify import CATEGORIES
        for cat in CATEGORIES:
            count = sum(1 for c in classifications if c["category"] == cat)
            if count:
                logger.info("  %s:  %d", cat.ljust(10), count)
    if kb_update_results:
        updated_count = sum(1 for r in kb_update_results if r.status == "updated")
        created_count = sum(1 for r in kb_update_results if r.status == "created")
        error_count = sum(1 for r in kb_update_results if r.status == "error")
        logger.info("  KB updated: %d | created: %d | errors: %d",
                     updated_count, created_count, error_count)
    if proposal_result and proposal_result.changes:
        logger.info("  Proposals: %d change(s) | %d skipped | report: %s",
                     len(proposal_result.changes), len(proposal_result.skipped),
                     proposal_result.proposal_path)
    if report_path:
        logger.info("  Report:    %s", report_path)

    # Send notifications
    if not quiet:
        if report.has_errors:
            error_names = [r.source.name for r in report.errors if r.consecutive_failures >= FAILURE_ALERT_THRESHOLD]
            if error_names:
                notify_errors(len(error_names), error_names)

        if report.has_changes:
            notify_changes(
                len(report.changed),
                len(report.high_priority_changes),
            )
        elif not report.has_errors:
            # Only send "no changes" if there are also no errors
            notify_no_changes(len(sources))

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check Anthropic documentation sources for changes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check without updating the checkpoint",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Check a single source URL only",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-check all sources regardless of recency",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress macOS notifications",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--classify",
        action="store_true",
        help="Classify detected changes by actionability (requires ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--update-kb",
        action="store_true",
        dest="update_kb",
        help="Auto-update KB files for CRITICAL/HIGH changes (requires --classify)",
    )
    parser.add_argument(
        "--propose-edits",
        action="store_true",
        dest="propose_edits",
        help="Generate edit proposals for SKILL.md/references from KB updates (requires --update-kb)",
    )

    args = parser.parse_args()

    # Load environment
    load_env()

    # Setup logging
    setup_logging(verbose=args.verbose)

    # Determine sources to check
    if args.source:
        source = get_source_by_url(args.source)
        if source is None:
            logger.error("Unknown source URL: %s", args.source)
            logger.error("Known sources:")
            for s in SOURCES:
                logger.error("  %s", s.url)
            sys.exit(1)
        sources = [source]
    else:
        sources = SOURCES

    # Run the check
    report = run_check(
        sources=sources,
        dry_run=args.dry_run,
        force=args.force,
        quiet=args.quiet,
        classify=args.classify,
        update_kb=args.update_kb,
        propose_edits=args.propose_edits,
    )

    # Exit with error if any scrapes failed
    if report.has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
