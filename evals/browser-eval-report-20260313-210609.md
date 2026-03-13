# Browser Eval Report: Claude.ai A/B Testing

**Generated:** 2026-03-13 21:06
**Eval run:** 2026-03-13T21:05:43Z
**Platform:** claude.ai
**Prompts tested:** 5

> **Note:** n=5 is a qualitative assessment for directional insight,
> not a statistically significant comparison. Results should be
> interpreted as indicative, not conclusive.

## Summary

| Prompt | Category | Skill Triggered? | Web Search (C/T) | Status |
|--------|----------|-------------------|-------------------|--------|
| P1 | Vision / PDF
 | NO | N / N | OK |
| P2 | API Features
 | NO | N / N | OK |
| P3 | Model Selection
 | NO | N / N | OK |
| P4 | Platform Comparison
 | NO | N / N | OK |
| P5 | Product Capabilities
 | NO | N / N | OK |

**Skill trigger rate:** 0/5 treatment prompts

## Per-Prompt Analysis

### P1: Vision / PDF


**Prompt:** Vision / PDF


**Skill trigger:** Not detected in thinking text

| | Control | Treatment |
|---|---------|-----------|
| Status | ok | ok |
| Web search | No | No |
| Response (excerpt) | "Marshaled official documentation to address API integration query\nMarshaled official documentation to address API integration query\n\nHere's a complete rundown based on the official API docs.\n\nImages\n\nSupported formats: JPEG, PNG, GIF, WebP.\n\nLimits:\n\nUp to 100 images per API request (but... | "Marshaled technical documentation to address API integration query\nMarshaled technical documentation to address API integration query\n\nHere's everything you need to know for your use case:\n\nImage Support\n\nFormats: JPEG, PNG, GIF, WebP — all natively supported across all current models.\n\nSe... |

Response lengths are comparable.

### P2: API Features


**Prompt:** API Features


**Skill trigger:** Not detected in thinking text

| | Control | Treatment |
|---|---------|-----------|
| Status | ok | ok |
| Web search | No | No |
| Response (excerpt) | "Synthesized comprehensive information to clarify key distinctions\nSynthesized comprehensive information to clarify key distinctions\n\nGood question — the distinction has sharpened significantly with the Claude 4.6 release. Here's a practical breakdown:\n\nExtended Thinking (manual mode)\n\nYou en... | "Crystallized distinction between extended and adaptive thinking approaches\nCrystallized distinction between extended and adaptive thinking approaches\n\nGood question — these are genuinely different things, and the naming can be confusing. Here's the breakdown:\n\nExtended thinking is the original... |

Response lengths are comparable.

### P3: Model Selection


**Prompt:** Model Selection


**Skill trigger:** Not detected in thinking text

| | Control | Treatment |
|---|---------|-----------|
| Status | ok | ok |
| Web search | No | No |
| Response (excerpt) | "Evaluated model options against speed, cost, and accuracy criteria\nEvaluated model options against speed, cost, and accuracy criteria\n\nFor a customer support chatbot, Claude Haiku 4.5 (claude-haiku-4-5-20251001) is the clear pick. Here's why it fits all three criteria:\n\nSpeed: Haiku 4.5 runs u... | "Evaluated model options and identified optimal solution\nEvaluated model options and identified optimal solution\n\nClaude Haiku 4.5 (claude-haiku-4-5-20251001) is the clear recommendation for your use case.\n\nHere's why it ticks all three boxes:\n\nFast — Haiku 4.5 runs up to 4–5× faster than Son... |

Response lengths are comparable.

### P4: Platform Comparison


**Prompt:** Platform Comparison


**Skill trigger:** Not detected in thinking text

| | Control | Treatment |
|---|---------|-----------|
| Status | ok | ok |
| Web search | No | No |
| Response (excerpt) | "Consulted documentation to synthesize platform-specific implementation guidance\nConsulted documentation to synthesize platform-specific implementation guidance\n\nGood news — the core skill format (a SKILL.md with YAML frontmatter + markdown instructions) is the same across all three surfaces. The... | "Synthesized platform differences for skill portability\nSynthesized platform differences for skill portability\n\nGood question — the skills standard is cross-platform, but the installation method and some behaviours differ. Here's what you need to know:\n\nWhat transfers directly\n\nThe skill cont... |

Response lengths are comparable.

### P5: Product Capabilities


**Prompt:** Product Capabilities


**Skill trigger:** Not detected in thinking text

| | Control | Treatment |
|---|---------|-----------|
| Status | ok | ok |
| Web search | No | No |
| Response (excerpt) | "Examined Claude's cross-conversation memory limitations\nExamined Claude's cross-conversation memory limitations\n\nYes, to a degree — though it works differently from how a person remembers things.\n\nClaude has a memory system that generates summaries from past conversations and stores key facts.... | "Examined Claude's cross-conversation memory limitations\nExamined Claude's cross-conversation memory limitations\n\nYes, to a degree — but with some important nuances worth knowing:\n\nWhat I can remember: Claude.ai has a memory system that derives key facts from past conversations and stores them ... |

Response lengths are comparable.

## Thinking Text Excerpts

Raw thinking text excerpts for manual review of trigger detection accuracy.

### P1 Thinking

**Treatment thinking (excerpt):**
```
""

```

**Control thinking (excerpt):**
```
""

```

### P2 Thinking

**Treatment thinking (excerpt):**
```
[20:55:23]   Found thinking panel toggle: e12
[32m✓[0m Done
""

```

**Control thinking (excerpt):**
```
[20:37:00]   Found thinking panel toggle: e12
[32m✓[0m Done
""

```

### P3 Thinking

**Treatment thinking (excerpt):**
```
""

```

**Control thinking (excerpt):**
```
""

```

### P4 Thinking

**Treatment thinking (excerpt):**
```
""

```

**Control thinking (excerpt):**
```
""

```

### P5 Thinking

**Treatment thinking (excerpt):**
```
""

```

**Control thinking (excerpt):**
```
""

```

## Methodology

- **Tool:** agent-browser (automated headless browser)
- **Platform:** Claude.ai web interface
- **Design:** Within-subject A/B (same prompts, skill OFF then ON)
- **Skill toggle:** Manual (user toggles between control/treatment phases)
- **Detection:** Skill triggering inferred from thinking panel keywords;
  web search inferred from thinking panel text. Both are heuristic-based.
- **Limitations:** n=5 prompts, qualitative assessment, potential confounds
  from time gap between conditions and DOM extraction reliability.
