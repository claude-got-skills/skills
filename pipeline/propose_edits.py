"""Propose skill/reference edits based on KB changes (Sprint 4).

After Sprint 3 updates knowledge-base files, this module generates edit proposals
for user-facing files (SKILL.md, references, quick-reference). Proposals are
human-reviewed markdown reports with unified diffs — never auto-applied.

Safety:
- Only READS target files (SKILL.md, references, quick-reference)
- Writes ONLY to pipeline/proposals/ directory
- All changes require human review before application
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    KB_TO_TARGETS,
    PROPOSALS_DIR,
    PROJECT_DIR,
    get_targets_for_kb,
)
from .update_kb import KBUpdateResult

logger = logging.getLogger(__name__)

# Model for generating edit proposals
PROPOSAL_MODEL = "claude-sonnet-4-6"

# Token budget limits for LLM input
MAX_DIFF_CHARS = 20_000
MAX_TARGET_CHARS = 30_000

PROPOSAL_PROMPT = """\
You are a technical editor maintaining a Claude capabilities skill. Your task is to \
propose specific edits to a user-facing file based on changes detected in the knowledge base.

## Maintenance Strategy (MUST follow)

Apply these rules to decide what to propose:

1. **KEEP in SKILL.md/quick-reference** if: load-bearing string (model ID, API header, \
tool type string), wrong value causes error (400, 404, silent failure), architectural \
guidance not in any single docs page, prevents common hallucination.
2. **POINTER only** if: number that changes independently (price, rate limit), version \
number with no functional implication.
3. **Reference files** should contain: detailed configurations, code examples, migration \
guides, compatibility matrices.
4. **Quick-reference** should only change when SKILL.md changes, and only for the most \
critical subset (model IDs, key parameters, breaking changes).

## Rules for proposals

- Propose ONLY changes justified by the KB diff. Do not rewrite or improve unrelated content.
- Preserve the target file's existing structure, formatting, and line count.
- For SKILL.md: only propose changes for load-bearing strings, error-preventing values, \
or new capabilities that need a summary line. Most KB updates should NOT require SKILL.md changes.
- For reference files: propose detailed updates reflecting the KB changes. If the target \
file already contains a concrete functional value (e.g., token limit, output cap, context \
window size) that has changed, update it — stale functional values cause errors. However, \
do NOT update pricing or rate limit numbers; these are POINTER-class and looked up from \
live documentation at query time.
- For quick-reference: only propose changes if a model ID, key parameter, or breaking \
change is affected.
- If the KB diff does not warrant any changes to this target file, respond with exactly: \
NO_CHANGES_NEEDED

## Output format

If changes are needed, respond with a structured proposal:

```
RATIONALE: <1-2 sentences explaining why this change is needed>

DIFF:
--- a/<target_file>
+++ b/<target_file>
@@ <section context> @@
-old line(s)
+new line(s)
```

You may include multiple DIFF blocks for changes in different sections of the same file. \
Each DIFF block should be a valid unified diff fragment.

If NO changes are needed for this target, respond with exactly: NO_CHANGES_NEEDED

## KB change diff

The following KB file was updated. Here is the diff showing what changed:

KB file: {kb_filename}
Source: {source_name} ({source_url})

```diff
{kb_diff}
```

## Current target file

File: {target_file}

```
{target_content}
```

Analyze the KB diff and propose edits to the target file following the maintenance strategy."""


@dataclass
class ProposalChange:
    """A single proposed change to a target file."""
    target_file: str
    rationale: str
    diff: str
    kb_sources: list[str] = field(default_factory=list)


@dataclass
class ProposalResult:
    """Result of generating proposals from a pipeline run."""
    timestamp: str
    changes: list[ProposalChange] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # targets with NO_CHANGES_NEEDED
    errors: list[str] = field(default_factory=list)
    proposal_path: str = ""


def propose_skill_edits(
    kb_update_results: list[KBUpdateResult],
    client,
) -> ProposalResult:
    """Generate edit proposals for user-facing files based on KB updates.

    Args:
        kb_update_results: Results from Sprint 3 KB auto-update.
            Only results with status "updated" or "created" are processed.
        client: An anthropic.Anthropic client instance.

    Returns:
        ProposalResult with all proposed changes.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    result = ProposalResult(timestamp=timestamp)

    if client is None:
        logger.error("No API client — cannot generate proposals")
        result.errors.append("No API client provided")
        return result

    # Filter for KB files that were actually updated
    actionable = [
        r for r in kb_update_results
        if r.status in ("updated", "created") and r.diff
    ]

    if not actionable:
        logger.info("No KB updates to generate proposals for")
        return result

    logger.info("Generating proposals for %d KB update(s)", len(actionable))

    # Aggregate by target file: group all KB diffs that affect the same target
    target_to_kb = _aggregate_by_target(actionable)

    if not target_to_kb:
        logger.info("No target files mapped for updated KB files")
        return result

    logger.info(
        "Proposing edits for %d target file(s) from %d KB update(s)",
        len(target_to_kb), len(actionable),
    )

    # Generate one proposal per target file
    for target_file, kb_items in target_to_kb.items():
        try:
            change = _generate_proposal(target_file, kb_items, client)
            if change is None:
                result.skipped.append(target_file)
                logger.info("  %s — no changes needed", target_file)
            else:
                result.changes.append(change)
                logger.info("  %s — proposal generated", target_file)
        except Exception as e:
            error_msg = f"Error generating proposal for {target_file}: {e}"
            result.errors.append(error_msg)
            logger.error("  %s", error_msg)

    # Save proposal report
    if result.changes:
        result.proposal_path = _save_proposal(result)
        logger.info(
            "Proposal saved: %s (%d changes, %d skipped)",
            result.proposal_path, len(result.changes), len(result.skipped),
        )

    return result


def _aggregate_by_target(
    kb_results: list[KBUpdateResult],
) -> dict[str, list[KBUpdateResult]]:
    """Group KB update results by their target files.

    When multiple KB files map to the same target, they are aggregated
    so a single coherent proposal is generated per target.
    """
    target_to_kb: dict[str, list[KBUpdateResult]] = {}

    for kb_result in kb_results:
        targets = get_targets_for_kb(kb_result.kb_filename)
        if not targets:
            logger.debug(
                "No target mapping for KB file: %s", kb_result.kb_filename,
            )
            continue

        for target in targets:
            if target not in target_to_kb:
                target_to_kb[target] = []
            target_to_kb[target].append(kb_result)

    return target_to_kb


def _generate_proposal(
    target_file: str,
    kb_items: list[KBUpdateResult],
    client,
) -> ProposalChange | None:
    """Generate a proposal for a single target file.

    Args:
        target_file: Relative path to the target file (from PROJECT_DIR).
        kb_items: List of KB updates that affect this target.
        client: Anthropic API client.

    Returns:
        ProposalChange if changes are proposed, None if NO_CHANGES_NEEDED.
    """
    # Read current target file
    target_path = PROJECT_DIR / target_file
    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")

    target_content = target_path.read_text(encoding="utf-8")
    if len(target_content) > MAX_TARGET_CHARS:
        target_content = (
            target_content[:MAX_TARGET_CHARS]
            + f"\n\n... (truncated, {len(target_content) - MAX_TARGET_CHARS:,} chars omitted)"
        )

    # Combine all KB diffs for this target
    combined_diff = ""
    kb_sources = []
    for kb_item in kb_items:
        kb_sources.append(f"{kb_item.kb_filename} (from {kb_item.source_name})")
        diff_text = kb_item.diff
        if len(diff_text) > MAX_DIFF_CHARS // len(kb_items):
            diff_text = diff_text[:MAX_DIFF_CHARS // len(kb_items)] + "\n... (truncated)"
        combined_diff += f"\n### {kb_item.kb_filename}\n{diff_text}\n"

    # Use first KB item for source info (or combine if multiple)
    source_names = ", ".join(item.source_name for item in kb_items)
    source_urls = ", ".join(item.source_url for item in kb_items)
    kb_filenames = ", ".join(item.kb_filename for item in kb_items)

    prompt = PROPOSAL_PROMPT.format(
        kb_filename=kb_filenames,
        source_name=source_names,
        source_url=source_urls,
        kb_diff=combined_diff,
        target_file=target_file,
        target_content=target_content,
    )

    response = client.messages.create(
        model=PROPOSAL_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    # Check for NO_CHANGES_NEEDED response
    if "NO_CHANGES_NEEDED" in text:
        return None

    # Parse the proposal response
    rationale, diff = _parse_proposal_response(text)

    return ProposalChange(
        target_file=target_file,
        rationale=rationale,
        diff=diff,
        kb_sources=kb_sources,
    )


def _parse_proposal_response(text: str) -> tuple[str, str]:
    """Parse the LLM proposal response into rationale and diff.

    Returns (rationale, diff) tuple.
    """
    rationale = ""
    diff = ""

    lines = text.splitlines()
    in_rationale = False
    in_diff = False
    diff_lines = []
    rationale_lines = []

    for line in lines:
        if line.startswith("RATIONALE:"):
            in_rationale = True
            in_diff = False
            rest = line[len("RATIONALE:"):].strip()
            if rest:
                rationale_lines.append(rest)
            continue
        if line.startswith("DIFF:"):
            in_rationale = False
            in_diff = True
            continue
        # Also detect bare diff markers without DIFF: header
        if line.startswith("--- a/") and not in_diff:
            in_rationale = False
            in_diff = True

        if in_rationale and not line.startswith("DIFF:"):
            rationale_lines.append(line)
        elif in_diff:
            # Strip wrapping code fences
            if line.strip() in ("```", "```diff"):
                continue
            diff_lines.append(line)

    rationale = " ".join(rationale_lines).strip()
    diff = "\n".join(diff_lines).strip()

    # Fallback: if parsing didn't find structured output, use the raw text
    if not rationale and not diff:
        rationale = "See raw proposal below"
        diff = text

    return rationale, diff


def _save_proposal(result: ProposalResult) -> str:
    """Save the proposal as a markdown report.

    Returns the path to the saved report.
    """
    lines = []
    lines.append(f"# Skill Edit Proposal — {result.timestamp}")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Changes proposed: {len(result.changes)}")
    lines.append(f"Targets skipped (no changes needed): {len(result.skipped)}")
    if result.errors:
        lines.append(f"Errors: {len(result.errors)}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    for i, change in enumerate(result.changes, 1):
        lines.append(f"{i}. **{change.target_file}** — {change.rationale[:100]}")
    if result.skipped:
        lines.append("")
        lines.append("**No changes needed:** " + ", ".join(
            f"`{s}`" for s in result.skipped
        ))
    lines.append("")

    # Detailed proposals
    lines.append("## Proposed Changes")
    lines.append("")

    for i, change in enumerate(result.changes, 1):
        lines.append(f"### {i}. {change.target_file}")
        lines.append("")
        lines.append(f"**Rationale:** {change.rationale}")
        lines.append("")
        if change.kb_sources:
            lines.append("**Triggered by KB updates:**")
            for src in change.kb_sources:
                lines.append(f"- {src}")
            lines.append("")
        lines.append("**Proposed diff:**")
        lines.append("")
        lines.append("```diff")
        lines.append(change.diff)
        lines.append("```")
        lines.append("")

    # Review checklist
    lines.append("## Review Checklist")
    lines.append("")
    lines.append("- [ ] All proposed changes verified against source documentation")
    lines.append("- [ ] Maintenance strategy filter applied correctly")
    lines.append("- [ ] No token budget increase in SKILL.md")
    lines.append("- [ ] Quick-reference stays under 100 lines")
    lines.append("- [ ] Changes are factually accurate")
    lines.append("")

    if result.errors:
        lines.append("## Errors")
        lines.append("")
        for err in result.errors:
            lines.append(f"- {err}")
        lines.append("")

    report_text = "\n".join(lines)
    report_path = PROPOSALS_DIR / f"proposal-{result.timestamp}.md"
    report_path.write_text(report_text, encoding="utf-8")

    return str(report_path)


def format_proposal_summary(result: ProposalResult) -> str:
    """Format a brief summary for logging/notification."""
    if not result.changes:
        return "No skill edit proposals generated."

    parts = [
        f"{len(result.changes)} proposal(s) generated",
    ]
    if result.skipped:
        parts.append(f"{len(result.skipped)} target(s) unchanged")
    if result.errors:
        parts.append(f"{len(result.errors)} error(s)")
    if result.proposal_path:
        parts.append(f"report: {result.proposal_path}")

    return "Skill edit proposals: " + " | ".join(parts)
