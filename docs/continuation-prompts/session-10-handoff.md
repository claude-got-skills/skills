# Session 10 Handoff: v2.1.0 Released, KB Refresh Complete, Ready for Launch

## Project Context

We are building and maintaining Claude skills under the **claude-got-skills** GitHub account. The primary skill — **Claude Capabilities Awareness** — gives Claude comprehensive, accurate knowledge about its capabilities across all platforms (Claude.ai, Desktop, Claude Code, CoWork, API).

**GitHub repo**: https://github.com/claude-got-skills/skills
**Skill status**: v2.1.0 on `main`. Dev branch synced.
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.

---

## Session 9→10 Completed Work

### 1. New Eval Tests ✅

Added 9 tests (24→33 total, 7 categories). All showing treatment lift, no regressions:

| ID | Category | Topic |
|----|----------|-------|
| 2.4 | Can Claude Do X | Vision/image analysis |
| 2.5 | Can Claude Do X | CoWork platform |
| 3.4 | Implementation Guidance | PDF processing |
| 3.5 | Implementation Guidance | Streaming with tool use |
| 3.6 | Implementation Guidance | Fast mode |
| 3.7 | Implementation Guidance | Automatic caching |
| 3.8 | Implementation Guidance | Dynamic filtering |
| 5.8 | Extension Awareness | Platform comparison |
| 7.5 | Hallucination Detection | Model deprecation (Sonnet 3.7) |

### 2. Full Knowledge-Base Refresh ✅ (Major)

All 28 KB files re-scraped from source docs via Firecrawl (parallel batches of 2).
4 parallel diff agents identified changes: 9 MAJOR, 12 MODERATE, 6 MINOR, 1 scrape issue.

**Key discoveries incorporated into skill:**
- Agent SDK: `query()` now supports hooks + custom tools, new `Transport` class, `list_sessions()`/`get_session_messages()`
- Programmatic tool calling GA: tool version `code_execution_20260120`, web search/fetch no longer restricted
- Structured outputs GA on Bedrock, schema complexity limits (max 20 strict tools, 24 optional params)
- Task tool renamed to Agent (v2.1.63), legacy `Task(...)` still works as alias
- New hook events: `ConfigChange`, `TeammateIdle`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`
- HTTP hooks (`type: "http"`) — new hook type
- `.claude/rules/` as new organization option, CLAUDE.md guideline reduced to ~200 lines
- 5 bundled skills: `/simplify`, `/batch`, `/debug`, `/loop`, `/claude-api`
- `CLAUDE_SKILL_DIR` variable
- Plugin `commands/` renamed to `skills/`, new `settings.json`, `/plugin-name:skill-name` syntax
- Claude.ai MCP servers auto-available in Claude Code
- Edge browser support alongside Chrome
- New sandbox settings: `allowWrite`/`denyWrite`/`denyRead`
- Structured outputs: property ordering docs, ZDR eligible
- Memory tool: "Using with Compaction" and "Multi-session development pattern"
- "Context rot" concept in context windows docs
- mcp-apps-overview.md: can't fully scrape (JS tabs), patched 3 values manually (spec version, client support, API docs URL)

### 3. Reference File Updates ✅

5 parallel agents updated all reference files with KB findings:
- `agent-capabilities.md`: SDK changes, Agent tool rename, HTTP hooks, new events, plugin changes (509 lines)
- `api-features.md`: Memory GA, structured outputs Bedrock GA + limits, context rot, caching (659 lines)
- `tool-types.md`: PTC GA + `code_execution_20260120`, computer use Sonnet 4.6, tool design practices (466 lines)
- `claude-code-specifics.md`: Agent rename, new hooks, bundled skills, .claude/rules/, sandbox, MCP (539 lines)
- `model-specifics.md`: Sonnet 4.6 across features, GA promotions, migration guides (310 lines)

### 4. SKILL.md Updates ✅

Targeted edits: structured outputs Bedrock GA + schema limits, Agent SDK query() hooks, Agent tool rename, bundled skills, .claude/rules/, `code_execution_20260120`. Now 259 lines.

### 5. Browser Eval Prompts Updated ✅

Replaced 2 of 5 prompts for v2.0 coverage (vision/PDF, platform comparison).
**Full A/B test NOT yet run** — requires Chrome to be closed first.

### 6. Freshness Diff Report Archived ✅

14/16 items resolved. Item 14 (1M context tier 3 vs 4) still unverified.

### 7. Automation Research ✅

Comprehensive analysis of freshness pipeline and Distill.io history. See "Pipeline Gaps" section below.

---

## Current Git State

```
Branch: main (up to date with origin)
Dev: synced with main
Tag: v2.1.0

Commit history (session 10 work):
a56add7 (HEAD -> main, tag: v2.1.0) Merge dev: KB refresh, 9 new eval tests, reference updates
f1f7380 Refresh all 28 KB files and update SKILL.md + 5 reference files
7bf5294 Update browser eval prompts for v2.0 coverage, archive freshness diff report
9432646 Add 9 eval tests for v2.0 content: vision, PDF, streaming, fast mode, caching, filtering, CoWork, platform comparison, model deprecation
```

---

## Session 11 Priority Order

### 1. Publish Skill to skills.sh (~30 min)

The skill has never been published to the skills.sh registry. This is the public marketplace for Claude Code skills.

Steps:
1. Check current `skills.sh` submission process — may need to register the repo or submit via PR
2. Verify `marketplace.json` at `.claude-plugin/marketplace.json` is correct
3. Test install: `npx skills add claude-got-skills/skills@claude-capabilities`
4. Submit to skills.sh registry if not already listed
5. Verify the skill appears in `find-skills` search results

### 2. Run Browser Eval (~30 min)

Auth state may have expired. Close Chrome first, then:
```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
./evals/browser_eval.sh --auth    # If auth expired — headed Chrome, manual login + 2FA
./evals/browser_eval.sh           # Full A/B test (5 prompts × 2 conditions)
```

Browser eval uses real Chrome binary via `--executable-path` to avoid bot detection. **Cannot run while Chrome is open.** Auth state at `evals/claude-ai-auth-state.json` (21 cookies, may expire between sessions).

### 3. Claude.ai ZIP Packaging & Testing (~1 hr)

Test the skill works correctly when uploaded as ZIP to Claude.ai:
1. Package SKILL.md into a ZIP file
2. Upload to Settings > Capabilities > Skills on Claude.ai
3. Test with prompts from browser eval (vision/PDF, platform comparison, thinking, model selection, memory)
4. Verify auto-invocation triggers from natural language
5. Confirm reference file content is inlined in Quick Reference section (since Claude.ai can't read reference files)

### 4. Freshness Pipeline Improvements (~2 hrs)

The pipeline works for change detection but has significant gaps. Address in priority order:

**4a. Fix KB file mapping (30 min)**
`pipeline/config.py` maps sources to KB filenames that don't match actual files. Update `kb_files` values to match the real naming convention (`claude-capabilities-*.md`, `claude-code-capabilities-*.md`).

**4b. Expand source coverage (30 min)**
Add missing sources to cover more of the 28 KB files. Priority additions:
- `platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use`
- `platform.claude.com/docs/en/build-with-claude/structured-outputs`
- `platform.claude.com/docs/en/build-with-claude/files`
- `platform.claude.com/docs/en/agent-sdk/overview`
- `modelcontextprotocol.io/extensions/apps/overview`

**4c. Replace Jina Reader with Firecrawl for code.claude.com (30 min)**
Jina Reader returns ~4,400 chars of boilerplate for code.claude.com pages. Switch to Firecrawl CLI (`firecrawl scrape --only-main-content`) for these sources. Requires Firecrawl API key in `.env`.

**4d. Add --update-kb flag (30 min)**
When a source changes and `--update-kb` is set, write scraped content directly to the mapped KB file. Closes the gap between "change detected" and "KB file updated".

### 5. Verify 1M Context Tier Requirement (~15 min)

SKILL.md and api-features.md say "tier 3+" but one KB source said "tier 4+". Scrape the current pricing/tier page to confirm which is correct. This has been unresolved since session 9.

### 6. Multi-Run Eval for Variance (~30 min)

The single-run eval shows Haiku variance (Architecture Decisions fluctuated 3→4.67→3 across runs). Run a 3-run eval to get stable means:
```bash
python3 evals/eval_runner.py --runs 3
```

### 7. Distill.io Cleanup (~15 min)

Distill.io is fully replaced by the freshness pipeline:
- Mark `monitoring/distill-monitoring-setup.md` as archived/historical
- Disable any remaining Distill browser extension monitors
- Remove Distill-specific references from any active docs

---

## Key Technical Context

### Environment

- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Python**: eval_runner.py needs `anthropic` package (installed globally, no .venv)
- **Pipeline deps**: trafilatura, requests (installed globally)
- **Firecrawl**: CLI installed (`firecrawl-cli`), authenticated, pay-as-you-go (~225 credits remaining). Concurrency limit: 2 parallel jobs.
- **agent-browser**: Uses real Chrome (`--executable-path`) with `--disable-blink-features=AutomationControlled`. Auth state at `evals/claude-ai-auth-state.json` (gitignored, may expire). Re-auth: `./evals/browser_eval.sh --auth`
- **Freshness pipeline**: Active, launchd loaded, twice daily at 09:00/21:00. Plist loaded directly (not symlinked to `~/Library/LaunchAgents/`).

### Pipeline Gaps (from automation research)

| Gap | Description | Fix Effort |
|-----|-------------|------------|
| 1 | Detection only — no auto-update of KB/references | Medium |
| 2 | `kb_files` mapping uses wrong filenames | Low |
| 3 | 13 monitored URLs vs 28 KB files | Low |
| 4 | Jina Reader returns boilerplate for code.claude.com | Low |
| 5 | No Claude-powered diff classification | Medium |
| 6 | No eval integration (auto-run on changes) | Medium |
| 7 | No PR/commit automation | High |
| 8 | support.claude.com extraction thin (~1,079 chars) | Low |
| 9 | No virtualenv (depends on global packages) | Low |
| 10 | No new page detection | Medium |

Distill.io is fully replaced. `monitoring/distill-monitoring-setup.md` is historical reference only.

### Eval Infrastructure

| Runner | Tests | Use |
|--------|-------|-----|
| `evals/eval_runner.py` | 33 tests, 7 categories | Content quality (API-based, keyword + LLM judge) |
| `evals/browser_eval.sh` | 5 prompts | Claude.ai real-world testing (agent-browser) |
| Skill-creator `run_eval.py` | N/A | Trigger accuracy (not suited for self-referential skills) |

### File Inventory

```
SKILL.md:                         259 lines
references/api-features.md:      659 lines
references/agent-capabilities.md: 509 lines
references/claude-code-specifics.md: 539 lines
references/tool-types.md:        466 lines
references/model-specifics.md:   310 lines
Total skill content:              2,742 lines

Eval reports:   7 total (5 from session 9, 2 from session 10)
Pipeline:       8 Python files + shell wrapper + launchd plist
Browser eval:   browser_eval.sh (737 lines) + browser_eval_report.py (355 lines)
Knowledge-base: 28 source files (all refreshed 2026-03-09)
```

### Platform Support Matrix (verified)

| Capability | Claude.ai | Desktop | Claude Code | CoWork |
|---|---|---|---|---|
| Skills (auto-invoke) | Yes (ZIP) | Yes (ZIP) | Yes (filesystem) | Yes |
| Skills (slash /name) | -- | -- | Yes | Via plugins |
| MCP | Connectors (paid) | Settings | Full (stdio/HTTP/SSE) | Via plugins |
| Projects | Yes | Yes | -- (use CLAUDE.md) | -- |
| Plugins/Hooks | -- | -- | Yes | -- |
| Subagents/Teams | -- | -- | Yes | -- |
| Background/Loop | -- | -- | Yes | -- |

### Frontmatter Constraints (Claude.ai/Desktop upload)

- No YAML block scalars (`>`, `|`)
- No colons in description value
- "Claude" reserved in `name` field — use `assistant-capabilities`
- Only allowed keys: name, description, license, allowed-tools, compatibility, metadata

---

## Research Findings (from session 10)

### KB Refresh Results

28 files compared via 4 parallel diff agents:

| Change Level | Count | Highlights |
|---|---|---|
| MAJOR | 9 | Agent SDK Python, features-overview, memory-tool, new-in-opus-4-6, PTC, structured-outputs, hooks, subagents, MCP |
| MODERATE | 12 | agent-sdk-overview, computer-use, context-windows, implement-tool-use, mcp-via-api, agent-teams, cli-reference, create-plugins, extension-options, plugin-reference, sandboxing, skills |
| MINOR | 6 | agent-skills-via-api, pdf-support, search-results-citations, files-api, use-chrome-browser, use-cli |
| SCRAPE ISSUE | 1 | mcp-apps-overview (JS tabs can't be scraped — patched 3 values manually) |

### Automation Pipeline Architecture

Current: `launchd (09:00/21:00) → scrape 13 URLs → SHA-256 detect → markdown report → macOS notification`

Recommended end-to-end flow:
```
launchd → scrape (Firecrawl for code.claude.com, trafilatura for API docs)
        → SHA-256 detect changes
        → Claude-powered diff classification (new feature / deprecation / breaking / cosmetic)
        → auto-update KB files (--update-kb flag)
        → propose SKILL.md/reference edits
        → auto-run eval_runner.py (gate on passing scores)
        → auto-commit to dev branch + create PR
        → macOS notification with summary
```

### Firecrawl Usage Notes

- Concurrency limit: 2 parallel jobs (plan-dependent)
- Credits: pay-as-you-go, ~225 remaining after session 10
- KB refresh cost: ~30 credits for 28 URLs + 2 URL discovery + 2 search queries
- Best approach: bash script with `& wait` for parallel batches, not subagents (bottleneck is API concurrency, not processing)
- `--only-main-content` flag recommended for cleaner extractions
- code.claude.com pages scrape well via Firecrawl (unlike Jina Reader)
- mcp-apps pages with JS tabs don't fully render even with `--wait-for 3000`
