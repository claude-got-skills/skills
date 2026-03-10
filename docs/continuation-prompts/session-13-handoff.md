# Session 13 Handoff: Plugin Architecture Live, Distribution Solved, Pipeline Operational

## Project Context

We are building and maintaining Claude skills under the **claude-got-skills** GitHub account. The primary skill — **Claude Capabilities Awareness** — gives Claude comprehensive, accurate knowledge about its capabilities across all platforms (Claude.ai, Desktop, Claude Code, CoWork, API).

**GitHub repo**: https://github.com/claude-got-skills/skills
**Private dev repo**: https://github.com/liam-jons/skills-dev
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.
**skills.sh listing**: https://skills.sh/claude-got-skills/skills/assistant-capabilities

---

## Session 12 Completed Work

### 1. Private Dev Repo Created ✅

- `liam-jons/skills-dev` on GitHub (private)
- Contains: 22 eval result JSONs, 2 eval reports, automation pipeline design doc, continuation prompts, monitoring doc
- Pipeline files stay local (machine-specific, gitignored)

### 2. Public Repo Audit + Fixes ✅

- README: updated eval results v2.1.0 → v2.2.0 (43 tests, 8 categories)
- README: fixed skill path `claude-capabilities/` → `assistant-capabilities/`
- README: removed 4 gitignored dirs from structure tree
- Removed legacy `evals/capabilities-skill-eval.py` (999 lines, superseded by eval_runner.py)
- gitignore: added eval-set and description-optimization patterns

### 3. Cross-Platform Content Fixes ✅ (Tests 8.7 + 8.10)

Root cause: SKILL.md described what platforms HAVE but never what they LACK.

Fixes applied:
- **Context & Memory**: Added Memory tool platform availability (API-only, not Claude.ai/Desktop). Added persistence options per platform (Projects, CLAUDE.md, skills).
- **Platform table**: Added "Cross-conv. memory" row showing Projects/CLAUDE.md/skills per platform.
- **Upgrade path**: Added explicit "Upgrading from Claude.ai/Desktop" paragraph — Claude.ai/Desktop cannot run code, access filesystems, or orchestrate multi-step workflows. Directs to Claude Code or Agent SDK.
- **Agent Capabilities**: Scoped Agent SDK, Subagents, Hooks, Plugins to "Claude Code only".

### 4. Two-Tier Plugin Architecture ✅ (Major)

Evolved from skill-only to full plugin with SessionStart hook injection:

**Architecture:**
```
.claude-plugin/
├── plugin.json              # Plugin manifest (v2.3.0)
└── marketplace.json         # Dual schema: plugins[] + skills[]
hooks/
└── hooks.json               # SessionStart hook (startup|resume|clear|compact)
scripts/
└── inject-capabilities.sh   # Reads quick-reference, outputs JSON (jq-first, python3 fallback)
data/
└── quick-reference.md       # Condensed ~90 lines, ~1.2K tokens (Tier 1)
skills/
└── assistant-capabilities/
    ├── SKILL.md              # Full ~270 lines (Tier 2, on-demand)
    └── references/           # 5 reference files (~2,400 lines)
```

- **Tier 1 (always-on)**: `data/quick-reference.md` injected via SessionStart hook into every session. Focused on **the art of the possible** — how capabilities compose, platform availability, key parameters. ~1.2K tokens.
- **Tier 2 (on-demand)**: Full SKILL.md + 5 reference files loaded when Claude needs deep answers.

### 5. Dual Distribution ✅

marketplace.json now supports both install methods:

| Path | Command | What Users Get |
|------|---------|----------------|
| **Full plugin** | `/plugin marketplace add claude-got-skills/skills` then `/plugin install claude-got-skills@claude-got-skills` | SessionStart hook + skill + references |
| **Skill only** | `npx skills add claude-got-skills/skills@assistant-capabilities` | On-demand skill only |
| **Claude.ai/Desktop** | ZIP upload | Skill only |

Key finding: `npx skills add` installs skills only (no hooks). For the full plugin experience with SessionStart hook, users must use `/plugin marketplace add` + `/plugin install`.

### 6. Plugin Validation ✅

- **PASS** overall from plugin-dev:plugin-validator
- No critical issues
- Fixed: inject script uses jq-first with python3 fallback (portability)
- Fixed: README token estimate corrected to ~1.2K
- Known: Description still too long (~1,123 chars with "MANDATORY TRIGGERS") — optimization in progress

### 7. Pipeline Sprint 1 Complete ✅

- Full (non-dry-run) execution succeeded: 12 sources, 0 errors, ~9 seconds
- 5 "changes" were extraction method normalization (Jina → trafilatura), not actual content changes — future runs will be stable
- 6 Firecrawl credits consumed per run (~360/month at twice-daily schedule)
- Launchd agent confirmed loaded and running (09:00/21:00 schedule)
- All checkpoint content is real documentation

### 8. 3-Run Eval Complete ✅

| Category | Tests | Ctrl | Trt | Lift | Variance |
|----------|-------|------|-----|------|----------|
| Architecture Decisions | 3 | 1.44 | 4.33 | **+200%** | Low |
| Can Claude Do X | 5 | 2.13 | 4.20 | **+97%** | Low |
| Implementation Guidance | 8 | 2.50 | 4.67 | **+87%** | Low |
| Model Selection | 1 | 1.00 | 6.00 | **+500%** | High (1 test) |
| Extension Awareness | 8 | 1.92 | 4.25 | **+122%** | Low |
| Hallucination Detection | 5 | 1.60 | 3.20 | **+100%** | Low |
| Cross-Platform | 10 | 1.97 | 3.90 | **+98%** | Low |
| **Negative (no regression)** | **3** | **5.00** | **4.78** | **-4%** | Noise |

**Important**: Category 6 = "Negative (No Change Expected)", Category 7 = "Hallucination Detection". Previous session notes had these swapped. The -4% on Negative is noise (1 keyword miss in 2/9 runs). All positive categories stable with low variance.

### 9. Description Optimization (In Progress)

The skill-creator `run_loop.py` was kicked off with a 20-query eval set (10 should-trigger, 10 should-not). Multiple generations of candidate descriptions have been produced. The latest generation converged on two patterns:

**Pattern A** (~480 chars):
> "Use when users ask about current Claude capabilities, API features, model specifications, or need guidance building with Claude. Triggers for queries about model selection, context limits, pricing, streaming, tool use, structured outputs, platform differences (Claude.ai vs Desktop vs Claude Code), extension patterns (skills vs hooks vs MCP), architectural decisions, or 'what can Claude do' questions..."

**Pattern B** (~450 chars):
> "Use when users need to make implementation decisions or configure Claude for their specific use case. Triggers for questions about choosing models, configuring API parameters, enabling beta features, understanding current limits and pricing, comparing platform options..."

Both are dramatically better than the current "MANDATORY TRIGGERS" keyword-stuffing approach. The optimization agent may still be running — check its output and apply the winning description.

### 10. Installed Quality Tools Documented ✅

| Tool | Plugin | Use Case |
|------|--------|----------|
| `run_loop.py` | skill-creator | Empirical description optimization |
| skill-reviewer agent | plugin-dev | Structured quality review |
| plugin-validator agent | plugin-dev | Plugin structure validation |
| writing-skills | superpowers | Skill authoring best practices |
| developing-claude-code-plugins | superpowers-dev | Plugin ecosystem reference |
| claude-session-driver | superpowers-marketplace | Parallel eval orchestration |

---

## Current Git State

```
Branch: dev (synced with main, up to date with origin)

Commit history (session 12 work):
a319c19 (HEAD -> dev, origin/main, origin/dev, main) Enable dual distribution: plugin marketplace + skill-only install
b1e3dad Add two-tier capabilities plugin with SessionStart hook
a94608d Fix public repo: update README for v2.2.0, strengthen cross-platform content
e6da8c9 Fix browser eval auth: URL pattern and state loading
1ba8109 Fix eval runner skill path after directory rename
```

---

## Session 13 Priority Order

### 1. Apply Description Optimization Result (~30 min)

Check if the description optimization agent completed. If so:
1. Review the winning description from its output
2. Apply to SKILL.md frontmatter
3. Run a quick eval to verify no score regression
4. Commit and push

If the agent didn't complete, run it again with:
```
skill-creator run_loop.py --eval-set evals/eval-set-description-triggers.json --skill-path skills/assistant-capabilities --max-iterations 5
```

### 2. Tier 1 Eval (Plugin Hook Effectiveness) (~1 hr)

Add a `--tier1-only` flag to `eval_runner.py` that:
- Prepends `data/quick-reference.md` content as a system message (simulating the SessionStart hook)
- Runs the same 43 tests WITHOUT loading the skill
- Measures how much the always-on quick-reference alone improves accuracy

This tells us the value of the plugin's hook vs skill-only install. Expected: moderate lift on all categories (Tier 1 has key facts) but less than full skill (no reference files).

### 3. Test Plugin Installation End-to-End (~30 min)

Verify the full plugin install path works:
```
/plugin marketplace add claude-got-skills/skills
/plugin install claude-got-skills@claude-got-skills
```
Then start a new session and verify:
- SessionStart hook fires and injects quick-reference content
- The skill auto-invokes on capability questions
- Both tiers work together

### 4. Pipeline Sprint 2: Change Classification (~2-3 hrs)

Add Claude Haiku-powered change classification to the freshness pipeline:
- When change detected, classify as BREAKING/NEW_FEATURE/DEPRECATION/BUG_FIX/COSMETIC
- Only BREAKING and NEW_FEATURE trigger notifications
- Estimated cost: ~$0.005/classification call
- See `docs/automation-pipeline-design.md` Stage 3 for implementation details

### 5. Browser Eval Rewrite (~2 hrs)

Fix agent-browser eval for Claude.ai testing:
- Run in headed mode (fixes Cloudflare blocking)
- Update input field selectors for current Claude.ai UI
- Add --yes flag for non-interactive execution
- Core logic is solid, only auth/selectors need updating

### 6. Official Anthropic Marketplace Submission (~30 min)

Submit the plugin to the official Anthropic marketplace for maximum reach:
- Submission via Claude.ai settings or platform.claude.com
- Would enable: `/plugin install claude-got-skills@claude-plugins-official`
- Simplest install path for users

### 7. Version Tag + Release (~15 min)

Tag v2.3.0 with release notes covering:
- Two-tier plugin architecture
- SessionStart hook injection
- Dual distribution (plugin + skill)
- Cross-platform content fixes
- 3-run eval variance confirmation

### 8. Claude.ai ZIP Packaging + Testing (~1 hr)

Package SKILL.md as ZIP for Claude.ai/Desktop upload:
1. Verify frontmatter compatibility (no colons, no block scalars)
2. Create ZIP, upload to Settings > Capabilities > Skills
3. Test cross-platform prompts from eval tests

---

## Key Technical Context

### Environment

- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Python**: eval_runner.py needs `anthropic` package (installed globally)
- **Firecrawl**: CLI v1.2.1, auth via shell env. ~210 credits remaining (6 used in Sprint 1 run)
- **agent-browser**: v0.13.0. Auth state expired. Re-auth: `./evals/browser_eval.sh --auth`
- **Freshness pipeline**: Operational, launchd running 09:00/21:00. Uses Firecrawl for code.claude.com, trafilatura for API docs.
- **Skill installed globally**: `~/.agents/skills/assistant-capabilities/`

### Eval Category Mapping (CORRECT)

| ID | Category | Expected Behavior |
|----|----------|-------------------|
| 1.x | Architecture Decisions | High positive lift |
| 2.x | Can Claude Do X | High positive lift |
| 3.x | Implementation Guidance | High positive lift |
| 4.x | Model Selection | High positive lift |
| 5.x | Extension Awareness | High positive lift |
| 6.x | **Negative (No Change Expected)** | ~0% lift, both scoring high |
| 7.x | **Hallucination Detection** | High positive lift |
| 8.x | Cross-Platform Awareness | High positive lift |

### File Inventory

```
SKILL.md:                          ~272 lines
data/quick-reference.md:           89 lines (~1.2K tokens)
references/api-features.md:       662 lines
references/agent-capabilities.md:  493 lines
references/claude-code-specifics.md: 542 lines
references/tool-types.md:         467 lines
references/model-specifics.md:    309 lines
Total skill content:               ~2,834 lines

Plugin components:                 4 files (plugin.json, marketplace.json, hooks.json, inject-capabilities.sh)
Eval tests:                        43 (8 categories)
Eval trigger set:                  20 queries (evals/eval-set-description-triggers.json)
Knowledge-base:                    28 source files (last refreshed 2026-03-09)
Pipeline:                          8 Python files + shell wrapper (on disk, gitignored)
```

### Description Optimization Status

The skill-creator `run_loop.py` was running with our 20-query eval set. Check for output in:
- `evals/description-optimization-results/`
- The agent's output (may need to check task history)

Two candidate patterns emerged during optimization:
- **Pattern A**: "Use when users ask about current Claude capabilities..." (~480 chars)
- **Pattern B**: "Use when users need to make implementation decisions..." (~450 chars)

Both remove the "MANDATORY TRIGGERS" anti-pattern. Apply whichever scored highest on the trigger eval set.

### Available Quality Tools

- **skill-creator** (Anthropic): `run_loop.py` for description optimization, eval framework, `generate_review.py` + `viewer.html`
- **plugin-dev** (Anthropic): `skill-reviewer` agent, `plugin-validator` agent
- **superpowers** (Jesse Vincent): `writing-skills` (TDD-based skill authoring)
- **superpowers-developing-for-claude-code**: Plugin ecosystem reference docs
- **claude-session-driver**: Orchestrate parallel eval runs via tmux
