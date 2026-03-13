# Session 17 Handoff: Production Readiness, Browser Eval, and Pipeline Maturation

## Project Context

We are building and maintaining Claude skills under the **claude-got-skills** GitHub account. The primary skill — **Claude Capabilities Awareness** — gives Claude comprehensive, accurate knowledge about its capabilities across all platforms (Claude.ai, Desktop, Claude Code, CoWork, API).

**GitHub repo**: https://github.com/claude-got-skills/skills
**Private dev repo**: https://github.com/liam-jons/skills-dev
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.
**skills.sh listing**: https://skills.sh/claude-got-skills/skills/assistant-capabilities

---

## Session 16 Completed Work

### 1. v2.4.0 Release ✅

- Merged dev → main (fast-forward, 5 commits)
- Tagged v2.4.0, pushed to both origin and dev remotes
- Merged dev remote's unrelated history (3 earlier init commits from private repo setup)

### 2. Origin Cleanup ✅

Dev artifacts were inadvertently merged to origin/main via the unrelated history merge. Cleaned up:
- Removed 35 files from origin/main HEAD (docs/, evals/results/, evals/reports/, monitoring/)
- Preserved `docs/eval-questions.md` (useful for public reference)
- Files remain in git history and on dev remote

### 3. Sprint 2 Pipeline Verified ✅

Ran `python -m pipeline.freshness_check --classify` end-to-end:
- 23/23 sources scraped successfully, 0 errors
- 1 change detected: API Release Notes (classified as MEDIUM — documentation restructuring, no action needed)
- Haiku classification working correctly with proper JSON parsing and fallback handling
- Fixed `notify.py` hardcoded source count (was "All 13 sources unchanged", now dynamic)

### 4. v2.5.0 Maintenance Strategy ✅

Comprehensive content audit determined:
- **SKILL.md**: 100% KEEP — every section is load-bearing API strings, error prevention, or unique advisory content
- **quick-reference.md**: 100% KEEP — compressed version of SKILL.md
- **Only 2 sections moved to pointers:**
  1. `model-specifics.md` pricing table → tier ordering + link to docs.anthropic.com
  2. `api-features.md` rate limits → patterns + links to console and docs
- Pricing multipliers retained (batch 50%, caching 10%, 1M 2x, fast mode 6x) — stable architectural guidance
- Rate limit header names, retry behaviour, and key patterns retained
- Decision framework for future content: KEEP if load-bearing/error-preventing/anti-hallucination, POINTER if volatile numbers

### 5. v2.5.0 Released ✅

- Description updated (Candidate B): +Code Review, +Remote Control, +web/cloud sessions, +Slack, +CoWork, +plugins, +competitor migration triggers (Copilot, Cursor, ChatGPT, Windsurf)
- Description validation: 13 tests improved, 52 unchanged, 0 regressions, 0 false-positive risk
- Pricing table → pointer in model-specifics.md
- Rate limits → pointer in api-features.md
- Version bumped to 2.5.0 across plugin.json, marketplace.json, quick-reference.md
- Merged dev → main, tagged v2.5.0, pushed to both remotes

### 6. Description Audit ✅

Agent analysis of trigger signals against all 65 eval tests:
- Current description had zero explicit triggers for 5 new feature areas
- Candidate B adds all 5 while maintaining natural language flow (73 words)
- Coverage matrix verified: all 10 eval categories now have explicit trigger signals
- Candidate B adopted and shipped in v2.5.0

---

## Current Git State

```
Branch: dev (in sync with main)
Tags: v2.5.0 on main (latest), v2.4.0 (prior)

Both remotes fully up to date:
- origin (github.com/claude-got-skills/skills) — public
- dev (github.com/liam-jons/skills-dev) — private

Working tree: clean, nothing to commit

Key recent commits on main:
605d06d Merge dev: v2.5.0 maintenance strategy release
3bada23 v2.5.0: Replace volatile pricing/rate-limit data with live doc pointers
f5c3336 Remove dev artifacts from public repo
022f630 Add Sprint 2 classification pipeline, eval report, and session 16 handoff
b425a73 Merge remote-tracking branch 'dev/main'
cacf18b Add v2.4.0 skill ZIP and updated eval questions
27550f0 Fix browser eval DOM selectors for current Claude.ai
```

Note: `docs/` and `pipeline/` are in `.gitignore` for origin. They were force-added to dev in earlier sessions and cleaned from origin in session 16. New docs/pipeline files need `git add -f` and should go to dev remote only (NOT origin). Exception: `docs/eval-questions.md` is deliberately on origin.

---

## Session 17 Priority Order

### Priority 1: Browser Eval Full Run (~1 hr)

This is the **highest outstanding priority** — carried over from sessions 15 and 16. The DOM selectors were fixed in session 15 and the skill is installed on Claude.ai, but a full A/B browser eval has never been run successfully.

**Pre-flight:**
1. **Check auth**: `./evals/browser_eval.sh --auth` — auth state from 2026-03-10 is likely expired. Re-authenticate via Playwright browser.
2. **Verify skill toggle location**: Navigate to `claude.ai/customize/skills` — the skill toggle is here, NOT in Settings > Capabilities.

**Control run (skill OFF):**
1. Navigate to `claude.ai/customize/skills` → toggle `assistant-capabilities` OFF
2. Run: `./evals/browser_eval.sh --control --headed --yes`

**Treatment run (skill ON):**
1. Toggle skill back ON at `claude.ai/customize/skills`
2. Run: `./evals/browser_eval.sh --treatment --headed --yes`

**Key technical notes:**
- The script uses `agent-browser` (not Playwright directly). If `agent-browser` snapshot format differs from Playwright, grep patterns may fail.
- If patterns fail, capture `ab snapshot -i` output and compare with session 15's Playwright snapshot to adjust.
- Input field: `textbox "Write your prompt to Claude"` with `data-testid="chat-input"`
- Completion detection: "Stop response" button disappearance
- Response text: `paragraph` elements in generic containers

### Priority 2: API Eval Run with Sonnet Judge (~45 min)

The v2.4.0 eval was run with Haiku as judge (high N/A rate). Run a clean v2.5.0 eval with Sonnet 4.6 as judge for reliable scoring:

```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
python evals/eval_runner.py --judge-model claude-sonnet-4-6 --runs 1
```

This must run with `dangerouslyDisableSandbox: true` (proxy env vars block API calls in sandbox).

Compare results against the v2.4.0 baseline (in `evals/eval-report-20260313-174102.md`). The v2.5.0 changes were to reference files only (pricing/rate-limits pointers), so scores should be stable or improved (less stale content risk).

### Priority 3: Production Readiness Checklist

Before considering this "production ready", verify:

1. **Install path works**: `npx skills add claude-got-skills/skills@assistant-capabilities` in a clean environment
2. **Plugin install works**: `/plugin marketplace add claude-got-skills/skills` → `/plugin install claude-got-skills@claude-got-skills`
3. **Skill auto-invokes on Claude.ai**: Ask a capability question, confirm "Consulted product knowledge" appears
4. **No stale content in skill files**: Spot-check 5 key facts against live docs:
   - Opus 4.6 model ID: `claude-opus-4-6` → verify at platform.claude.com/docs
   - 1M context beta header: `context-1m-2025-08-07` → verify current
   - Structured outputs GA (no beta header) → verify
   - Code Review pricing ($15-25/review) → verify at code.claude.com/docs
   - Remote Control command (`claude remote-control`) → verify
5. **Pricing pointer URLs resolve**: Check that docs.anthropic.com/en/docs/about-claude/models/all-models returns a real page
6. **Rate limit pointer URLs resolve**: Check console.anthropic.com and docs.anthropic.com/en/docs/about-claude/models/rate-limits

### Priority 4: New Plugin Integration

A concurrent session is adding a new plugin to the repository. When ready:
- Check if it's been committed to dev or a feature branch
- Add to `.claude-plugin/marketplace.json` if not already there
- Verify it doesn't conflict with existing plugin/hook configuration (especially the SessionStart hook)
- Test install path
- Bump marketplace.json if needed

### Priority 5: Freshness Pipeline — Sprint 3 Implementation (~2 hrs)

Sprint 1 (scrape + detect) and Sprint 2 (classify) are complete and verified. Sprint 3 is a **must-build** — Anthropic's docs change frequently and the KB falls behind fast without automation.

**Goal**: Auto-update KB files when classified changes are detected.

**Implementation approach:**
1. When a CRITICAL or HIGH change is detected, automatically update the corresponding KB file(s) using the `kb_files` mapping in `config.py`
2. Use Claude (Haiku or Sonnet) to intelligently merge detected changes into existing KB markdown — not a naive overwrite, but a structured update that preserves KB formatting and adds/modifies only the changed sections
3. Generate a diff of what changed in the KB for human review
4. Commit KB updates automatically (on dev branch) with descriptive messages linking back to the source URL and classification
5. Don't auto-update SKILL.md or references — that's Sprint 4 (human review gate)

**Key design decisions needed:**
- How to handle NEW sources that don't have existing KB files (create from template vs scrape-and-summarize)
- Whether MEDIUM changes should also trigger KB updates or just be logged
- Rate limiting: if many sources change simultaneously (e.g., after a major Anthropic release), batch the LLM calls
- Rollback strategy: if an auto-update introduces errors, how to revert

### Priority 6: Description Trigger Eval Runner (Optional)

The description validation agent noted there's no automated runner for testing description trigger effectiveness. An `eval-set-description-triggers.json` with 20 test cases exists but has no runner. Building one would enable:
- Empirical A/B testing of description changes
- Regression testing before releasing new descriptions
- Integration with the skill-creator workflow

This is low priority but would strengthen the eval infrastructure.

---

## Key Technical Context

### Environment
- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Sandbox**: Eval runner and pipeline must run with `dangerouslyDisableSandbox: true`
- **Model IDs**: Only shorthands work for 4.6 (`claude-opus-4-6`, `claude-sonnet-4-6`). No dated variants.
- **Plugin installed locally** — SessionStart hook fires every session in this workspace
- **Skill installed on Claude.ai** — at claude.ai/customize/skills, auto-invokes
- **Playwright auth**: Likely expired (last auth 2026-03-10). Re-auth with `./evals/browser_eval.sh --auth`

### Model Training Data Cutoffs
- Opus 4.6: Reliable May 2025, Training Aug 2025
- Sonnet 4.6: Reliable Aug 2025, Training Jan 2026
- Haiku 4.5: Reliable Feb 2025, Training Jul 2025

**Implication**: Haiku doesn't know Opus 4.6/Sonnet 4.6 exist. Opus 4.6 doesn't know about itself. This is WHY model IDs must stay in the skill — bootstrapping problem that web fetch can't solve.

### Judge Configuration
- **Sonnet 4.6 as judge** — no prefill (removed in session 15), reliable JSON extraction
- **Haiku as judge** — high N/A rate due to JSON parse failures, not recommended
- Judge uses per-test rubrics from `evals/rubrics.py` (65 rubrics from KB docs), falls back to SKILL.md

### Browser Eval Key Info
- Skills page: `claude.ai/customize/skills` (not Settings > Capabilities)
- Input field: `textbox "Write your prompt to Claude"` with `data-testid="chat-input"`
- Completion detection: "Stop response" button disappearance
- Response text: `paragraph` elements in generic containers
- `agent-browser` and Playwright snapshots may differ in format — if grep patterns fail, capture `ab snapshot -i` and compare

### Anthropic's product-self-knowledge Skill
- **Routing skill** — tells Claude to web_fetch live docs, contains almost no facts
- Available on Claude Desktop and Claude.ai, NOT Claude Code
- Complementary to our skill, not competing
- Our advantage: curated knowledge, architecture patterns, decision frameworks
- Their advantage: always current (defers to live source)
- See `memory/reference_product_self_knowledge.md` for full analysis

### Maintenance Strategy (v2.5.0 Decision Framework)
When adding new content to the skill, apply this test:
1. Load-bearing string (model ID, header, tool type)? → KEEP (bootstrapping)
2. Wrong value causes error (400, 404, silent failure)? → KEEP (error prevention)
3. Architectural guidance not in any single docs page? → KEEP (unique advisory)
4. Prevents common hallucination? → KEEP (anti-hallucination)
5. Number that changes independently of features? → POINTER (price, rate limit)
6. Version number with no functional implication? → POINTER or omit

### Pipeline
- 23 sources in `pipeline/config.py`
- Sprint 1 (scrape + detect) + Sprint 2 (classify) complete and verified
- `--classify` flag uses Haiku for actionability classification
- Pipeline directory is gitignored from origin, tracked on dev remote
- Sprint 3 (auto-update KB) is a **must-build** — Anthropic docs change frequently, KB falls behind fast
- Sprint 4 (propose SKILL.md edits) still TODO
- Last run (2026-03-13): 1 MEDIUM change (API Release Notes restructuring)

### Key Files
```
pipeline/config.py                    — 23 source URLs
pipeline/classify.py                  — Sprint 2 classification
pipeline/freshness_check.py           — main pipeline entry point, --classify flag
pipeline/report.py                    — classified report generation
pipeline/notify.py                    — macOS notifications (source count fixed)
data/quick-reference.md               — Tier 1 content (100 lines, v2.5.0)
skills/assistant-capabilities/SKILL.md — main skill (280 lines, v2.5.0)
references/claude-code-specifics.md   — Code Review, RC, Web, Slack + existing
references/api-features.md            — API features (rate limits now pointer)
references/model-specifics.md         — model specs (pricing now pointer)
evals/eval_runner.py                  — 65 tests, 10 categories
evals/rubrics.py                      — 65 independent judge rubrics
evals/browser_eval.sh                 — DOM selectors fixed 2026-03-13
evals/eval-report-20260313-174102.md  — v2.4.0 baseline (Haiku judge)
docs/eval-questions.md                — all 65 questions for review
.claude-plugin/marketplace.json       — v2.5.0, 2 plugins + 1 skill
.claude-plugin/plugin.json            — v2.5.0
```

### Git Remotes and Push Rules

| Remote | URL | What to push |
|--------|-----|--------------|
| `origin` | `github.com/claude-got-skills/skills` | **Public repo** — code, evals, skill content, plugin files. No design docs, continuation prompts, or agent outputs. |
| `dev` | `github.com/liam-jons/skills-dev` | **Private repo** — everything from origin PLUS `docs/` (continuation prompts, agent outputs, eval audits, design docs). |

When committing:
1. **Code/eval changes** → normal `git add` + `git commit` → `git push origin dev` + `git push dev dev`
2. **Docs/research/handoffs** → `git add -f docs/...` → separate commit → `git push dev dev` only (do NOT push to origin)
3. **Pipeline files** → `git add -f pipeline/...` → same as docs (dev remote only)

Note: The origin cleanup in session 16 removed docs/pipeline files from origin/main. Do not re-add them to origin.
