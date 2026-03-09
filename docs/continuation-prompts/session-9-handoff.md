# Session 9 Handoff: v2.0 Released, Cross-Platform Restructure Complete

## Project Context

We are building and maintaining Claude skills under the **claude-got-skills** GitHub account. The primary skill — **Claude Capabilities Awareness** — gives Claude comprehensive, accurate knowledge about its capabilities across all platforms (Claude.ai, Desktop, Claude Code, CoWork, API).

**GitHub repo**: https://github.com/claude-got-skills/skills
**Skill status**: v2.0.0 on `main` (cross-platform restructure). Dev branch synced.
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.

---

## Session 8→9 Completed Work

### 1. Content Freshness Updates ✅

- Applied all 16 items from freshness diff report (Sonnet 4.6, 6 GA promotions, pricing fixes, model retirements)
- Scraped missing API details via Firecrawl: fast mode (beta header `fast-mode-2026-02-01`, 6x pricing), automatic caching (`{"type": "ephemeral"}` not `"auto"`), dynamic filtering (`web_search_20260209`/`web_fetch_20260209` tool versions)
- Updated all 5 reference files to 2026-03-07/09

### 2. Freshness Pipeline Built & Activated ✅

- `pipeline/` — 8 Python files: config, scrape (trafilatura + Jina Reader), detect (SHA-256), report, notify (macOS), orchestrator, shell wrapper
- `launchd/` — plist loaded and active, runs at 09:00 and 21:00
- Smoke-tested: GitHub CHANGELOG extraction works end-to-end
- Replaces Distill.io (hit free tier limits)

### 3. Browser Eval Built ✅

- `evals/browser_eval.sh` (737 lines) — agent-browser A/B testing on Claude.ai
- `evals/browser_eval_report.py` (355 lines) — report generator with skill trigger detection
- Fixed bot detection: uses real Chrome binary via `--executable-path` with anti-automation flags
- Auth state saved (user logged in via headed Chrome session)
- **Not yet run**: full A/B test still pending

### 4. Automation Features Added ✅

- Added `/loop`, background tasks (`Ctrl+B`, `run_in_background`), cron tools (`CronCreate/Delete/List`)
- New "Background Tasks & Scheduling" section in claude-code-specifics.md
- Eval tests 5.6 (recurring monitoring) and 5.7 (background tasks) added

### 5. v2.0 Restructure ✅ (Major)

Complete rewrite of SKILL.md from "post-training corrections" to "comprehensive capabilities awareness":

**New sections added:**
- **Core Capabilities**: vision/images, PDF processing, multilingual, streaming, common misconceptions (no embeddings, no fine-tuning)
- **Platform Overview**: Claude.ai vs Desktop vs Claude Code vs CoWork with feature availability matrix
- **Quick Reference**: expanded with temperature, max_tokens, streaming, image/PDF input formats
- Extension pattern table now shows platform availability per feature

**Reference file additions:**
- api-features.md: Vision & Image Processing, PDF Processing, Streaming (SSE events), Rate Limits & Usage Tiers
- model-specifics.md: Common Misconceptions table
- Platform Availability Matrix updated with Vision/PDF/Streaming rows

**Structural changes:**
- Dropped "(Post-Training)" labels from section headers
- Broadened description with new trigger keywords (vision, PDF, streaming, Claude Desktop, CoWork)
- Reframed extension guidance as platform-aware (shows which extensions work where)

### 6. Codebase Alignment ✅

- README.md: complete rewrite for v2.0
- marketplace.json: description updated
- eval_runner.py: version bumped v1.3.0 → v2.0.0
- CLAUDE.md: updated scope, line counts, conventions
- MEMORY.md: updated with platform matrix, pipeline status

### 7. Eval Validation ✅

5 eval runs this session, all passing with strong lift and no regressions:
- Latest (v2.0, eval-report-20260309-180149): Treatment lift across all categories
- Model Selection: 0→6 (from zero baseline)
- Can Claude Do X: 1.67→5.00
- Negative tests: 4.67→4.67 (no regression)

---

## Current Git State

```
Branch: main (up to date with origin)
Dev: synced with main
Tag: v2.0.0

Commit history (session 9 work):
f2e1ff0 (HEAD -> main) Update codebase for v2.0: README, marketplace, eval version, CLAUDE.md
718a0eb (tag: v2.0.0) v2.0: Restructure skill for cross-platform "art of the possible" coverage
d530407 Fix API details from scrape: fast mode header, auto caching value, dynamic filtering versions
c3610f0 Add background tasks, /loop, and cron scheduling to skill + eval tests
302d37f Update eval tests for GA promotions: memory tool, Sonnet 4.6, adaptive thinking
9cde713 Add freshness pipeline and browser eval infrastructure
4f16f04 Complete content updates: automatic caching, fast mode, dynamic filtering, description optimization
```

---

## Session 10 Priority Order

### 1. Add New Eval Tests (~1.5 hrs)

9 tests identified covering v2.0 content gaps:

| # | Category | Prompt Focus |
|---|----------|--------------|
| 1 | Can Claude Do X | Vision/image analysis — formats, API shape, token costs |
| 2 | Implementation Guidance | PDF processing — 80-page doc, limits, best practices |
| 3 | Extension Awareness | Platform comparison — skill on Claude.ai vs Desktop vs Code |
| 4 | Can Claude Do X | CoWork — what it is, what extensions it supports |
| 5 | Implementation Guidance | Streaming with tool use — SSE events, implementation |
| 6 | Implementation Guidance | Fast mode — speed parameter, pricing, constraints |
| 7 | Implementation Guidance | Automatic caching — multi-turn without manual breakpoints |
| 8 | Implementation Guidance | Dynamic filtering — noisy web search results |
| 9 | Hallucination Detection | Model deprecation — using retired Sonnet 3.7 in production |

### 2. Run Browser Eval (~30 min)

Auth state is saved. Run the full A/B test:
```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
./evals/browser_eval.sh
```

Consider updating the 5 browser prompts to cover v2.0 content:
- Replace one prompt with a vision/PDF question
- Replace one with a platform comparison question

### 3. Knowledge-Base File Refresh (~2-3 hrs)

28 files in `knowledge-base/` are stale. The freshness pipeline will have run by session 10 and flagged which sources have drifted. Use the pipeline reports to prioritize:

```bash
ls pipeline/reports/  # Check for freshness reports
```

Strategy: re-scrape the highest-priority sources (release notes, models overview, CHANGELOG) and update the KB files. Lower-priority source docs can be refreshed incrementally.

### 4. Claude.ai ZIP Packaging & Testing (~1 hr)

Test that the skill works correctly when uploaded as ZIP to Claude.ai:
1. Package SKILL.md into a ZIP
2. Upload to Settings > Capabilities > Skills
3. Test with the browser eval prompts
4. Verify auto-invocation triggers from natural language

### 5. Freshness Diff Report Cleanup (~15 min)

Archive `docs/freshness-diff-report.md` — 14/16 items resolved in v2.0. Item 14 (1M context tier requirement: tier 3 vs tier 4) still unverified. Item 16 (KB file refresh) pending.

### 6. Session-9 Continuation Prompt (~15 min)

Create handoff for session 10 if not all items completed.

---

## Key Technical Context

### Environment

- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Python**: eval_runner.py needs `anthropic` package (installed)
- **Pipeline deps**: trafilatura, requests (installed)
- **agent-browser**: Uses real Chrome (`--executable-path`) with `--disable-blink-features=AutomationControlled`. Auth state saved at `evals/claude-ai-auth-state.json` (gitignored, 21 cookies). May expire between sessions — if so, re-run `./evals/browser_eval.sh --auth` (headed Chrome, manual login + 2FA, ~30s)
- **Firecrawl**: Available as MCP tool for ad-hoc scraping
- **Freshness pipeline**: Active, launchd loaded, twice daily at 09:00/21:00

### Platform Support Matrix (verified)

| Capability | Claude.ai | Desktop | Claude Code | CoWork |
|---|---|---|---|---|
| Skills (auto-invoke) | Yes (ZIP) | Yes (ZIP) | Yes (filesystem) | Yes |
| Skills (slash /name) | -- | -- | Yes | Via plugins |
| MCP | Connectors (paid) | Settings | Full (stdio/HTTP/SSE) | Via plugins |
| Projects | Yes | Yes | -- (use CLAUDE.md) | -- |
| Plugins/Hooks | -- | -- | Yes | -- |
| Subagents/Teams | -- | -- | Yes | -- |

### Frontmatter Constraints (Claude.ai/Desktop upload)

- No YAML block scalars (`>`, `|`)
- No colons in description value
- "Claude" reserved in `name` field — use `assistant-capabilities`
- Only allowed keys: name, description, license, allowed-tools, compatibility, metadata

### Eval Infrastructure

| Runner | Tests | Use |
|--------|-------|-----|
| `evals/eval_runner.py` | 24 tests, 7 categories | Content quality (API-based, keyword + LLM judge) |
| `evals/browser_eval.sh` | 5 prompts | Claude.ai real-world testing (agent-browser) |
| Skill-creator `run_eval.py` | N/A | Trigger accuracy (not suited for self-referential skills) |

### File Inventory

```
SKILL.md:                 252 lines
references/api-features.md:     630 lines
references/agent-capabilities.md: 451 lines
references/claude-code-specifics.md: 463 lines
references/tool-types.md:       452 lines
references/model-specifics.md:  297 lines
Total skill content:      2,545 lines

Eval reports:             5 from this session (20260308-000551 through 20260309-180149)
Pipeline:                 8 Python files + shell wrapper + launchd plist
Browser eval:             browser_eval.sh (737 lines) + browser_eval_report.py (355 lines)
Knowledge-base:           28 source files (stale, pending refresh)
```

---

## Research Findings (from this session)

### Platform Research
- Claude Desktop and Claude.ai both support skills via ZIP upload (Settings > Capabilities > Skills)
- CoWork supports skills via auto-invocation and slash commands via plugins
- No platform detection mechanism exists — skills can't conditionally show content
- Reference files only work in Claude Code (requires Read tool)
- Detailed matrix source: `ai-smb-playbook/app/src/content/shared/skills-extensions-data.ts`

### Content Gap Analysis
- Vision/images and PDF processing were completely absent — now added
- Streaming, rate limits, common misconceptions were absent — now added
- The skill was ~40% Claude Code-specific content — now rebalanced with Platform Overview section
- "Post-training" framing missed fundamental capabilities — broadened to comprehensive coverage

### API Detail Corrections
- Fast mode requires beta header `fast-mode-2026-02-01` (was incorrectly "None")
- Automatic caching uses `{"type": "ephemeral"}` not `{"type": "auto"}`
- Dynamic filtering uses `web_search_20260209`/`web_fetch_20260209` (newer tool versions)
- Fast mode pricing is 6x ($30/$150 MTok), no long context surcharge
- Minimum cacheable lengths vary by model (4,096 for Opus/Haiku, 2,048 for Sonnet 4.6)
