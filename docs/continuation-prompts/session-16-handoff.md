# Session 16 Handoff: v2.4.0 Release, Browser Eval, and Maintenance Strategy

## Project Context

We are building and maintaining Claude skills under the **claude-got-skills** GitHub account. The primary skill — **Claude Capabilities Awareness** — gives Claude comprehensive, accurate knowledge about its capabilities across all platforms (Claude.ai, Desktop, Claude Code, CoWork, API).

**GitHub repo**: https://github.com/claude-got-skills/skills
**Private dev repo**: https://github.com/liam-jons/skills-dev
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.
**skills.sh listing**: https://skills.sh/claude-got-skills/skills/assistant-capabilities

---

## Session 15 Completed Work

### 1. Major Content Update (Phase 1) ✅

Added coverage for 4 significant new features:
- **Code Review**: Managed PR review service ($15-25/review, Teams/Enterprise, REVIEW.md customization)
- **Remote Control**: Continue local sessions from phone/browser via `claude remote-control` or `/rc`
- **Claude Code on the Web**: Cloud sessions at claude.ai/code, `--remote` flag, `/teleport` back to terminal
- **Slack Integration**: @Claude in channels auto-creates Claude Code web sessions

**9 new KB files created** (37 total):
- `claude-code-capabilities-code-review.md`
- `claude-code-capabilities-remote-control.md`
- `claude-code-capabilities-slack.md`
- `claude-code-capabilities-web-sessions.md`
- `claude-code-capabilities-desktop.md`
- `claude-code-capabilities-jetbrains.md`
- `claude-code-capabilities-vscode.md`
- `claude-code-capabilities-ci-cd.md`
- `claude-capabilities-pricing.md`

**Updated skill files:**
- `SKILL.md` (280 lines) — platform table expanded, Claude Code section updated
- `data/quick-reference.md` (100 lines) — 4 new capability lines, 4 platform rows
- `references/claude-code-specifics.md` (663 lines) — 4 new sections (Code Review, Remote Control, Web Sessions, Slack) + expanded IDE section
- `references/model-specifics.md` (317 lines) — training data cutoff dates added
- `references/api-features.md` — timestamp updated

**Pipeline config updated**: 23 monitored sources (was 12), added code-review, remote-control, slack, desktop, desktop-quickstart, claude-code-on-the-web, jetbrains, vs-code, github-actions, gitlab-ci-cd, pricing.

### 2. Sprint 2 — Classification Pipeline (Phase 2) ✅

Built and verified:
- **`pipeline/classify.py`** — Haiku-based change classification (CRITICAL/HIGH/MEDIUM/LOW) with JSON parsing, fallback handling, and both in-memory and report-file entry points
- **`pipeline/freshness_check.py`** — added `--classify` flag, integrates with classify_results()
- **`pipeline/report.py`** — generates classified reports grouped by actionability

Verification: PASS (1 minor dead code issue on line 224 — fixed).

### 3. Eval Suite Expansion (Phase 3) ✅

**55 → 65 tests across 10 categories** (was 9):
- Fixed 9 outdated questions with new keywords (Chrome, Remote Control, web sessions, Agent Skills, CoWork, Haiku 3 retirement)
- Added 10 new tests: Code Review (Q2.6), Remote Control (Q2.7), cloud sessions (Q3.9), Slack (Q5.9), Remote vs Web (Q8.11), IDE parity (Q8.12), and 4 **Competitor Migration** tests (Q10.1-10.4)
- Updated 9 existing rubrics + added 10 new rubrics (65/65 coverage)
- All rubrics sourced from KB docs, not SKILL.md

Verification: PASS (thorough — all 65 IDs checked, KB cross-referenced for new rubrics).

### 4. Judge Prefill Fix ✅

Sonnet 4.6 and Opus 4.6 reject assistant message prefill with 400 error. Removed prefill from `judge_score()` in eval_runner.py. JSON extraction already handles responses without leading `{` via regex fallback.

### 5. Browser Eval DOM Selector Fix ✅

Live Playwright inspection of Claude.ai revealed:
- **Input field**: `textbox "Write your prompt to Claude"` — Playwright uses `getByTestId('chat-input')` internally
- **Completion**: "Stop response" button disappears when generation finishes
- **Response**: text in `paragraph` elements within generic containers

Updated `browser_eval.sh` with layered input discovery (4 strategies) and "Stop response" button disappearance as primary completion signal.

### 6. Key Discovery: Anthropic's product-self-knowledge Skill

Claude.ai's "Consulted product knowledge" is actually **our skill auto-invoking**, not a competing Anthropic skill. However, Claude Desktop has a separate Anthropic-built `product-self-knowledge` skill that:
- Is a **routing skill** — contains almost no product facts
- Tells Claude to web_fetch live docs rather than trusting training data
- Covers basic product info via live fetch, but no architecture patterns or decision frameworks
- **Not available in Claude Code** — only Claude Desktop and Claude.ai

**Our skill is complementary, not competing.** It provides curated knowledge, architecture patterns, and decision frameworks that no live fetch can replicate. See `memory/reference_product_self_knowledge.md` for full analysis.

### 7. Manifests Updated to v2.4.0 ✅

- `.claude-plugin/plugin.json` → v2.4.0
- `.claude-plugin/marketplace.json` → v2.4.0, updated skill description
- Skill ZIP at `evals/assistant-capabilities-v2.4.0.zip` (not needed for Claude.ai — skill already installed)

### 8. API Eval Results (Haiku + Sonnet Judge, 65 Tests) ✅

| Category | Ctrl Acc → Trt Acc (Lift) | Ctrl Comp → Trt Comp (Lift) |
|----------|--------------------------|----------------------------|
| Architecture | 1.33 → 3.33 (+150%) | 2.00 → 2.33 (+17%) |
| Can Claude Do X | 2.14 → 4.00 (+87%) | 1.00 → 2.14 (+114%) |
| **Competitor Migration** | 1.25 → 3.25 (+160%) | 1.25 → 3.50 (+180%) |
| Conversational | 2.75 → 3.58 (+30%) | 1.25 → 2.42 (+94%) |
| Cross-Platform | 2.08 → 4.00 (+92%) | 1.25 → 3.08 (+146%) |
| Extension | 1.78 → 4.22 (+137%) | 1.56 → 2.78 (+78%) |
| Hallucination | 1.60 → 2.80 (+75%) | 1.20 → 2.60 (+117%) |
| Implementation | 2.44 → 4.33 (+77%) | 1.11 → 2.67 (+140%) |
| Model Selection | 1.00 → 4.00 (+300%) | 2.00 → 5.00 (+150%) |
| Negative | 5.00 → 5.00 (0%) | 4.00 → 4.00 (0%) |

Report: `evals/eval-report-20260313-174102.md`

---

## Current Git State

```
Branch: dev (8 commits ahead of main)
Tag: v2.3.0 on main

Commits on dev not on main:
27550f0 Fix browser eval DOM selectors for current Claude.ai
65d5a2a Fix judge prefill error on Sonnet 4.6 models
7ed2633 Expand eval suite to 65 tests with Competitor Migration category
348268a Add Code Review, Remote Control, web sessions, Slack integration coverage
28e4f34 Add codebase-review plugin — full codebase quality review with parallel agents
7e09da9 Add session 14 docs, eval audit, and agent outputs
9900c8d Add independent judge rubrics and browser eval improvements
b61041c Fix browser eval auth: use manual ENTER confirmation instead of URL detection

All pushed to both origin and dev remotes.

Uncommitted files on dev (need committing at start of session 16):
 M docs/eval-questions.md              — updated to 65 questions, 10 categories
?? evals/assistant-capabilities-v2.4.0.zip — skill ZIP for Claude.ai (if needed)
?? evals/eval-report-20260313-174102.md  — v2.4.0 Haiku eval report
?? evals/eval-results-20260313-174102.json — raw eval results (gitignored)
?? docs/continuation-prompts/session-16-handoff.md — this file

Pipeline files modified on disk (gitignored from origin, push to dev remote):
   pipeline/config.py         — 23 sources (11 new added this session)
   pipeline/classify.py       — Sprint 2 classification (NEW this session)
   pipeline/freshness_check.py — --classify flag added
   pipeline/report.py         — classified report generation added
```

---

## Session 16 Priority Order

### Priority 1: v2.4.0 Release (~15 min)

1. **Merge dev → main**: `git checkout main && git merge dev`
2. **Tag**: `git tag v2.4.0`
3. **Push**: `git push origin main --tags && git push dev main --tags`
4. **Verify install**: `npx skills add claude-got-skills/skills@assistant-capabilities` in clean environment

### Priority 2: Browser Eval Full Run (~1 hr)

The browser eval DOM selectors have been fixed based on live Playwright inspection. Run the full A/B test:

1. **Re-auth if needed**: `./evals/browser_eval.sh --auth` (auth state from 2026-03-10 may be expired — but Playwright session is currently authenticated, so save that state first)
2. **Control run**: Navigate to `claude.ai/customize/skills` → toggle `assistant-capabilities` OFF → run `./evals/browser_eval.sh --control --headed --yes`
3. **Treatment run**: Toggle skill back ON → run `./evals/browser_eval.sh --treatment --headed --yes`

**Key finding from session 15**: Skills management has moved from Settings > Capabilities to **claude.ai/customize/skills**. The skill toggle is there, not in the old location. No ZIP upload needed — skill is already installed.

**Browser eval approach**: The script uses `agent-browser` (not Playwright). If `agent-browser` snapshots differ from Playwright snapshots, the grep patterns may still fail. In that case, capture an `ab snapshot -i` output and compare with the Playwright snapshot to adjust patterns.

### Priority 3: Sprint 2 Pipeline Test (~30 min)

Run the classification pipeline with the `--classify` flag:
```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
python -m pipeline.freshness_check --classify
```
This requires `ANTHROPIC_API_KEY` in `.env` and must run outside sandbox (`dangerouslyDisableSandbox: true`).

### Priority 4: v2.5.0 Maintenance Strategy Planning (~1 hr)

Based on the product-self-knowledge analysis, plan a content split:

**Keep in skill (changes slowly, high advisory value):**
- Model names, IDs, and training cutoffs (solves the "model doesn't exist" problem)
- Architecture decision patterns
- Extension selection guidance ("when to use X vs Y")
- Feature combination patterns
- Breaking changes and migration guides
- Platform comparison table

**Move to "check live docs" pointer (changes fast, low advisory value):**
- Exact pricing per MTok
- Exact rate limits per tier
- Tier threshold details

**Explicitly decided to KEEP model IDs in skill:** Model IDs solve a bootstrapping problem — Claude can't web_fetch info about a model it doesn't know exists. Training cutoffs mean Haiku doesn't know about Opus/Sonnet 4.6 at all, and Opus 4.6 doesn't know about itself (training data predates its release). This was a specific user-driven decision based on real friction experienced in Claude Code sessions.

**Beta header strings:** Borderline — keep for now because wrong headers cause real API errors, similar to the model ID problem.

This reduces maintenance burden while preserving the skill's unique value over Anthropic's routing-based product-self-knowledge skill.

### Priority 5: Description Re-validation (~30 min)

Use skill-creator's `run_loop.py` for empirical trigger testing. The description needs updating to mention Code Review, Remote Control, web sessions, and Slack — these are new trigger signals. Don't manually edit — use the eval workflow.

### Priority 6: New Plugin Integration

A new plugin is being added to the repository by a concurrent session. When it's ready, integrate it:
- Add to `.claude-plugin/marketplace.json`
- Verify it doesn't conflict with existing plugin/hook configuration
- Test install path

### Priority 7: Commit Remaining Artifacts + Docs Push

Several files from session 15 are uncommitted. Handle in two commits:

**Commit A — eval artifacts (push to both remotes):**
```bash
git add evals/eval-report-20260313-174102.md evals/assistant-capabilities-v2.4.0.zip docs/eval-questions.md
git commit -m "Add v2.4.0 eval report, skill ZIP, and updated eval questions"
git push origin dev && git push dev dev
```

**Commit B — docs (push to dev remote only, NOT origin):**
```bash
git add -f docs/continuation-prompts/session-16-handoff.md
git commit -m "Add session 16 handoff"
git push dev dev  # dev remote only
```

**Pipeline files** are tracked on dev remote but gitignored from origin. They may need force-adding:
```bash
git add -f pipeline/classify.py pipeline/config.py pipeline/freshness_check.py pipeline/report.py
git commit -m "Sprint 2: add classification pipeline and new source URLs"
git push dev dev  # dev remote only
```

---

## Key Technical Context

### Environment
- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Sandbox**: Eval runner must run with `dangerouslyDisableSandbox: true`
- **Model IDs**: Only shorthands work for 4.6 (`claude-opus-4-6`, `claude-sonnet-4-6`). No dated variants.
- **Plugin installed locally** — SessionStart hook fires every session
- **Skill installed on Claude.ai** — at claude.ai/customize/skills, auto-invokes
- **Playwright session**: May still be authenticated from session 15 (accepted cookies, verified login code)

### Model Training Data Cutoffs
- Opus 4.6: Reliable May 2025, Training Aug 2025
- Sonnet 4.6: Reliable Aug 2025, Training Jan 2026
- Haiku 4.5: Reliable Feb 2025, Training Jul 2025

**Implication**: Haiku doesn't know Opus 4.6/Sonnet 4.6 exist. Opus 4.6 doesn't know about itself. This is WHY model IDs must stay in the skill — it's a bootstrapping problem that web fetch can't solve.

### Judge Configuration
- **Sonnet 4.6 as judge** — no prefill (removed in session 15), reliable JSON extraction
- **Haiku as judge** — high N/A rate due to JSON parse failures, not recommended
- Judge uses per-test rubrics from `evals/rubrics.py` (65 rubrics from KB docs), falls back to SKILL.md

### Browser Eval Key Info
- Skills page moved to `claude.ai/customize/skills` (not Settings > Capabilities)
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

### Pipeline
- 23 sources in `pipeline/config.py` (was 12)
- Sprint 1 (scrape + detect) + Sprint 2 (classify) complete
- `--classify` flag uses Haiku for actionability classification
- Pipeline directory is gitignored from origin, tracked on dev remote only
- Sprint 3 (auto-update KB) and Sprint 4 (propose SKILL.md edits) still TODO

### Key Files
```
pipeline/config.py                    — 23 source URLs
pipeline/classify.py                  — Sprint 2 classification (NEW)
pipeline/freshness_check.py           — --classify flag added
pipeline/report.py                    — classified report generation
data/quick-reference.md               — Tier 1 content (100 lines, v2.4.0)
skills/assistant-capabilities/SKILL.md — main skill (280 lines)
references/claude-code-specifics.md   — Code Review, RC, Web, Slack + existing
references/api-features.md            — API features
references/model-specifics.md         — model specs + training cutoffs
evals/eval_runner.py                  — 65 tests, 10 categories
evals/rubrics.py                      — 65 independent judge rubrics
evals/browser_eval.sh                 — DOM selectors fixed 2026-03-13
evals/assistant-capabilities-v2.4.0.zip — skill ZIP (not needed for Claude.ai)
docs/eval-questions.md                — all 65 questions for review
```
