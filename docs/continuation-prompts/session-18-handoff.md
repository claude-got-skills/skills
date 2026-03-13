# Session 18 Handoff: Sonnet Eval, Sprint 3 Verification, and Browser Eval Refinement

## Project Context

We are building and maintaining Claude skills under the **claude-got-skills** GitHub account. The primary skill — **Claude Capabilities Awareness** — gives Claude comprehensive, accurate knowledge about its capabilities across all platforms (Claude.ai, Desktop, Claude Code, CoWork, API).

**GitHub repo**: https://github.com/claude-got-skills/skills
**Private dev repo**: https://github.com/liam-jons/skills-dev
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.
**skills.sh listing**: https://skills.sh/claude-got-skills/skills/assistant-capabilities

---

## Session 17 Completed Work

### 1. API Eval v2.5.0 Baseline (Sonnet Judge) ✅

Ran full 65-test eval with `claude-sonnet-4-6` as judge, `claude-haiku-4-5-20251001` as test model:

| Category | Ctrl Accuracy | Trt Accuracy | Ctrl Completeness | Trt Completeness |
|----------|:---:|:---:|:---:|:---:|
| Architecture Decisions | 1.33 | 4.67 | 0.33 | 3.00 |
| Can Claude Do X | 2.00 | 4.14 | 0.71 | 2.43 |
| Competitor Migration | 2.25 | 3.50 | 1.75 | 3.50 |
| Conversational Platform | 2.33 | 3.83 | 1.42 | 2.42 |
| Cross-Platform Awareness | 1.83 | 4.08 | 1.42 | 2.83 |
| Extension Awareness | 1.89 | 4.11 | 1.56 | 2.44 |
| Hallucination Detection | 1.60 | 2.80 | 1.60 | 2.60 |
| Implementation Guidance | 2.56 | 4.33 | 1.22 | 2.44 |
| Model Selection | 1.00 | 4.00 | 2.00 | 4.00 |
| Negative (No Change) | 5.00 | 5.00 | 3.67 | 4.67 |

- Treatment wins all 10 categories. Negative tests hold steady (5/5).
- Zero N/A results from Sonnet judge (vs high N/A with Haiku judge).
- Report: `evals/eval-report-20260313-201051.md`
- Token usage: Control 32,797 | Treatment 340,897 | Overhead 308,100

### 2. Browser Eval — First Successful A/B Run ✅

- **5/5 control** (skill OFF), **5/5 treatment** (skill ON) on Claude.ai
- Three bugs fixed in `browser_eval.sh`:
  1. **Ref format**: agent-browser snapshot changed from `@eN` to `[ref=eN]` — updated 6 grep patterns
  2. **networkidle hang**: Claude.ai WebSockets prevent networkidle from resolving (~2.5 min/prompt) — replaced with 5s sleep
  3. **Stale daemon**: agent-browser daemon persists across script runs, ignoring `--state` flag — added double-close pre-cleanup, moved `--executable-path/--args` to daemon start only, simplified `ab()` wrapper
- **Key finding**: `fill` command takes ~2.5 min per prompt (character-by-character typing of long prompts)
- **Key finding**: agent-browser commands hang when run via background tasks (stdin/tty issue) — must run in foreground
- **Thinking panel extraction returns empty** — Claude.ai DOM changed, thinking panel selectors no longer match
- **Skill invocation evidence**: Treatment P4 contains `context: fork`, `userInvoked`, `CLAUDE_SKILL_DIR` — content only present in the skill, absent from control
- Report: `evals/browser-eval-report-20260313-210609.md`

### 3. Production Readiness — URL Checks ✅

Found and fixed 3 broken pointer URLs in skill references:
- `docs.anthropic.com/.../rate-limits` → **404** — fixed to `platform.claude.com/docs/en/api/rate-limits`
- `console.anthropic.com` → login wall — fixed to `platform.claude.com`
- `docs.anthropic.com/.../all-models` → 301 redirect — fixed to `platform.claude.com/docs/en/about-claude/models/all-models`
- Verified: `platform.claude.com/.../pricing`, `code.claude.com/.../code-review`, `code.claude.com/.../remote-control` all 200 OK

### 4. Sprint 3 Pipeline — KB Auto-Update ✅

Created `pipeline/update_kb.py` (555 lines):
- `update_kb_files()` — main entry point, filters CRITICAL/HIGH, calls Sonnet 4.6 for intelligent merge
- Safety: only touches `knowledge-base/` files, never SKILL.md or references (Sprint 4 gate)
- Merge via LLM: preserves KB structure, updates changed sections, adds new features, marks deprecated
- Diff generation for human review, truncation for token budget, 50-char sanity check on output
- Integrated `--update-kb` flag in `freshness_check.py` (requires `--classify`)
- **NOT YET TESTED END-TO-END** — this is session 18's top priority

### 5. Codebase-Review Plugin v1.2.0 ✅

- Confirmed merged to main by concurrent session (commit `f8e4fb0`)
- marketplace.json version bumped from 1.0.0 to 1.2.0
- New: pattern-checker agent, `--thorough` mode, `--verify-all`, delta analysis, findings.json

---

## Current Git State

```
Branch: dev
Tags: v2.5.0 on main (latest)

main at: f8e4fb0 (codebase-review v1.2.0)
dev at:  26a27d1 (Sprint 3 pipeline) — 3 commits ahead of main

origin (public):  pushed up to b25f7d4 (URL fixes) — Sprint 3 NOT on origin
dev (private):    pushed up to 26a27d1 (Sprint 3 included)

Recent commits on dev:
26a27d1 Sprint 3: auto-update KB files from detected documentation changes
b25f7d4 Fix broken pointer URLs and bump codebase-review version
e2d647f Fix browser eval: ref format, networkidle hang, stale daemon
f8e4fb0 codebase-review v1.2.0: implement all 17 improvements (P1-P4)
f60f571 Add session 17 handoff: production readiness, browser eval, pipeline maturation
605d06d Merge dev: v2.5.0 maintenance strategy release
```

Note: `docs/` and `pipeline/` are in `.gitignore` for origin. Pipeline files are force-added (`git add -f`) and go to dev remote only. Do NOT push pipeline/docs commits to origin.

---

## Session 18 Priority Order

### Priority 1: Sonnet 4.6 API Eval (~45 min)

The v2.5.0 eval ran Haiku as the test model. **Most users interact with Sonnet 4.6 or Opus 4.6**, not Haiku. We need to know the skill's value when the model already has more current training data.

**Why this matters**: Sonnet 4.6's training data extends to Jan 2026 — it likely knows many features the skill teaches. The delta between control and treatment will be smaller, but the remaining delta is what justifies the skill's existence for the majority of users. If the skill still lifts scores on Sonnet, that's a strong validation signal. If it doesn't, we need to understand which categories lose value and potentially refocus the skill content.

```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
python evals/eval_runner.py --model claude-sonnet-4-6 --judge-model claude-sonnet-4-6 --runs 1
```

Must run with `dangerouslyDisableSandbox: true`.

**Compare against Haiku baseline** (`evals/eval-report-20260313-201051.md`):
- Which categories still show treatment lift on Sonnet?
- Which categories show diminished lift (Sonnet already knows this)?
- Are there categories where Sonnet control EXCEEDS Haiku treatment? (skill redundant for those)
- Do negative tests still hold? (critical — skill shouldn't degrade Sonnet)

**If time permits**, also run Opus 4.6:
```bash
python evals/eval_runner.py --model claude-opus-4-6 --judge-model claude-sonnet-4-6 --runs 1
```

### Priority 2: Sprint 3 End-to-End Test (~30 min)

Sprint 3 (`--update-kb`) was implemented but never tested. Test it:

```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
python -m pipeline.freshness_check --classify --update-kb
```

Must run with `dangerouslyDisableSandbox: true`.

**Expected scenarios**:
1. If 0 changes detected → "No changes to classify" → "No CRITICAL or HIGH" → nothing to update (verify graceful no-op)
2. If changes detected but all MEDIUM/LOW → classification runs but no KB update
3. If CRITICAL/HIGH detected → KB files should be updated with Sonnet 4.6 merge

**If no natural changes exist**, force a test:
- Temporarily modify a checkpoint hash in `pipeline/checkpoint.json` to force a "change" detection
- Or use `--force` to re-check all sources (may detect changes if content drifted since last run)
- Verify: KB file is updated, diff is generated, SKILL.md/references are NOT touched

**Check for edge cases**:
- Does `--update-kb` without `--classify` produce the expected warning?
- Does the LLM merge handle long KB files without hitting token limits?
- Are new KB files created correctly from the template?

### Priority 3: Fix Browser Eval Thinking Panel Extraction (~30 min)

The thinking panel extraction returns empty for all prompts. This is needed to:
1. Confirm skill invocation (thinking text should mention "Consulted product knowledge" or skill name)
2. Detect web search usage in control vs treatment

**Debug approach**:
1. Open Claude.ai in headed browser, send a prompt, wait for response
2. Capture `ab snapshot -i` and look for thinking-related DOM elements
3. Look for: `details`, `summary`, thinking toggle buttons, collapsible panels
4. The current selectors target `[data-testid="thinking-content"]`, `div[class*="thinking"]`, etc.
5. Claude.ai likely changed these to a different pattern — the thinking summary line ("Synthesized platform differences...") is visible in screenshots but the panel content isn't captured

**Key technical context**:
- The thinking toggle was found via `grep -i 'think\|reasoning'` in the snapshot, and `e12` was returned — but `e12` is actually the textbox, not a thinking element. The regex is too broad.
- The JS extraction tries `[data-testid="thinking-content"]` and similar — these may no longer exist
- Check the screenshots in `evals/browser-eval-run-20260313-204830/screenshots/` to see the actual UI

### Priority 4: Production Readiness — Install Path Verification

Verify the skill installs correctly in clean environments:

1. **Skill install via npx**:
   ```bash
   npx skills add claude-got-skills/skills@assistant-capabilities
   ```
   Test in a clean project directory (not this workspace).

2. **Plugin install via CLI**:
   ```bash
   /plugin marketplace add claude-got-skills/skills
   /plugin install claude-got-skills@claude-got-skills
   ```

3. **Claude.ai skill auto-invocation**: Ask a capability question, confirm "Consulted product knowledge" appears in thinking panel.

4. **Spot-check 5 key facts** against live docs:
   - Opus 4.6 model ID: `claude-opus-4-6`
   - 1M context beta header: `context-1m-2025-08-07`
   - Structured outputs GA (no beta header needed)
   - Code Review pricing ($15-25/review)
   - Remote Control command (`claude remote-control`)

### Priority 5: Merge dev → main, Tag v2.5.1

After priorities 1-3 are validated, merge and release:
- dev has 3 commits ahead of main (browser eval fixes, URL fixes, Sprint 3)
- Sprint 3 pipeline commit should NOT go to origin (pipeline/ is gitignored from public repo)
- Tag as v2.5.1 (URL fixes are a patch-level change)
- Push tag to both remotes
- Update version in plugin.json, marketplace.json, quick-reference.md

### Priority 6: Sprint 4 — Propose SKILL.md Edits (Design Only)

When Sprint 3 updates a KB file, the next step is proposing edits to SKILL.md and references. This is the human review gate — no auto-updates to user-facing files.

**Design decisions needed**:
- Generate a PR-style diff showing proposed SKILL.md changes?
- Use which model for SKILL.md edit proposals? (Opus for quality?)
- How to present proposals to the human reviewer? (markdown report? interactive prompt?)
- What triggers Sprint 4? (after Sprint 3 updates KB? on a schedule? manually?)

---

## Key Technical Context

### Environment
- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Sandbox**: Eval runner and pipeline must run with `dangerouslyDisableSandbox: true`
- **Model IDs**: Only shorthands work for 4.6 (`claude-opus-4-6`, `claude-sonnet-4-6`). No dated variants.
- **Plugin installed locally** — SessionStart hook fires every session in this workspace
- **Skill installed on Claude.ai** — at claude.ai/customize/skills, auto-invokes

### Model Training Data Cutoffs
- Opus 4.6: Reliable May 2025, Training Aug 2025
- Sonnet 4.6: Reliable Aug 2025, Training Jan 2026
- Haiku 4.5: Reliable Feb 2025, Training Jul 2025

**Implication for Sonnet eval**: Sonnet 4.6 knows about most features up to Jan 2026 (including 4.6 models, code review, remote control, etc.). The skill's value for Sonnet users is in:
1. Precise API strings (model IDs, headers, tool types) that prevent 400 errors
2. Cross-platform awareness (what works where) not in any single doc page
3. Architecture patterns and decision frameworks
4. Anti-hallucination for deprecated features (old model IDs, removed beta headers)

### Eval Infrastructure
- **API eval**: `evals/eval_runner.py` — 65 tests, 10 categories. Flags: `--model`, `--judge-model`, `--runs`, `--tier1-only`, `--no-judge`
- **Browser eval**: `evals/browser_eval.sh` — `--auth`, `--control`, `--treatment`, `--headed`, `--yes`. Must run foreground (background hangs agent-browser)
- **Judge**: Sonnet 4.6 (`--judge-model claude-sonnet-4-6`). No prefill. Reliable JSON.
- **Haiku baseline**: `evals/eval-report-20260313-201051.md` (65 tests, Sonnet judge)
- **Browser baseline**: `evals/browser-eval-report-20260313-210609.md` (5 prompts, A/B)

### Browser Eval Key Info
- Skills page: `claude.ai/customize/skills` (not Settings > Capabilities)
- `fill` takes ~2.5 min per prompt (character-by-character typing). Total run: ~17 min per condition.
- agent-browser daemon: must be killed between runs if stale. Use `agent-browser --session claude-eval close` (double close to kill daemon).
- Snapshot ref format: `[ref=eN]` — extract with `grep -oE 'ref=e[0-9]+' | sed 's/ref=//'`
- Thinking panel: currently NOT extracted (DOM changed). See Priority 3.

### Pipeline
- 23 sources in `pipeline/config.py`
- Sprint 1 (scrape + detect) + Sprint 2 (classify) verified and working
- Sprint 3 (auto-update KB) implemented but NOT tested: `--classify --update-kb`
- Sprint 4 (propose SKILL.md edits) still TODO
- `pipeline/update_kb.py` uses Sonnet 4.6 for merge, 60K char input limit, safety path checks

### Git Remotes and Push Rules

| Remote | URL | What to push |
|--------|-----|--------------|
| `origin` | `github.com/claude-got-skills/skills` | **Public repo** — code, evals, skill content, plugin files. No docs, pipeline, or agent outputs. |
| `dev` | `github.com/liam-jons/skills-dev` | **Private repo** — everything from origin PLUS `docs/`, `pipeline/`. |

When committing:
1. **Code/eval changes** → normal `git add` + `git commit` → `git push origin dev` + `git push dev dev`
2. **Docs/pipeline** → `git add -f docs/... pipeline/...` → separate commit → `git push dev dev` only (NOT origin)
3. **Selective push to origin**: Use `git push origin <commit-sha>:dev` to push only up to a specific commit

### Key Files
```
pipeline/update_kb.py                 — Sprint 3 KB auto-update (NEW, untested)
pipeline/freshness_check.py           — main pipeline entry (--update-kb flag added)
pipeline/config.py                    — 23 source URLs + kb_files mapping
pipeline/classify.py                  — Haiku classification
data/quick-reference.md               — Tier 1 content (100 lines, v2.5.0)
skills/assistant-capabilities/SKILL.md — main skill (280 lines, v2.5.0)
references/api-features.md            — API features (rate limits pointer FIXED)
references/model-specifics.md         — model specs (pricing pointer FIXED)
evals/eval_runner.py                  — 65 tests, 10 categories
evals/rubrics.py                      — 65 independent judge rubrics
evals/browser_eval.sh                 — FIXED: ref format, networkidle, stale daemon
evals/eval-report-20260313-201051.md  — v2.5.0 Haiku baseline (Sonnet judge)
evals/browser-eval-report-20260313-210609.md — first A/B browser eval
.claude-plugin/marketplace.json       — v2.5.0, codebase-review v1.2.0
plugins/codebase-review/              — v1.2.0, 17 improvements
```

### Maintenance Strategy (v2.5.0 Decision Framework)
When adding new content to the skill, apply this test:
1. Load-bearing string (model ID, header, tool type)? → KEEP (bootstrapping)
2. Wrong value causes error (400, 404, silent failure)? → KEEP (error prevention)
3. Architectural guidance not in any single docs page? → KEEP (unique advisory)
4. Prevents common hallucination? → KEEP (anti-hallucination)
5. Number that changes independently of features? → POINTER (price, rate limit)
6. Version number with no functional implication? → POINTER or omit
