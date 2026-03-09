# Freshness Diff Report (ARCHIVED)

**Generated:** 2026-03-07
**Archived:** 2026-03-09 (v2.0.0 release)
**Skill last updated:** 2026-02-11
**Comparison window:** 2026-02-11 to 2026-03-07

> **Resolution status:** 14/16 items resolved in v2.0.0.
> - Item 14 (1M context tier requirement): Unverified — currently says "tier 3+" in api-features.md. Needs official confirmation.
> - Item 16 (KB file refresh): Pending — 28 knowledge-base source files need re-scraping. Tracked as separate work item.

Sources scraped:
- API Release Notes: https://platform.claude.com/docs/en/release-notes/overview
- API Overview: https://platform.claude.com/docs/en/overview
- Claude Code docs index: https://docs.claude.com/en/docs

Files compared:
- `knowledge-base/claude-capabilities-features-overview.md`
- `knowledge-base/claude-capabilities-new-in-opus-4-6.md`
- `knowledge-base/claude-capabilities-programmatic-tool-calling.md`
- `knowledge-base/claude-capabilities-context-windows.md`
- `knowledge-base/claude-capabilities-structured-outputs.md`
- `SKILL.md` and all `references/*.md` files

---

## 1. NEW MODEL: Claude Sonnet 4.6

**Category:** New Model
**Priority:** Critical
**Date:** February 17, 2026

Claude Sonnet 4.6 has been released. It is described as the "latest balanced model combining speed and intelligence for everyday tasks" with "improved agentic search performance while consuming fewer tokens." It supports extended thinking and 1M token context window (beta).

**What our skill currently says:**
- SKILL.md `Current Models` section lists Opus 4.6, Sonnet 4.5, Haiku 4.5, Opus 4.5 -- Sonnet 4.6 is completely absent
- `references/model-specifics.md` Model Overview table has no entry for Sonnet 4.6
- Capability Matrix, Model IDs, Pricing, and all per-model tables are missing Sonnet 4.6

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Current Models | Add Sonnet 4.6 with key specs |
| `references/model-specifics.md` | Model Overview | Add Sonnet 4.6 row |
| `references/model-specifics.md` | Capability Matrix | Add Sonnet 4.6 column |
| `references/model-specifics.md` | Model IDs and Aliases | Add Sonnet 4.6 IDs |
| `references/model-specifics.md` | Pricing | Add Sonnet 4.6 pricing (TBD - need to scrape pricing page) |
| `references/model-specifics.md` | Thinking Capabilities | Add Sonnet 4.6 row |
| `references/model-specifics.md` | Model Selection Guidance | Update recommendations |
| `knowledge-base/claude-capabilities-features-overview.md` | Context window table | Update to include Sonnet 4.6 |
| `knowledge-base/claude-capabilities-context-windows.md` | 1M context section | Add Sonnet 4.6 to supported models list |

---

## 2. GA PROMOTION: Web Search Tool

**Category:** GA Promotion
**Priority:** Critical
**Date:** February 17, 2026

Web search tool is now generally available (no beta header required).

**What our skill currently says:**
- `references/tool-types.md` already shows Web Search as `Status: GA` -- this appears correct
- `knowledge-base/claude-capabilities-features-overview.md` shows web search with mixed availability (GA on Claude API, Vertex, Azure; missing Bedrock note)
- SKILL.md Tools section does not explicitly mark web search as beta or GA

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `knowledge-base/claude-capabilities-features-overview.md` | Tools table | Verify web search availability is current |

**Status:** Already mostly correct in our files. Low-impact update.

---

## 3. GA PROMOTION: Programmatic Tool Calling

**Category:** GA Promotion
**Priority:** Critical
**Date:** February 17, 2026

Programmatic tool calling is now GA -- no beta header required.

**What our skill currently says:**
- SKILL.md says: "Programmatic tool calling (beta, `advanced-tool-use-2025-11-20`)"
- `references/tool-types.md` says: `Status: Beta | Header: advanced-tool-use-2025-11-20`
- `knowledge-base/claude-capabilities-programmatic-tool-calling.md` says: "Programmatic tool calling is currently in public beta. To use this feature, add the `advanced-tool-use-2025-11-20` beta header"
- The knowledge-base doc lists model compatibility as Opus 4.5 and Sonnet 4.5 only

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Tools & Integration | Change "(beta, `advanced-tool-use-2025-11-20`)" to "(GA)" |
| `references/tool-types.md` | Programmatic Tool Calling | Change Status to GA, remove Header requirement |
| `references/tool-types.md` | Tool Compatibility Matrix | Update if needed |
| `references/model-specifics.md` | Beta Features table | Move to GA Features list |
| `knowledge-base/claude-capabilities-programmatic-tool-calling.md` | Top-level note | Remove beta note and header requirement |
| `references/model-specifics.md` | Feature Availability | Check if Sonnet 4.6 or Opus 4.6 now support PTC |

**Note:** Need to verify whether Sonnet 4.6 and/or Opus 4.6 support programmatic tool calling now that it's GA.

---

## 4. GA PROMOTION: Code Execution Tool

**Category:** GA Promotion
**Priority:** High
**Date:** February 17, 2026

Code execution tool is now GA (no beta header required).

**What our skill currently says:**
- `references/tool-types.md` says: `Status: Beta | Header: code-execution-2025-08-25`
- `knowledge-base/claude-capabilities-features-overview.md` shows code execution with `claudeApiBeta` and `azureAiBeta` availability

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `references/tool-types.md` | Code Execution | Change Status to GA, remove Header |
| `knowledge-base/claude-capabilities-features-overview.md` | Tools table | Update code execution availability to GA |
| `references/model-specifics.md` | Beta Features table | Move code execution to GA list |
| `references/agent-capabilities.md` | Agent Skills | Update beta headers for skills (may still need `skills-2025-10-02` but not `code-execution-2025-08-25`) |

---

## 5. GA PROMOTION: Web Fetch Tool

**Category:** GA Promotion
**Priority:** High
**Date:** February 17, 2026

Web fetch tool is now GA (no beta header required).

**What our skill currently says:**
- `references/tool-types.md` says: `Status: Beta | Header: Required`
- `knowledge-base/claude-capabilities-features-overview.md` shows web fetch with `claudeApiBeta` and `azureAiBeta`

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `references/tool-types.md` | Web Fetch | Change Status to GA, remove Header |
| `knowledge-base/claude-capabilities-features-overview.md` | Tools table | Update web fetch availability to GA |

---

## 6. GA PROMOTION: Tool Search Tool

**Category:** GA Promotion
**Priority:** High
**Date:** February 17, 2026

Tool search tool is now GA (no beta header required).

**What our skill currently says:**
- SKILL.md says: "Tool Search (beta)"
- `references/tool-types.md` says: `Status: Beta | Models: Sonnet 4+, Opus 4+`
- `knowledge-base/claude-capabilities-features-overview.md` shows tool search with mixed beta availability

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Tools & Integration | Change "Tool Search (beta)" to "Tool Search (GA)" |
| `references/tool-types.md` | Tool Search | Change Status to GA |
| `knowledge-base/claude-capabilities-features-overview.md` | Tools table | Update to GA availability |

---

## 7. GA PROMOTION: Tool Use Examples

**Category:** GA Promotion
**Priority:** Medium
**Date:** February 17, 2026

Tool use examples are now GA (no beta header required).

**What our skill currently says:**
- `references/tool-types.md` says: `Tool Use Examples (Beta)` with header `advanced-tool-use-2025-11-20`
- `references/claude-code-specifics.md` says: "Tool Use Examples (Beta)" with beta headers

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `references/tool-types.md` | Tool Use Examples | Change to GA, remove header requirement |
| `references/claude-code-specifics.md` | Tool Use Best Practices | Update header references |

---

## 8. GA PROMOTION: Memory Tool

**Category:** GA Promotion
**Priority:** High
**Date:** February 17, 2026

Memory tool is now GA (no beta header required).

**What our skill currently says:**
- SKILL.md says: "Memory tool (beta, `memory_20250818`, cross-conversation persistence)"
- `references/tool-types.md` says: `Status: Beta | Header: context-management-2025-06-27`
- `references/api-features.md` says: `Status: Beta | Header: context-management-2025-06-27`
- `knowledge-base/claude-capabilities-features-overview.md` shows memory with mixed beta availability

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Context & Memory | Change "Memory tool (beta, ...)" to "Memory tool (GA)" |
| `references/tool-types.md` | Memory Tool | Change Status to GA, remove Header requirement |
| `references/api-features.md` | Memory Tool | Change Status to GA, remove Header requirement |
| `references/model-specifics.md` | Beta Features table | Move memory tool to GA list |
| `knowledge-base/claude-capabilities-features-overview.md` | Tools table | Update memory availability to GA |

---

## 9. NEW FEATURE: Automatic Caching

**Category:** New Feature
**Priority:** High
**Date:** February 19, 2026

New "automatic caching" for the Messages API. Add a single `cache_control` field to the request body and the system automatically caches the last cacheable block, moving the cache point forward as conversations grow. No manual breakpoint management required. Works alongside existing block-level cache control. Available on Claude API and Azure AI Foundry (preview).

**What our skill currently says:**
- SKILL.md mentions: "Prompt caching (5-min and 1-hour)"
- `references/api-features.md` Prompt Caching section describes manual `cache_control` on individual blocks
- No mention of automatic caching anywhere

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Context & Memory | Add mention of automatic caching |
| `references/api-features.md` | Prompt Caching | Add automatic caching mode description |

---

## 10. NEW FEATURE: Dynamic Filtering (Web Search/Fetch)

**Category:** New Feature
**Priority:** High
**Date:** February 17, 2026

Web search and web fetch now support "dynamic filtering" which uses code execution to filter results before they reach the context window, for better performance and reduced token cost. Available with Opus 4.6 and Sonnet 4.6.

**What our skill currently says:**
- No mention of dynamic filtering anywhere in the skill or references

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Tools & Integration | Add brief mention of dynamic filtering |
| `references/tool-types.md` | Web Search | Add dynamic filtering section |
| `references/tool-types.md` | Web Fetch | Add dynamic filtering mention |

---

## 11. NEW FEATURE: Code Execution Free with Web Search/Fetch

**Category:** New Feature
**Priority:** Medium
**Date:** February 17, 2026

API code execution is now free when used in combination with web search or web fetch. Standalone usage has separate pricing.

**What our skill currently says:**
- No mention of this pricing change

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `references/tool-types.md` | Code Execution | Add pricing note about free usage with web search/fetch |

---

## 12. NEW FEATURE: Fast Mode (Research Preview)

**Category:** New Feature
**Priority:** Medium
**Date:** February 7, 2026

Fast mode in research preview for Opus 4.6. Up to 2.5x faster output token generation via the `speed` parameter at premium pricing. Waitlist-gated.

**What our skill currently says:**
- No mention of fast mode anywhere

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `references/api-features.md` | New section | Add Fast Mode section |
| `references/model-specifics.md` | Opus 4.6 specifics | Add fast mode note |
| `SKILL.md` | Thinking & Reasoning or Platform | Brief mention of fast mode (research preview) |

---

## 13. MODEL DEPRECATION: Sonnet 3.7 and Haiku 3.5 Retired

**Category:** Model Change / Deprecation
**Priority:** Medium
**Date:** February 19, 2026

Claude Sonnet 3.7 (`claude-3-7-sonnet-20250219`) and Claude Haiku 3.5 (`claude-3-5-haiku-20241022`) have been retired. All requests now return errors. Claude Haiku 3 (`claude-3-haiku-20240307`) deprecated with retirement scheduled April 19, 2026.

**What our skill currently says:**
- `references/model-specifics.md` mentions Sonnet 3.7 in computer use versions table
- `knowledge-base/claude-capabilities-context-windows.md` mentions "Sonnet 3.7 does not support interleaved thinking"

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `references/model-specifics.md` | Migration Guides | Note Sonnet 3.7 and Haiku 3.5 are retired |
| `references/model-specifics.md` | Computer Use Versions | Update Sonnet 3.7 reference (model now retired) |
| `knowledge-base/claude-capabilities-context-windows.md` | Interleaved thinking note | Remove or update Sonnet 3.7 reference |

---

## 14. SKILL.MD ACCURACY: 1M Context Tier Requirement

**Category:** Correction
**Priority:** Low
**Date:** Pre-existing

SKILL.md says "1M context (beta, all models, tier 3+)" but the knowledge-base doc says "tier 4 and organizations with custom rate limits." The api-features.md reference says "tier 3+."

The release notes from Feb 5, 2026 say "1M token context window is now available in beta for Claude Opus 4.6" but don't specify tier changes. Need to verify which tier requirement is current.

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Context & Memory | Verify and correct tier requirement |

---

## 15. SKILL.MD ACCURACY: Programmatic Tool Calling Model Support

**Category:** Correction
**Priority:** High
**Date:** February 17, 2026

SKILL.md says programmatic tool calling is "Sonnet 4.5 and Opus 4.5 only." With PTC now GA and Sonnet 4.6 released, model support may have expanded. The release notes mention PTC going GA alongside Sonnet 4.6 launch, suggesting Sonnet 4.6 likely supports it. Need to verify Opus 4.6 support.

`references/model-specifics.md` Capability Matrix shows: Opus 4.6 = No, Sonnet 4.5 = Yes, Haiku 4.5 = No, Opus 4.5 = Yes.

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `SKILL.md` | Tools & Integration | Update model list for PTC |
| `references/model-specifics.md` | Capability Matrix | Add Sonnet 4.6 column, verify PTC support |
| `references/tool-types.md` | Programmatic Tool Calling | Update model list |

---

## 16. KNOWLEDGE-BASE: Features Overview Tool Status Drift

**Category:** Correction
**Priority:** Medium
**Date:** February 17, 2026

`knowledge-base/claude-capabilities-features-overview.md` shows many tools with beta availability markers that are now GA:
- Code execution: shows `claudeApiBeta azureAiBeta` -- now GA
- Programmatic tool calling: shows `claudeApiBeta azureAiBeta` -- now GA
- Web fetch: shows `claudeApiBeta azureAiBeta` -- now GA
- Tool search: shows `claudeApiBeta bedrockBeta vertexAiBeta azureAiBeta` -- now GA
- Memory: shows `claudeApiBeta bedrockBeta vertexAiBeta azureAiBeta` -- now GA

**What needs updating:**
| File | Section | Action |
|------|---------|--------|
| `knowledge-base/claude-capabilities-features-overview.md` | Core capabilities table | Update all GA-promoted tools |
| `knowledge-base/claude-capabilities-features-overview.md` | Tools table | Update all GA-promoted tools |

---

## Summary: Priority Update Order

### Critical (must update before next release)
1. **Add Sonnet 4.6 as a model** across SKILL.md, model-specifics.md
2. **Update PTC from beta to GA** across SKILL.md, tool-types.md, model-specifics.md
3. **Update web search from beta to GA** (verify current state)

### High (should update before next release)
4. **Update code execution from beta to GA** across tool-types.md, features-overview.md
5. **Update web fetch from beta to GA** across tool-types.md, features-overview.md
6. **Update tool search from beta to GA** across SKILL.md, tool-types.md
7. **Update memory tool from beta to GA** across SKILL.md, tool-types.md, api-features.md
8. **Add automatic caching** to SKILL.md and api-features.md
9. **Add dynamic filtering** to tool-types.md
10. **Update PTC model support** (likely includes Sonnet 4.6 now)

### Medium (include in next release)
11. **Add fast mode** (research preview) to api-features.md, model-specifics.md
12. **Update tool use examples to GA** in tool-types.md
13. **Add code execution free pricing** with web search/fetch
14. **Update model deprecations** (Sonnet 3.7, Haiku 3.5 retired; Haiku 3 deprecated)

### Low (can wait)
15. **Verify 1M context tier requirement** (tier 3 vs tier 4)
16. **Update knowledge-base source files** to match GA promotions

---

## Items NOT yet verified (need additional scraping)

1. **Claude Code CHANGELOG** -- GitHub returned 429 rate limit error. Need to check for new Claude Code features (e.g., /loop command, scheduled tasks, new CLI flags). Recommend scraping via raw.githubusercontent.com or the GitHub API later.
2. **Sonnet 4.6 pricing** -- Not captured in the release notes. Need to scrape the pricing page.
3. **Sonnet 4.6 full model ID** -- Not captured. Need to scrape the models page.
4. **Whether Opus 4.6 now supports PTC** -- Release notes don't explicitly say. The current model-specifics.md says No. Verify via the programmatic tool calling docs page.
5. **Whether Sonnet 4.6 supports PTC** -- Highly likely given it launched alongside PTC GA, but not explicitly confirmed in the release notes.
6. **Dynamic filtering details** -- The release notes mention it but don't provide configuration details. Need to scrape the web search tool docs page.
7. **Automatic caching configuration** -- Release notes describe it at a high level. Need to scrape the prompt caching docs page for exact API shape.
8. **Fast mode API shape** -- Release notes mention the `speed` parameter but don't provide details. Need to scrape the fast mode docs page.
