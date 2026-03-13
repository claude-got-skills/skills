"""Markdown change report generation with unified diffs.

Merges diff.py functionality (per review finding) for MVP simplicity.
"""

import difflib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field

from .config import REPORTS_DIR, Source

logger = logging.getLogger(__name__)


@dataclass
class SourceResult:
    """Result of checking a single source."""
    source: Source
    status: str             # "changed", "unchanged", "new", "error"
    new_hash: str = ""
    old_hash: str | None = None
    content: str = ""
    previous_content: str = ""
    extraction_method: str = ""
    error_message: str = ""
    consecutive_failures: int = 0


@dataclass
class CheckReport:
    """Aggregated results of a full freshness check."""
    results: list[SourceResult] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    dry_run: bool = False

    @property
    def changed(self) -> list[SourceResult]:
        return [r for r in self.results if r.status in ("changed", "new")]

    @property
    def unchanged(self) -> list[SourceResult]:
        return [r for r in self.results if r.status == "unchanged"]

    @property
    def errors(self) -> list[SourceResult]:
        return [r for r in self.results if r.status == "error"]

    @property
    def has_changes(self) -> bool:
        return len(self.changed) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def high_priority_changes(self) -> list[SourceResult]:
        return [r for r in self.changed if r.source.is_high_priority]


# ── Diff Generation ─────────────────────────────────────────────────────────

def generate_diff(old_content: str, new_content: str, source_name: str) -> str:
    """Generate a unified diff between old and new content.

    Returns empty string if no meaningful diff (e.g., both empty).
    """
    if not old_content and not new_content:
        return ""

    old_lines = (old_content or "").splitlines(keepends=True)
    new_lines = (new_content or "").splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"previous/{source_name}",
        tofile=f"current/{source_name}",
        n=3,  # context lines
    )

    return "".join(diff)


def _truncate_diff(diff_text: str, max_lines: int = 100) -> str:
    """Truncate a diff to a maximum number of lines."""
    lines = diff_text.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return diff_text
    truncated = "".join(lines[:max_lines])
    remaining = len(lines) - max_lines
    truncated += f"\n... ({remaining} more lines truncated)\n"
    return truncated


# ── Report Generation ────────────────────────────────────────────────────────

def generate_report(report: CheckReport) -> str:
    """Generate a markdown change report."""
    lines = []

    # Header
    lines.append("# Freshness Check Report")
    lines.append("")
    lines.append(f"**Date:** {report.started_at[:10]}")
    lines.append(f"**Started:** {report.started_at}")
    lines.append(f"**Finished:** {report.finished_at}")
    if report.dry_run:
        lines.append("**Mode:** Dry run (checkpoint not updated)")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Changed:** {len(report.changed)}")
    lines.append(f"- **Unchanged:** {len(report.unchanged)}")
    lines.append(f"- **Errors:** {len(report.errors)}")
    lines.append(f"- **Total:** {len(report.results)}")
    lines.append("")

    # High-priority changes
    if report.high_priority_changes:
        lines.append("### High-Priority Changes")
        lines.append("")
        for r in report.high_priority_changes:
            lines.append(f"- **{r.source.name}** ({r.source.url})")
        lines.append("")

    # Errors section
    if report.errors:
        lines.append("## Errors")
        lines.append("")
        for r in report.errors:
            lines.append(f"### {r.source.name}")
            lines.append(f"- **URL:** {r.source.url}")
            lines.append(f"- **Error:** {r.error_message}")
            if r.consecutive_failures >= 3:
                lines.append(f"- **Consecutive failures:** {r.consecutive_failures} (ALERT)")
            lines.append("")

    # Changes with diffs
    if report.changed:
        lines.append("## Changes")
        lines.append("")

        for r in report.changed:
            priority_tag = " [HIGH]" if r.source.is_high_priority else ""
            lines.append(f"### {r.source.name}{priority_tag}")
            lines.append("")
            lines.append(f"- **URL:** {r.source.url}")
            lines.append(f"- **Status:** {r.status}")
            lines.append(f"- **Extraction:** {r.extraction_method}")
            lines.append(f"- **KB files:** {', '.join(r.source.kb_files)}")

            if r.status == "new":
                lines.append(f"- **Note:** First time seeing this source")
            else:
                lines.append(f"- **Old hash:** `{r.old_hash[:12]}...`")
            lines.append(f"- **New hash:** `{r.new_hash[:12]}...`")
            lines.append("")

            # Include diff if we have previous content
            if r.previous_content and r.content:
                diff = generate_diff(r.previous_content, r.content, r.source.name)
                if diff:
                    diff = _truncate_diff(diff)
                    lines.append("<details>")
                    lines.append(f"<summary>Diff ({_count_diff_changes(diff)})</summary>")
                    lines.append("")
                    lines.append("```diff")
                    lines.append(diff.rstrip())
                    lines.append("```")
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")

    # Unchanged sources (compact)
    if report.unchanged:
        lines.append("## Unchanged Sources")
        lines.append("")
        for r in report.unchanged:
            lines.append(f"- {r.source.name}")
        lines.append("")

    return "\n".join(lines)


def _count_diff_changes(diff_text: str) -> str:
    """Count additions and deletions in a diff for the summary line."""
    additions = sum(1 for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff_text.splitlines() if line.startswith("-") and not line.startswith("---"))
    return f"+{additions}/-{deletions}"


def save_report(report: CheckReport) -> str | None:
    """Generate and save a markdown report. Returns the file path."""
    content = generate_report(report)
    date_str = report.started_at[:10]
    # Add time to avoid collisions on multiple runs per day
    time_str = report.started_at[11:16].replace(":", "")
    filename = f"freshness-{date_str}-{time_str}.md"
    filepath = REPORTS_DIR / filename

    try:
        with open(filepath, "w") as f:
            f.write(content)
        logger.info("Report saved to %s", filepath)
        return str(filepath)
    except OSError as e:
        logger.error("Failed to save report: %s", e)
        return None


# ── Classified Report ────────────────────────────────────────────────────────

# Category ordering (most actionable first)
_CATEGORY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# Category descriptions for the report
_CATEGORY_DESCRIPTIONS = {
    "CRITICAL": "Breaking changes, deprecations, removed features -- immediate update needed",
    "HIGH": "New features, tools, pricing changes -- update within days",
    "MEDIUM": "Documentation improvements, clarifications -- may improve accuracy",
    "LOW": "Formatting, typos, link changes -- no action needed",
}


def _build_classification_lookup(classifications: list[dict]) -> dict[str, dict]:
    """Build a lookup from source_name to classification dict."""
    lookup = {}
    for c in classifications:
        name = c.get("source_name", "")
        if name:
            lookup[name] = c
    return lookup


def generate_classified_report(
    report: CheckReport,
    classifications: list[dict],
) -> str:
    """Generate a markdown report with changes grouped by actionability category.

    This replaces the standard "## Changes" section with category-grouped sections,
    showing the most critical changes first.
    """
    lines = []
    lookup = _build_classification_lookup(classifications)

    # Header
    lines.append("# Freshness Check Report (Classified)")
    lines.append("")
    lines.append(f"**Date:** {report.started_at[:10]}")
    lines.append(f"**Started:** {report.started_at}")
    lines.append(f"**Finished:** {report.finished_at}")
    if report.dry_run:
        lines.append("**Mode:** Dry run (checkpoint not updated)")
    lines.append("**Classification:** Enabled (Haiku)")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Changed:** {len(report.changed)}")
    lines.append(f"- **Unchanged:** {len(report.unchanged)}")
    lines.append(f"- **Errors:** {len(report.errors)}")
    lines.append(f"- **Total:** {len(report.results)}")
    lines.append("")

    # Classification summary table
    lines.append("### Classification Breakdown")
    lines.append("")
    lines.append("| Category | Count | Action Required |")
    lines.append("|----------|-------|-----------------|")
    for cat in _CATEGORY_ORDER:
        count = sum(1 for c in classifications if c.get("category") == cat)
        if count > 0:
            lines.append(f"| **{cat}** | {count} | {_CATEGORY_DESCRIPTIONS.get(cat, '')} |")
    lines.append("")

    # Errors section (same as original)
    if report.errors:
        lines.append("## Errors")
        lines.append("")
        for r in report.errors:
            lines.append(f"### {r.source.name}")
            lines.append(f"- **URL:** {r.source.url}")
            lines.append(f"- **Error:** {r.error_message}")
            if r.consecutive_failures >= 3:
                lines.append(f"- **Consecutive failures:** {r.consecutive_failures} (ALERT)")
            lines.append("")

    # Changes grouped by category
    for cat in _CATEGORY_ORDER:
        # Find changes that belong to this category
        cat_changes = []
        for r in report.changed:
            classification = lookup.get(r.source.name)
            if classification and classification.get("category") == cat:
                cat_changes.append((r, classification))

        if not cat_changes:
            continue

        lines.append(f"## {cat} Changes")
        lines.append("")
        lines.append(f"*{_CATEGORY_DESCRIPTIONS.get(cat, '')}*")
        lines.append("")

        for r, classification in cat_changes:
            priority_tag = " [HIGH]" if r.source.is_high_priority else ""
            lines.append(f"### {r.source.name}{priority_tag}")
            lines.append("")
            lines.append(f"- **Classification:** {cat}")
            lines.append(f"- **Reasoning:** {classification.get('reasoning', 'N/A')}")
            affected = classification.get("affected_files", [])
            if affected:
                lines.append(f"- **Affected files:** {', '.join(affected)}")
            lines.append(f"- **URL:** {r.source.url}")
            lines.append(f"- **Status:** {r.status}")
            lines.append(f"- **Extraction:** {r.extraction_method}")
            lines.append(f"- **KB files:** {', '.join(r.source.kb_files)}")

            if r.status == "new":
                lines.append("- **Note:** First time seeing this source")
            else:
                lines.append(f"- **Old hash:** `{r.old_hash[:12]}...`")
            lines.append(f"- **New hash:** `{r.new_hash[:12]}...`")
            lines.append("")

            # Include diff if we have previous content
            if r.previous_content and r.content:
                diff = generate_diff(r.previous_content, r.content, r.source.name)
                if diff:
                    diff = _truncate_diff(diff)
                    lines.append("<details>")
                    lines.append(f"<summary>Diff ({_count_diff_changes(diff)})</summary>")
                    lines.append("")
                    lines.append("```diff")
                    lines.append(diff.rstrip())
                    lines.append("```")
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")

    # Any changes that were not classified (shouldn't happen, but defensive)
    unclassified = [r for r in report.changed if r.source.name not in lookup]
    if unclassified:
        lines.append("## Unclassified Changes")
        lines.append("")
        for r in unclassified:
            lines.append(f"- **{r.source.name}** ({r.source.url})")
        lines.append("")

    # Unchanged sources (compact)
    if report.unchanged:
        lines.append("## Unchanged Sources")
        lines.append("")
        for r in report.unchanged:
            lines.append(f"- {r.source.name}")
        lines.append("")

    return "\n".join(lines)


def save_classified_report(
    report: CheckReport,
    classifications: list[dict],
) -> str | None:
    """Generate and save a classified markdown report. Returns the file path."""
    content = generate_classified_report(report, classifications)
    date_str = report.started_at[:10]
    time_str = report.started_at[11:16].replace(":", "")
    filename = f"freshness-{date_str}-{time_str}-classified.md"
    filepath = REPORTS_DIR / filename

    try:
        with open(filepath, "w") as f:
            f.write(content)
        logger.info("Classified report saved to %s", filepath)
        return str(filepath)
    except OSError as e:
        logger.error("Failed to save classified report: %s", e)
        return None
