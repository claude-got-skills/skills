<\!-- Source: https://code.claude.com/docs/en/code-review | Scraped: 2026-03-13 -->

# Code Review

**Status:** Research preview (Teams and Enterprise only, not available with ZDR)

Code Review analyzes GitHub pull requests and posts findings as inline comments. A fleet of specialized agents examine code changes in the context of the full codebase, looking for logic errors, security vulnerabilities, broken edge cases, and subtle regressions.

Findings are tagged by severity and don't approve or block PRs — existing review workflows stay intact.

## How Reviews Work

Reviews trigger when a PR opens, on every push, or when manually requested (`@claude review`). Multiple agents analyze the diff and surrounding code in parallel on Anthropic infrastructure. Each agent looks for a different class of issue, then a verification step checks candidates against actual code behavior to filter out false positives. Results are deduplicated, ranked by severity, and posted as inline comments.

Reviews scale in cost with PR size and complexity, completing in 20 minutes on average.

## Severity Levels

| Marker | Severity | Meaning |
|--------|----------|---------|
| Red | Normal | A bug that should be fixed before merging |
| Yellow | Nit | A minor issue, worth fixing but not blocking |
| Purple | Pre-existing | A bug in the codebase not introduced by this PR |

Findings include collapsible extended reasoning sections.

## What Code Review Checks

By default focuses on correctness: bugs that would break production, not formatting preferences or missing test coverage. Expandable via CLAUDE.md and REVIEW.md.

## Setup

1. Open claude.ai/admin-settings/claude-code (admin access required)
2. Install the Claude GitHub App (Contents: read/write, Issues: read/write, Pull requests: read/write)
3. Select repositories to enable
4. Set review triggers per repo:
   - **Once after PR creation**: review runs once when PR opens
   - **After every push**: review runs on each push (highest cost)
   - **Manual**: reviews only when `@claude review` commented (subsequent pushes then auto-reviewed)

## Manually Trigger Reviews

Comment `@claude review` on a PR (top-level comment, not inline). Must have owner/member/collaborator access. PR must be open and not draft.

## Customize Reviews

### CLAUDE.md
Code Review reads CLAUDE.md files and treats newly-introduced violations as nit-level findings. Works bidirectionally — if PR makes CLAUDE.md outdated, Claude flags that too. Reads at every directory level.

### REVIEW.md
Review-only guidance at repo root. Encode:
- Style guidelines
- Language/framework conventions
- Things to always flag (e.g., "new API routes must have integration tests")
- Things to skip (e.g., "don't comment on generated code under /gen/")

Auto-discovered at repository root, no configuration needed.

## View Usage

Analytics at claude.ai/analytics/code-review:
- PRs reviewed (daily count)
- Cost weekly
- Feedback (auto-resolved comments)
- Repository breakdown

## Pricing

Billed based on token usage. **Reviews average $15-25**, scaling with PR size, codebase complexity, and verification needs. Billed separately through extra usage — does not count against plan's included usage.

Cost factors:
- "Once after PR creation" = 1 review per PR
- "After every push" = multiplied by number of pushes
- "Manual" = no cost until `@claude review` commented

Spend cap: claude.ai/admin-settings/usage -> Claude Code Review service limit.

## Related

- Plugin marketplace has a `code-review` plugin for local on-demand reviews before pushing
- GitHub Actions / GitLab CI/CD for self-hosted Claude integration
