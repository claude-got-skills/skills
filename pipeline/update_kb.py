"""Auto-update knowledge base files when CRITICAL or HIGH changes are detected.

Sprint 3 of the freshness pipeline. Uses Claude Sonnet 4.6 to intelligently
merge new scraped content into existing KB files, preserving structure, formatting,
and manually-added notes.

Safety:
- Only updates files in knowledge-base/ directory
- Never touches SKILL.md, references/, or skills/ files
- Falls back gracefully on LLM errors (logs and skips)
- Truncates inputs to stay within token budget
"""

import difflib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import KB_DIR, Source

logger = logging.getLogger(__name__)

# Model for intelligent merging — smarter than Haiku, cheaper than Opus
MERGE_MODEL = "claude-sonnet-4-6"

# Max characters of scraped content to send to the merge LLM.
# Sonnet 4.6 has 200K context; we budget ~60K chars (~15K tokens) for new content,
# plus existing KB content, plus the prompt.
MAX_NEW_CONTENT_CHARS = 60_000
MAX_EXISTING_CONTENT_CHARS = 40_000

# Directories/paths that must NEVER be updated (Sprint 4 — human review gate)
PROTECTED_PATTERNS = [
    "SKILL.md",
    "skills/",
    "references/",
    ".claude/",
    ".claude-plugin/",
]

NEW_KB_TEMPLATE = """\
# {source_name}

> Source: {source_url}
> Last updated: {date}
> Auto-generated from freshness pipeline

{content}
"""

MERGE_PROMPT = """\
You are a technical editor for a knowledge base that tracks Claude's capabilities.
Your task is to merge updated documentation into an existing knowledge base file.

## Rules

1. Preserve the existing KB file's structure, heading hierarchy, and any manually-added \
context or notes.
2. Update facts, parameters, code examples, and descriptions that have changed in the \
new content.
3. Add new sections for new features or capabilities not in the existing file.
4. Remove or clearly mark as deprecated any content that is no longer present in the \
new documentation source.
5. Keep markdown formatting consistent with the existing file.
6. Do NOT add commentary, explanations, or meta-notes about what you changed. Return \
ONLY the updated file content.
7. If the new content is substantially different in scope (e.g., a completely restructured \
page), restructure the KB file to match while preserving any unique context from the \
original.

## Source information

Source name: {source_name}
Source URL: {source_url}

## Existing KB file content

```
{existing_content}
```

## New scraped content from source

```
{new_content}
```

Return ONLY the updated KB file content. No wrapping code fences, no explanations."""


@dataclass
class KBUpdateResult:
    """Result of updating a single KB file."""
    kb_filename: str
    source_name: str
    source_url: str
    status: str          # "updated", "created", "skipped", "error"
    diff: str = ""       # Human-readable diff of changes
    error_message: str = ""
    chars_before: int = 0
    chars_after: int = 0


def update_kb_files(
    classifications: list[dict],
    report,
    client,
) -> list[KBUpdateResult]:
    """Auto-update KB files for CRITICAL and HIGH classifications.

    Args:
        classifications: List of classification dicts from classify_results().
            Each has: category, reasoning, affected_files, source_name, source_url.
        report: CheckReport with SourceResult objects containing scraped content.
        client: An anthropic.Anthropic client instance.

    Returns:
        List of KBUpdateResult objects describing what was updated.
    """
    if client is None:
        logger.error("No API client provided — cannot update KB files")
        return []

    # Filter for actionable classifications only
    actionable = [
        c for c in classifications
        if c.get("category") in ("CRITICAL", "HIGH")
    ]

    if not actionable:
        logger.info("No CRITICAL or HIGH classifications — nothing to update")
        return []

    logger.info(
        "Found %d actionable classification(s) to process",
        len(actionable),
    )

    # Build lookup: source_name -> SourceResult (for accessing scraped content)
    source_results = {}
    for r in report.changed:
        source_results[r.source.name] = r

    results = []

    for classification in actionable:
        source_name = classification.get("source_name", "")
        source_url = classification.get("source_url", "")
        affected_files = classification.get("affected_files", [])
        category = classification.get("category", "")

        logger.info(
            "[%s] Processing '%s' — %d affected file(s)",
            category, source_name, len(affected_files),
        )

        # Get the scraped content for this source
        source_result = source_results.get(source_name)
        if source_result is None:
            logger.warning(
                "No SourceResult found for '%s' — skipping",
                source_name,
            )
            continue

        new_content = source_result.content
        if not new_content:
            logger.warning(
                "Empty scraped content for '%s' — skipping",
                source_name,
            )
            continue

        # Update each affected KB file
        for kb_filename in affected_files:
            result = _update_single_kb_file(
                kb_filename=kb_filename,
                source_name=source_name,
                source_url=source_url,
                new_content=new_content,
                client=client,
            )
            results.append(result)

    # Log summary
    updated = sum(1 for r in results if r.status == "updated")
    created = sum(1 for r in results if r.status == "created")
    skipped = sum(1 for r in results if r.status == "skipped")
    errors = sum(1 for r in results if r.status == "error")
    logger.info(
        "KB update complete: %d updated, %d created, %d skipped, %d errors",
        updated, created, skipped, errors,
    )

    return results


def _update_single_kb_file(
    kb_filename: str,
    source_name: str,
    source_url: str,
    new_content: str,
    client,
) -> KBUpdateResult:
    """Update or create a single KB file using LLM-assisted merge.

    Args:
        kb_filename: Filename within knowledge-base/ directory.
        source_name: Human-readable source name.
        source_url: URL of the source.
        new_content: New scraped content to merge in.
        client: Anthropic API client.

    Returns:
        KBUpdateResult describing the outcome.
    """
    # Safety check: ensure we're only touching KB files
    if not _is_safe_kb_path(kb_filename):
        logger.warning(
            "Refusing to update protected path: %s",
            kb_filename,
        )
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="skipped",
            error_message=f"Protected path — not a knowledge-base file: {kb_filename}",
        )

    kb_path = KB_DIR / kb_filename

    # Check if KB file exists
    if kb_path.exists():
        return _merge_into_existing(
            kb_path=kb_path,
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            new_content=new_content,
            client=client,
        )
    else:
        return _create_new_kb_file(
            kb_path=kb_path,
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            new_content=new_content,
        )


def _merge_into_existing(
    kb_path: Path,
    kb_filename: str,
    source_name: str,
    source_url: str,
    new_content: str,
    client,
) -> KBUpdateResult:
    """Merge new content into an existing KB file using Claude."""
    try:
        existing_content = kb_path.read_text(encoding="utf-8")
    except OSError as e:
        logger.error("Failed to read KB file %s: %s", kb_path, e)
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="error",
            error_message=f"Failed to read existing file: {e}",
        )

    chars_before = len(existing_content)

    # Truncate inputs to stay within token budget
    truncated_existing = _truncate_content(existing_content, MAX_EXISTING_CONTENT_CHARS)
    truncated_new = _truncate_content(new_content, MAX_NEW_CONTENT_CHARS)

    prompt = MERGE_PROMPT.format(
        source_name=source_name,
        source_url=source_url,
        existing_content=truncated_existing,
        new_content=truncated_new,
    )

    try:
        logger.info("  Calling %s to merge into %s ...", MERGE_MODEL, kb_filename)
        response = client.messages.create(
            model=MERGE_MODEL,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

        merged_content = response.content[0].text

        # Strip any accidental wrapping code fences the model might add
        merged_content = _strip_code_fences(merged_content)

    except Exception as e:
        logger.error(
            "LLM merge failed for %s: %s",
            kb_filename, e,
        )
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="error",
            error_message=f"LLM merge call failed: {e}",
            chars_before=chars_before,
        )

    # Sanity check: don't write empty or suspiciously short content
    if not merged_content or len(merged_content) < 50:
        logger.warning(
            "LLM returned empty/short content for %s (%d chars) — skipping",
            kb_filename, len(merged_content) if merged_content else 0,
        )
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="error",
            error_message=f"LLM returned suspiciously short content ({len(merged_content) if merged_content else 0} chars)",
            chars_before=chars_before,
        )

    # Generate human-readable diff
    diff = _generate_diff(existing_content, merged_content, kb_filename)

    # Check if content actually changed
    if existing_content.strip() == merged_content.strip():
        logger.info("  No changes needed for %s", kb_filename)
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="skipped",
            error_message="LLM merge produced identical content",
            chars_before=chars_before,
            chars_after=chars_before,
        )

    # Write the updated content
    try:
        kb_path.write_text(merged_content, encoding="utf-8")
        chars_after = len(merged_content)
        logger.info(
            "  Updated %s (%d -> %d chars)",
            kb_filename, chars_before, chars_after,
        )
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="updated",
            diff=diff,
            chars_before=chars_before,
            chars_after=chars_after,
        )
    except OSError as e:
        logger.error("Failed to write KB file %s: %s", kb_path, e)
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="error",
            error_message=f"Failed to write updated file: {e}",
            chars_before=chars_before,
        )


def _create_new_kb_file(
    kb_path: Path,
    kb_filename: str,
    source_name: str,
    source_url: str,
    new_content: str,
) -> KBUpdateResult:
    """Create a new KB file from the template using scraped content."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Truncate content if extremely long
    truncated = _truncate_content(new_content, MAX_NEW_CONTENT_CHARS)

    file_content = NEW_KB_TEMPLATE.format(
        source_name=source_name,
        source_url=source_url,
        date=date_str,
        content=truncated,
    )

    try:
        kb_path.write_text(file_content, encoding="utf-8")
        chars_after = len(file_content)
        logger.info(
            "  Created new KB file %s (%d chars)",
            kb_filename, chars_after,
        )
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="created",
            diff=f"(new file: {chars_after} chars)",
            chars_before=0,
            chars_after=chars_after,
        )
    except OSError as e:
        logger.error("Failed to create KB file %s: %s", kb_path, e)
        return KBUpdateResult(
            kb_filename=kb_filename,
            source_name=source_name,
            source_url=source_url,
            status="error",
            error_message=f"Failed to create file: {e}",
        )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _is_safe_kb_path(filename: str) -> bool:
    """Check if a filename is safe to update (only knowledge-base files).

    Rejects anything that matches protected patterns or tries to escape
    the knowledge-base directory via path traversal.
    """
    # Block path traversal
    if ".." in filename or filename.startswith("/"):
        return False

    # Block protected patterns
    for pattern in PROTECTED_PATTERNS:
        if pattern in filename:
            return False

    # Must end with .md (knowledge base files are markdown)
    if not filename.endswith(".md"):
        return False

    # Must be a simple filename (no subdirectory paths)
    if "/" in filename:
        return False

    return True


def _truncate_content(text: str, max_chars: int) -> str:
    """Truncate content to stay within token budget."""
    if len(text) <= max_chars:
        return text
    return (
        text[:max_chars]
        + f"\n\n... (truncated, {len(text) - max_chars:,} chars omitted)"
    )


def _strip_code_fences(text: str) -> str:
    """Strip wrapping code fences if the model accidentally adds them."""
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        # Remove opening fence (possibly with language tag like ```markdown)
        first_newline = stripped.find("\n")
        if first_newline > 0:
            stripped = stripped[first_newline + 1:]
        # Remove closing fence
        stripped = stripped[:-3].rstrip()
    return stripped


def _generate_diff(old_content: str, new_content: str, filename: str) -> str:
    """Generate a human-readable unified diff between old and new content."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff_lines = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3,
    )

    diff_text = "".join(diff_lines)

    # Truncate very large diffs for readability
    lines = diff_text.splitlines(keepends=True)
    if len(lines) > 200:
        diff_text = "".join(lines[:200])
        remaining = len(lines) - 200
        diff_text += f"\n... ({remaining} more diff lines truncated)\n"

    return diff_text


def format_update_summary(results: list[KBUpdateResult]) -> str:
    """Format update results into a human-readable summary for logging/reports.

    Args:
        results: List of KBUpdateResult objects.

    Returns:
        Markdown-formatted summary string.
    """
    if not results:
        return "No KB files were updated."

    lines = []
    lines.append("## Knowledge Base Updates")
    lines.append("")

    # Group by status
    updated = [r for r in results if r.status == "updated"]
    created = [r for r in results if r.status == "created"]
    skipped = [r for r in results if r.status == "skipped"]
    errors = [r for r in results if r.status == "error"]

    lines.append(f"**Updated:** {len(updated)} | **Created:** {len(created)} | "
                 f"**Skipped:** {len(skipped)} | **Errors:** {len(errors)}")
    lines.append("")

    if updated:
        lines.append("### Updated Files")
        lines.append("")
        for r in updated:
            lines.append(f"- **{r.kb_filename}** ({r.chars_before:,} -> {r.chars_after:,} chars)")
            lines.append(f"  - Source: {r.source_name}")
            if r.diff:
                # Show a compact summary of changes
                additions = sum(1 for line in r.diff.splitlines()
                               if line.startswith("+") and not line.startswith("+++"))
                deletions = sum(1 for line in r.diff.splitlines()
                               if line.startswith("-") and not line.startswith("---"))
                lines.append(f"  - Changes: +{additions}/-{deletions} lines")
        lines.append("")

    if created:
        lines.append("### Created Files")
        lines.append("")
        for r in created:
            lines.append(f"- **{r.kb_filename}** ({r.chars_after:,} chars)")
            lines.append(f"  - Source: {r.source_name}")
        lines.append("")

    if errors:
        lines.append("### Errors")
        lines.append("")
        for r in errors:
            lines.append(f"- **{r.kb_filename}**: {r.error_message}")
        lines.append("")

    return "\n".join(lines)
