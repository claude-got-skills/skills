# Session 8 Handoff: Repo Restructured, Content Updated, Specs Ready for Implementation

## Project Context

We are building and maintaining Claude Code skills under the **claude-got-skills** GitHub account. The first skill — **Claude Capabilities Awareness** — gives Claude accurate post-training knowledge about its capabilities, API features, extension patterns, and model specifics.

**GitHub repo**: https://github.com/claude-got-skills/skills (renamed from `claude-capabilities` in this session)
**Skill status**: Content updated to v1.6.0-dev on `dev` branch. Main branch has v1.5.0 (mono-repo restructure).
**Local folder**: `/Users/liamj/Documents/development/claude-got-skills/claude-capabilities/` — this is the git repo root.

---

## Session 7→8 Completed Work

### 1. Repo Restructure ✅

- **Renamed** from `claude-capabilities` to `skills` on GitHub
- **Restructured** to mono-repo pattern (matching Anthropic/Vercel conventions):
  - Skills live in `skills/<skill-name>/` with own SKILL.md + references
  - `.claude-plugin/marketplace.json` for skill discovery
  - Install: `npx skills add claude-got-skills/skills@claude-capabilities`
- **Deleted** redundant `skill-published/` and `skill-unpublished/` directories
- **Fixed** git lock files (stale since Feb 11)
- **Created** `main` and `dev` branches, both pushed to GitHub
- **Committed** as v1.5.0 on main, pushed

### 2. Content Freshness Update ✅

Scraped current Anthropic docs (Firecrawl + Gmail Anthropic Alerts analysis) and identified **16 changes** since Feb 11. Applied critical and high-priority updates:

- **Added Sonnet 4.6** — adaptive thinking, $3/$15, 64K output, 1M context beta
- **Fixed Opus 4.6 pricing** — $5/$25 (was incorrectly $15/$75)
- **Fixed Haiku 4.5** — now supports extended thinking, pricing corrected to $1/$5
- **Marked Sonnet 4.5 and Opus 4.5 as legacy**
- **Promoted to GA**: tool search, code execution, web fetch, web search, memory tool, programmatic tool calling
- **Added**: dynamic filtering, automatic caching, fast mode (research preview)
- **Added model retirements**: Sonnet 3.7, Haiku 3.5

Full diff report: `docs/freshness-diff-report.md`
Content updates committed on `dev` branch (not yet merged to main).

### 3. Implementation Specs Written ✅

Two detailed specs ready for implementation:

| Spec | Path | Summary |
|------|------|---------|
| **Browser Eval** | `docs/specs/browser-eval-spec.md` | Automated agent-browser script for A/B testing on Claude.ai |
| **Freshness Pipeline** | `docs/specs/freshness-pipeline-spec.md` | Distill replacement — self-hosted Python pipeline with launchd scheduling |

Both specs have been reviewed by separate agents (findings appended below).

### 4. Research Completed ✅

| Research Area | Key Finding |
|---|---|
| **Skill-creator plugin** | Has eval infrastructure (trigger accuracy, blind A/B, description optimization). Trigger eval not suited for self-referential skills (0% trigger rate because Claude answers from training). |
| **Superpowers plugin** | No eval infrastructure. Useful `update_docs.js` pattern for doc freshness. |
| **IMS repo** (`/Users/liamj/Documents/development/ims/`) | 9 ingestion pipelines, launchd scheduling, SHA-256 change detection, Supabase storage. Highly reusable for freshness pipeline. |
| **Agent-browser vs Playwright** | Agent-browser wins: state persistence, named sessions, scriptable bash. Use for Claude.ai testing. |
| **Gmail Anthropic Alerts** | 41 alerts in 24 days (~1.7/day). Distill hit free tier email limit Feb 21. |
| **Skills.sh conventions** | Both Anthropic and Vercel use mono-repos. `npx skills add owner/repo@skill-name` for individual install. |

### 5. Memory Files Updated ✅

- `/Users/liamj/.claude/projects/-Users-liamj-Documents-development-claude-got-skills/memory/MEMORY.md`
- `/Users/liamj/.claude/projects/-Users-liamj-Documents-development-claude-got-skills/memory/research-findings.md`

---

## Current Git State

```
Branch: dev (ahead of main by 2 commits)
Remote: https://github.com/claude-got-skills/skills.git

Commit history:
ea9c3d0 (dev) Update skill content: Sonnet 4.6, GA promotions, pricing corrections
a173fb6 Add implementation specs and freshness diff report
ccd5d4a (main) v1.5.0: Mono-repo restructure, add development infrastructure
2921d11 v1.4.0: Condense SKILL.md, add architecture patterns, deduplicate refs
3e16b7f v1.3.0: Claude capabilities awareness skill
```

### What's on dev but NOT on main:
- Content freshness updates (Sonnet 4.6, GA promotions, pricing fixes)
- Implementation specs (browser eval, freshness pipeline)
- Freshness diff report
- Updated .gitignore

### Merge strategy:
After running evals to confirm no regression → merge dev to main → tag v1.6.0

---

## Session 8 Priority Order

### 1. Run Evals to Validate Content Updates (~30 min)

The content was updated but not eval'd. Run:

```bash
cd /Users/liamj/Documents/development/claude-got-skills/claude-capabilities
python evals/eval_runner.py --runs 1
```

Check for:
- No regression on existing categories
- Improved scores on model selection (Sonnet 4.6 now included)
- Verify GA promotions improve "Implementation Guidance" scores

If clean → merge dev to main, tag v1.6.0, push.

### 2. Remaining Content Updates (~1-2 hrs)

The diff report identified items not yet addressed:
- **tool-types.md**: Update status fields for GA-promoted tools (tool search, code execution, web fetch, memory, programmatic tool calling)
- **api-features.md**: Update memory tool from beta to GA, add automatic caching section
- **knowledge-base/ files**: Update source docs to match current state
- Scrape missing details: Sonnet 4.6 full specs page, fast mode API shape, dynamic filtering config

### 3. Build Freshness Pipeline (~6-7 hrs)

Implement from `docs/specs/freshness-pipeline-spec.md`:

```
pipeline/
├── config.py          # Source URL registry (13 sources)
├── scrape.py          # trafilatura + Jina Reader extraction
├── detect.py          # SHA-256 change detection
├── diff.py            # Unified diff generation
├── report.py          # Markdown change reports
├── notify.py          # macOS notifications
├── freshness_check.py # Main orchestrator
└── run-freshness-check.sh  # Launchd wrapper
```

Dependencies: `pip install trafilatura requests`
Schedule: launchd plist, twice daily (09:00, 21:00)

### 4. Build Browser Eval Script (~3-4 hrs)

Implement from `docs/specs/browser-eval-spec.md`:

```
evals/
├── browser_eval.sh         # Bash orchestration with agent-browser
└── browser_eval_report.py  # Python report generator
```

First-time: `./evals/browser_eval.sh --auth` (headed browser for Claude.ai 2FA)
Full run: `./evals/browser_eval.sh` (control + treatment with manual skill toggle)

### 5. Description Optimization (~30 min)

The skill-creator eval found 0% trigger rate (expected for self-referential skills). Consider reframing description to emphasize "post-training corrections" and "outdated training data":

```yaml
description: Use when answering questions about Claude's capabilities where training data may be outdated — this skill contains POST-TRAINING updates including new models, GA promotions, breaking changes, and deprecated features that correct stale information...
```

### 6. Merge and Release

After evals pass:
```bash
git checkout main
git merge dev
git tag v1.6.0
git push origin main v1.6.0
```

---

## Key Technical Context

### Environment

- **API key**: ANTHROPIC_API_KEY in `.env` at repo root (gitignored)
- **Python**: eval_runner.py needs `anthropic` package
- **agent-browser**: v0.13.0 installed at `/Users/liamj/.agents/skills/agent-browser/`
- **Firecrawl**: Available as MCP tool for ad-hoc scraping
- **Gmail**: Anthropic Alerts label accessible via Gmail MCP (label ID: `Label_935583694514506464`)

### Frontmatter Constraints (Claude.ai capabilities page)

- No YAML block scalars (`>`, `|`)
- No colons in description
- "Claude" reserved in `name` field — use `assistant-capabilities`
- Only allowed keys: name, description, license, allowed-tools, compatibility, metadata

### Eval Infrastructure

| Runner | Use |
|--------|-----|
| `evals/eval_runner.py` | Content quality (API-based, keyword + LLM judge, control vs treatment) |
| Skill-creator `run_eval.py` | Trigger accuracy (tests if skill fires — not suited for self-referential skills) |
| Skill-creator `run_loop.py` | Description optimization (train/test split, automated improvement) |
| `evals/browser_eval.sh` | Claude.ai browser testing (to be built from spec) |

### IMS Repo Patterns (for freshness pipeline)

Located at `/Users/liamj/Documents/development/ims/`:
- `ims_pipeline/extract.py` — trafilatura + Jina Reader (reuse for scraping)
- `tana_sync.py` — SHA-256 change detection (reuse for diffing)
- `launchd/*.plist` + `scripts/run-*.sh` — scheduling pattern
- `monitor_pipelines.py` — macOS notifications

### Skills.sh Install Path

After repo rename, the install command is:
```bash
npx skills add claude-got-skills/skills@claude-capabilities
```

The marketplace.json at `.claude-plugin/marketplace.json` enables `npx skills add claude-got-skills/skills` to discover all skills in the repo.

---

## Spec Review Findings

### Browser Eval Spec Review

(To be appended when review agent completes — check if `docs/specs/browser-eval-spec.md` has been updated with review notes, or check memory files.)

### Freshness Pipeline Spec Review

(To be appended when review agent completes — check if `docs/specs/freshness-pipeline-spec.md` has been updated with review notes, or check memory files.)

---

## File Inventory

### Git-tracked (current dev branch)

```
.claude-plugin/marketplace.json    # Skill discovery
.gitignore                         # Comprehensive
LICENSE                            # MIT
README.md                          # Updated install path and structure
skills/claude-capabilities/SKILL.md       # v1.6.0-dev (updated content)
skills/claude-capabilities/references/    # 5 reference files (model-specifics updated)
evals/eval_runner.py               # Canonical eval runner
evals/capabilities-skill-eval.py   # Supplementary eval runner
evals/eval-report-*.md             # 14 historical eval reports
evals/v1.4.0-eval-report.md        # Combined Haiku+Sonnet report
docs/specs/browser-eval-spec.md    # Implementation spec
docs/specs/freshness-pipeline-spec.md  # Implementation spec
docs/freshness-diff-report.md      # 16 changes identified
docs/browser-test-analysis.md      # Session 7 manual browser test
docs/continuation-prompts/         # Session handoffs (1-8)
docs/design/                       # Design docs
docs/analysis/                     # Eval analysis
knowledge-base/                    # 28 Anthropic doc source files
monitoring/                        # Distill setup (being replaced by pipeline)
```

### Untracked / gitignored

```
.env                              # API key
.firecrawl/                       # Scraped doc cache
eval-set-trigger.json             # Skill-creator eval artifacts
eval-trigger-output.txt           # Skill-creator eval output
```
