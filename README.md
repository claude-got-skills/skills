# Claude Capabilities Awareness Skill

A skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that gives Claude accurate, post-training knowledge about its own capabilities, API features, extension patterns, and model specifics.

## Why this skill exists

Claude's training data has a cutoff. New features — adaptive thinking, the memory tool, agent teams, the skills ecosystem, MCP connectors, and more — ship faster than training data updates. Without this skill, Claude may give outdated or vague answers about what it can do.

With this skill loaded, Claude can accurately answer questions like "Can Claude remember things between conversations?", recommend the right model for a workload, suggest when to build a skill vs a hook vs a plugin, and cite specific API headers and parameters.

## What it covers

- **Current models**: Opus 4.6, Sonnet 4.5, Haiku 4.5, Opus 4.5 — context windows, output limits, thinking modes, effort levels
- **Thinking & reasoning**: Adaptive thinking, effort parameter, 128K output tokens
- **Context & memory**: 1M context window, compaction API, memory tool, prompt caching
- **Tools & integration**: Tool search, MCP connector, programmatic tool calling, computer use, code execution
- **Structured outputs**: Guaranteed JSON schema conformance, Files API, citations
- **Agent capabilities**: Agent SDK, subagents, hooks, plugins, MCP apps, agent teams
- **Extension patterns**: When to use CLAUDE.md vs skills vs hooks vs plugins vs MCP — with decision matrix
- **Architecture patterns**: Subagents vs tool chaining, batch vs streaming, model tiering, multi-agent coordination
- **Breaking changes**: Opus 4.6 prefill removal, budget_tokens deprecation, output_format migration

Reference files provide deeper detail with code examples for API features, tool types, agent capabilities, model specifics, and Claude Code specifics.

## Installation

```bash
npx skills add claude-got-skills/skills@claude-capabilities
```

Or add manually to your Claude Code skills directory.

## Eval results

### API eval (v1.3.0, Haiku 4.5, no web search)

The skill was evaluated against a baseline (no skill context) across 22 test prompts in 7 categories using the Claude API with Haiku 4.5 (no web search access).

#### Keyword accuracy lift (Control → Treatment)

| Category | Control | Treatment | Lift |
|----------|---------|-----------|------|
| Architecture Decisions | 1.33 | 4.33 | **+225%** |
| Can Claude Do X | 2.0 | 4.67 | **+134%** |
| Implementation Guidance | 2.0 | 5.67 | **+184%** |
| Model Selection | 1.0 | 4.0 | **+300%** |
| Extension Awareness | 1.8 | 4.6 | **+156%** |
| Hallucination Detection | 1.5 | 2.75 | **+83%** |
| **Negative (regression check)** | **5.0** | **4.67** | **-7% (negligible)** |

The LLM judge (Haiku 4.5 with SKILL.md rubric) confirmed treatment responses as more accurate and actionable across all positive categories. In hallucination test 7.1 (browser cookie access), the control response contained a hallucinated claim that was absent from the treatment response.

### Browser eval (v1.4.0, Opus 4.6 on Claude.ai, with web search)

Five prompts tested on Claude.ai with skill OFF (control) then ON (treatment). This tests real-world conditions where Claude has web search and stronger built-in product knowledge.

| Prompt | Skill Triggered | Quality Δ |
|--------|----------------|-----------|
| Document processing pipeline (API) | YES | Similar — marginal lift |
| Extended vs adaptive thinking | YES | Similar — slightly more concise |
| Model selection for chatbot | YES | Similar — more specific pricing |
| Code review checklist in Claude Code | YES (explicit) | **Treatment notably better** |
| Cross-conversation memory | UNCLEAR | Similar — more personalized |

**Key finding:** The skill's unique value is strongest for **Claude Code extension patterns** (skills, hooks, plugins, CLAUDE.md) where web search alone doesn't surface structured, actionable guidance. For API and model questions, Claude.ai's web search already gives strong answers — the skill adds marginal improvements.

**Decision: Standalone skill (not plugin).** On-demand loading is sufficient. The skill triggers reliably (4/5 confirmed) and doesn't need autoInvoke, hooks, or slash commands. Token-efficient at ~4,100 tokens loaded only when relevant.

Full analysis: [`docs/browser-test-analysis.md`](docs/browser-test-analysis.md)

## Token cost

SKILL.md is ~4,100 tokens. It loads once per session when invoked. Reference files load on-demand only when Claude needs deeper detail.

## Structure

```
├── .claude-plugin/
│   └── marketplace.json              # Skill discovery for npx skills add
├── skills/
│   └── claude-capabilities/
│       ├── SKILL.md                  # Always-loaded skill (~297 lines, ~4,100 tokens)
│       └── references/
│           ├── agent-capabilities.md # Agent SDK, subagents, hooks, plugins
│           ├── api-features.md       # API parameters, headers, code examples
│           ├── claude-code-specifics.md
│           ├── model-specifics.md    # Pricing, feature matrices, migration guides
│           └── tool-types.md         # Built-in tools, tool definitions, examples
├── evals/                            # Automated eval runner + results
│   ├── eval_runner.py                # Control/treatment eval with LLM judge
│   └── eval-results-*.json           # Timestamped eval runs (gitignored)
├── docs/                             # Design docs, analysis, test results
├── knowledge-base/                   # Source docs from Anthropic documentation
└── monitoring/                       # Freshness checks and update tracking
```

## License

MIT
