"""Change classification using Claude Haiku.

Classifies detected changes from freshness reports into actionability categories
so reports highlight what matters most.

Categories:
- CRITICAL: Breaking changes, model deprecations, removed features
- HIGH: New features, new tools, pricing changes
- MEDIUM: Documentation improvements, clarifications, expanded examples
- LOW: Formatting, typos, link changes
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# The model used for classification — cheapest and fastest
CLASSIFY_MODEL = "claude-haiku-4-5-20251001"

# Ordered from most to least actionable
CATEGORIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# Default category when classification fails
DEFAULT_CATEGORY = "MEDIUM"

CLASSIFICATION_PROMPT = """\
You are a documentation change classifier for a Claude capabilities skill/plugin.
Your job is to classify a detected change in Anthropic documentation by how urgently
the skill's content needs updating.

## Categories

- **CRITICAL**: Breaking changes, model deprecations, removed features, API endpoint \
changes, security advisories. Requires immediate SKILL.md update.
- **HIGH**: New features, new tools, new model releases, pricing changes, new platform \
capabilities. Requires knowledge-base and skill content update within days.
- **MEDIUM**: Documentation improvements, clarifications, expanded examples, rewording \
of existing content. May improve skill accuracy but not urgent.
- **LOW**: Formatting changes, typos, link changes, navigation updates, boilerplate \
changes (headers/footers/sidebars). No action needed.

## Instructions

Classify the following change. Return ONLY valid JSON (no markdown fences) with these fields:
- "category": one of CRITICAL, HIGH, MEDIUM, LOW
- "reasoning": 1-2 sentence explanation of why this category was chosen
- "affected_files": list of knowledge-base or skill files that would need updating \
(use the kb_files hint if provided, or suggest based on the change content)

## Source information

Source name: {source_name}
Source URL: {source_url}
Source type: {page_type}
KB files mapped to this source: {kb_files}

## Change summary

{change_summary}
"""


def classify_change(
    change_summary: str,
    source_name: str,
    source_url: str = "",
    page_type: str = "",
    kb_files: list[str] | None = None,
    client=None,
) -> dict:
    """Classify a single change using Claude Haiku.

    Args:
        change_summary: The diff or description of what changed.
        source_name: Human-readable name of the source (e.g., "Claude Code CHANGELOG").
        source_url: The URL of the source.
        page_type: The source page type (api-docs, claude-code, github, etc.).
        kb_files: List of KB files mapped to this source.
        client: An anthropic.Anthropic client instance.

    Returns:
        Dict with keys: category, reasoning, affected_files.
        Falls back to MEDIUM with an explanation if classification fails.
    """
    if client is None:
        return _fallback_result("No API client provided")

    if not change_summary or not change_summary.strip():
        return _fallback_result("Empty change summary")

    kb_files_str = ", ".join(kb_files) if kb_files else "unknown"

    prompt = CLASSIFICATION_PROMPT.format(
        source_name=source_name,
        source_url=source_url,
        page_type=page_type,
        kb_files=kb_files_str,
        change_summary=_truncate_summary(change_summary),
    )

    try:
        response = client.messages.create(
            model=CLASSIFY_MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        result = _parse_classification(text, kb_files or [])
        logger.info(
            "Classified '%s' as %s: %s",
            source_name, result["category"], result["reasoning"][:80],
        )
        return result

    except Exception as e:
        logger.warning("Classification API call failed for '%s': %s", source_name, e)
        return _fallback_result(f"API error: {e}", kb_files)


def classify_report(report_path: Path, client=None) -> list[dict]:
    """Classify all changes found in a freshness report file.

    Parses the markdown report to extract change entries, then classifies each one.

    Args:
        report_path: Path to a freshness report markdown file.
        client: An anthropic.Anthropic client instance.

    Returns:
        List of classification dicts, one per detected change.
    """
    if not report_path.exists():
        logger.error("Report file not found: %s", report_path)
        return []

    report_text = report_path.read_text()
    changes = _extract_changes_from_report(report_text)

    if not changes:
        logger.info("No changes to classify in %s", report_path.name)
        return []

    logger.info("Classifying %d change(s) from %s", len(changes), report_path.name)

    results = []
    for change in changes:
        classification = classify_change(
            change_summary=change["diff"],
            source_name=change["name"],
            source_url=change.get("url", ""),
            page_type=change.get("page_type", ""),
            kb_files=change.get("kb_files", []),
            client=client,
        )
        classification["source_name"] = change["name"]
        classification["source_url"] = change.get("url", "")
        results.append(classification)

    return results


def classify_results(changed_results: list, client=None) -> list[dict]:
    """Classify a list of SourceResult objects directly (in-memory pipeline).

    This is the preferred integration point — called from freshness_check.py
    after the check completes, passing the list of changed SourceResult objects.

    Args:
        changed_results: List of SourceResult objects with status "changed" or "new".
        client: An anthropic.Anthropic client instance.

    Returns:
        List of classification dicts, one per changed result.
    """
    if not changed_results:
        logger.info("No changes to classify")
        return []

    logger.info("Classifying %d change(s)", len(changed_results))

    results = []
    for r in changed_results:
        # Build a change summary from the diff or content
        if r.previous_content and r.content:
            from .report import generate_diff
            summary = generate_diff(r.previous_content, r.content, r.source.name)
            if not summary:
                summary = f"New content ({len(r.content)} chars) for {r.source.name}"
        elif r.status == "new":
            summary = f"NEW SOURCE: First observation of {r.source.name}. Content length: {len(r.content)} chars.\n\nFirst 2000 chars:\n{r.content[:2000]}"
        else:
            summary = f"Change detected in {r.source.name} but no diff available."

        classification = classify_change(
            change_summary=summary,
            source_name=r.source.name,
            source_url=r.source.url,
            page_type=r.source.page_type,
            kb_files=r.source.kb_files,
            client=client,
        )
        classification["source_name"] = r.source.name
        classification["source_url"] = r.source.url
        results.append(classification)

    return results


# ── Internal helpers ─────────────────────────────────────────────────────────

def _truncate_summary(text: str, max_chars: int = 8000) -> str:
    """Truncate a change summary to stay within token budget."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n... (truncated, {len(text) - max_chars} chars omitted)"


def _parse_classification(text: str, default_kb_files: list[str]) -> dict:
    """Parse the JSON response from the classification model.

    Handles common issues: markdown fences, trailing commas, etc.
    """
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (possibly with language tag)
        first_newline = cleaned.index("\n")
        cleaned = cleaned[first_newline + 1:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse classification JSON: %s\nRaw: %s", e, text[:200])
        return _fallback_result(f"JSON parse error: {e}", default_kb_files)

    # Validate and normalize
    category = data.get("category", DEFAULT_CATEGORY).upper()
    if category not in CATEGORIES:
        logger.warning("Unknown category '%s', defaulting to %s", category, DEFAULT_CATEGORY)
        category = DEFAULT_CATEGORY

    reasoning = data.get("reasoning", "No reasoning provided")
    affected_files = data.get("affected_files", default_kb_files)

    # Ensure affected_files is a list of strings
    if not isinstance(affected_files, list):
        affected_files = [str(affected_files)]
    affected_files = [str(f) for f in affected_files]

    return {
        "category": category,
        "reasoning": reasoning,
        "affected_files": affected_files,
    }


def _fallback_result(reason: str, kb_files: list[str] | None = None) -> dict:
    """Return a default MEDIUM classification when the real one fails."""
    return {
        "category": DEFAULT_CATEGORY,
        "reasoning": f"Fallback classification ({reason})",
        "affected_files": kb_files or [],
    }


def _extract_changes_from_report(report_text: str) -> list[dict]:
    """Extract individual change entries from a freshness report markdown file.

    Parses the '## Changes' section to find each '### SourceName' block,
    extracting the name, URL, KB files, and diff content.
    """
    changes = []

    # Split into sections at ### headings within the Changes section
    in_changes = False
    current_change = None

    for line in report_text.splitlines():
        if line.startswith("## Changes"):
            in_changes = True
            continue
        if line.startswith("## ") and in_changes:
            # Hit the next top-level section, stop
            break

        if not in_changes:
            continue

        if line.startswith("### "):
            # Save previous change if exists
            if current_change and current_change.get("diff"):
                changes.append(current_change)

            name = line[4:].strip()
            # Strip priority tags like [HIGH]
            if name.endswith("]"):
                bracket_start = name.rfind("[")
                if bracket_start > 0:
                    name = name[:bracket_start].strip()

            current_change = {"name": name, "url": "", "kb_files": [], "diff": ""}
            continue

        if current_change is None:
            continue

        # Parse metadata lines
        if line.startswith("- **URL:**"):
            current_change["url"] = line.split("**URL:**")[-1].strip()
        elif line.startswith("- **KB files:**"):
            kb_str = line.split("**KB files:**")[-1].strip()
            current_change["kb_files"] = [f.strip() for f in kb_str.split(",")]
        elif line.startswith("```diff"):
            current_change["_in_diff"] = True
        elif line.startswith("```") and current_change.get("_in_diff"):
            current_change.pop("_in_diff", None)
        elif current_change.get("_in_diff"):
            current_change["diff"] += line + "\n"

    # Don't forget the last change
    if current_change and current_change.get("diff"):
        changes.append(current_change)

    # Clean up internal flags
    for c in changes:
        c.pop("_in_diff", None)

    return changes


def get_api_client():
    """Create an Anthropic API client using environment variable.

    Returns None if the API key is not available.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set — cannot classify changes")
        return None

    try:
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        logger.error("anthropic package not installed — run: pip install anthropic")
        return None
