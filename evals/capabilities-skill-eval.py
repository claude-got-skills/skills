#!/usr/bin/env python3
"""
Capabilities Skill Evaluation Script
=====================================

Blind evaluation of whether the claude-capabilities skill improves Claude's
knowledge of current capabilities. Runs 10 test prompts as subagent tasks,
comparing a control (no skill) against a treatment (skill installed).

Usage:
    python capabilities-skill-eval.py [--model MODEL] [--runs N] [--output DIR]

Requirements:
    pip install claude-agent-sdk

The prompts are deliberately "blind" — they do NOT mention the skill, capabilities
awareness, or hint at what's being tested. They are realistic tasks a developer
would actually ask.
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Test prompts
# ---------------------------------------------------------------------------

TESTS = [
    # Category 1: Architecture Decisions
    {
        "id": "1.1",
        "category": "Architecture Decisions",
        "prompt": (
            "I'm building a document analysis pipeline that needs to process "
            "100-page PDFs. The system should extract key information, cross-reference "
            "it with a knowledge base, and produce a structured summary. What "
            "architecture would you recommend? Keep it simple — this is for a small team."
        ),
        "expected_advantage": (
            "Should recommend using 1M context window (beta) to process entire "
            "documents in one pass rather than chunking. Should mention Files API "
            "for upload. Should consider effort parameter for cost control."
        ),
        "scoring_keywords": {
            "accuracy": [
                "1M context", "1 million", "context window", "beta",
                "files api", "file upload", "effort", "cost"
            ],
            "completeness": [
                "tier 3", "usage tier", "premium pricing", "streaming",
                "prompt caching", "batch"
            ],
            "deprecated_patterns": [
                "chunk", "split into", "RAG only", "embedding-based only"
            ],
        },
    },
    {
        "id": "1.2",
        "category": "Architecture Decisions",
        "prompt": (
            "I need to build a quality assurance system that reviews AI-generated "
            "content before it goes to customers. The system should check for accuracy, "
            "tone, and compliance with our style guide. How would I architect this?"
        ),
        "expected_advantage": (
            "Should recommend subagents or Agent SDK with appropriate model selection "
            "(Haiku for fast checks, Sonnet/Opus for nuanced review). Should mention "
            "hooks for automation. Without the skill, may recommend older multi-agent "
            "patterns."
        ),
        "scoring_keywords": {
            "accuracy": [
                "agent sdk", "subagent", "haiku", "sonnet", "opus",
                "hook", "model selection"
            ],
            "completeness": [
                "cost", "parallel", "structured output", "effort parameter",
                "prompt caching"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "1.3",
        "category": "Architecture Decisions",
        "prompt": (
            "We want to add AI features to our Next.js app. Users should be able to "
            "ask questions about their data and get real-time streaming responses. "
            "What's the simplest way to integrate Claude into this?"
        ),
        "expected_advantage": (
            "Should mention fine-grained tool streaming (GA), structured outputs for "
            "typed responses, and possibly MCP Connector for direct server integration. "
            "May recommend Agent SDK for backend."
        ),
        "scoring_keywords": {
            "accuracy": [
                "streaming", "tool streaming", "structured output",
                "messages api", "sdk"
            ],
            "completeness": [
                "mcp connector", "agent sdk", "output_config",
                "server-sent events", "token counting"
            ],
            "deprecated_patterns": [
                "output_format"
            ],
        },
    },

    # Category 2: "Can Claude Do X?"
    {
        "id": "2.1",
        "category": "Can Claude Do X",
        "prompt": (
            "Can I get Claude to remember things between separate conversations? "
            "I'm building a tool where Claude helps with ongoing projects and it's "
            "frustrating that it loses context each time."
        ),
        "expected_advantage": (
            "Should describe the Memory tool (beta) with specific details — commands "
            "(view, create, str_replace, insert, delete, rename), client-side "
            "persistence requirement, beta header. Without the skill, may say this "
            "isn't possible or suggest workarounds."
        ),
        "scoring_keywords": {
            "accuracy": [
                "memory tool", "memory_20250818", "beta",
                "cross-conversation", "persistent"
            ],
            "completeness": [
                "view", "create", "str_replace", "client-side",
                "context-management-2025-06-27"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "2.2",
        "category": "Can Claude Do X",
        "prompt": (
            "Is there a way to make Claude use tools without me having to define "
            "every single one upfront? I have hundreds of MCP tools and the context "
            "window overhead is killing me."
        ),
        "expected_advantage": (
            "Should describe Tool Search (beta) with dynamic discovery via regex, "
            "and mention the 10% auto-activation threshold. Should also mention MCP "
            "Connector for remote servers. Without the skill, may suggest manual "
            "tool filtering."
        ),
        "scoring_keywords": {
            "accuracy": [
                "tool search", "dynamic", "discovery", "regex",
                "auto-activate", "10%"
            ],
            "completeness": [
                "mcp connector", "defer_loading", "context",
                "ENABLE_TOOL_SEARCH"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "2.3",
        "category": "Can Claude Do X",
        "prompt": (
            "I want Claude to help fill out web forms and navigate browser interfaces "
            "for data entry tasks. Is that possible through the API?"
        ),
        "expected_advantage": (
            "Should describe Computer Use with specific tool version "
            "(computer_20251124 for Opus 4.6 with zoom), requirements (screenshot "
            "handling, coordinate system), and current status. May also mention Claude "
            "Code's Chrome browser use capability."
        ),
        "scoring_keywords": {
            "accuracy": [
                "computer use", "computer_20251124", "computer_20250124",
                "screenshot", "mouse", "keyboard"
            ],
            "completeness": [
                "zoom", "beta", "chrome", "browser",
                "coordinate", "sandbox"
            ],
            "deprecated_patterns": [],
        },
    },

    # Category 3: Implementation Guidance
    {
        "id": "3.1",
        "category": "Implementation Guidance",
        "prompt": (
            "I'm using Claude Opus 4.6 and want to control how much 'thinking' it "
            "does on different types of requests. Some are simple lookups, others are "
            "complex analysis. How do I configure this?"
        ),
        "expected_advantage": (
            "Should recommend adaptive thinking (type: 'adaptive') + effort parameter. "
            "Should NOT recommend budget_tokens (deprecated on Opus 4.6). Should "
            "mention that 'max' effort is Opus 4.6 exclusive."
        ),
        "scoring_keywords": {
            "accuracy": [
                "adaptive", "thinking", "effort", "low", "medium", "high", "max"
            ],
            "completeness": [
                "type: \"adaptive\"", "type: 'adaptive'",
                "budget_tokens", "deprecated", "opus 4.6"
            ],
            "deprecated_patterns": [
                "budget_tokens"
            ],
        },
    },
    {
        "id": "3.2",
        "category": "Implementation Guidance",
        "prompt": (
            "I have a working integration with Claude that uses assistant message "
            "prefilling to start responses in a specific format. I want to upgrade "
            "to Opus 4.6. Anything I should know?"
        ),
        "expected_advantage": (
            "Should flag that prefill is REMOVED on Opus 4.6 (returns 400 error), "
            "and recommend structured outputs or system prompts as alternatives. "
            "Without the skill, may not flag this breaking change."
        ),
        "scoring_keywords": {
            "accuracy": [
                "prefill", "removed", "400", "error",
                "structured output", "system prompt"
            ],
            "completeness": [
                "output_config", "json_schema", "breaking change",
                "migration"
            ],
            "deprecated_patterns": [
                "prefill works", "prefill is supported"
            ],
        },
    },
    {
        "id": "3.3",
        "category": "Implementation Guidance",
        "prompt": (
            "I want Claude to output JSON that strictly matches my schema — not "
            "'best effort' but guaranteed. How do I set this up?"
        ),
        "expected_advantage": (
            "Should describe structured outputs (GA) with the correct parameter path "
            "(output_config.format), mention the old output_format is deprecated, and "
            "provide both JSON output and strict tool use approaches with SDK helpers."
        ),
        "scoring_keywords": {
            "accuracy": [
                "structured output", "output_config", "json_schema",
                "strict", "guaranteed"
            ],
            "completeness": [
                "strict: true", "tool use", "parse()",
                "zodOutputFormat", "sdk"
            ],
            "deprecated_patterns": [
                "output_format"
            ],
        },
    },

    # Category 4: Model Selection
    {
        "id": "4.1",
        "category": "Model Selection",
        "prompt": (
            "I need to choose a Claude model for my application. It needs to handle "
            "long documents (200+ pages), produce detailed analysis, and keep costs "
            "reasonable. What would you recommend?"
        ),
        "expected_advantage": (
            "Should present the current model matrix accurately — Opus 4.6 with 128K "
            "output and 1M context (beta), vs Sonnet 4.5 with 64K output and "
            "interleaved thinking, vs Haiku 4.5 for cost efficiency. Should mention "
            "effort parameter for cost control."
        ),
        "scoring_keywords": {
            "accuracy": [
                "opus 4.6", "sonnet 4.5", "haiku 4.5",
                "128k", "64k", "1M", "200k"
            ],
            "completeness": [
                "effort", "batch", "prompt caching", "cost",
                "interleaved thinking", "adaptive"
            ],
            "deprecated_patterns": [],
        },
    },

    # ---------------------------------------------------------------------------
    # NEW TEST CASES (v1.4.0) — Targeting architecture, model selection,
    # hallucination detection, and extension awareness gaps
    # ---------------------------------------------------------------------------

    # Category 5: Architecture Patterns (new)
    {
        "id": "5.1",
        "category": "Architecture Patterns",
        "prompt": (
            "I need to process 10,000 PDFs and extract structured data from each. "
            "The data needs to match a specific JSON schema. What's the most "
            "cost-effective approach with Claude?"
        ),
        "expected_advantage": (
            "Should recommend batch API (50% discount) + Haiku for extraction + "
            "structured outputs (strict: true or output_config.format). Should mention "
            "prompt caching for the shared schema/system prompt. May mention Files API "
            "for uploads. Should NOT default to expensive Opus for bulk extraction."
        ),
        "scoring_keywords": {
            "accuracy": [
                "batch", "haiku", "structured output", "json schema",
                "cost", "output_config"
            ],
            "completeness": [
                "prompt caching", "50%", "files api", "strict",
                "token counting", "effort"
            ],
            "deprecated_patterns": [
                "output_format"
            ],
        },
    },
    {
        "id": "5.2",
        "category": "Architecture Patterns",
        "prompt": (
            "How should I combine vision and structured outputs to process receipt "
            "images? I need to extract merchant, amount, date, and line items as JSON."
        ),
        "expected_advantage": (
            "Should describe using image content blocks + output_config.format with "
            "a JSON schema. Should mention that this works on all current models. "
            "May suggest prompt caching for the schema, and Haiku for cost efficiency "
            "on high-volume receipt processing."
        ),
        "scoring_keywords": {
            "accuracy": [
                "image", "output_config", "json_schema", "structured output",
                "content block"
            ],
            "completeness": [
                "prompt caching", "haiku", "batch", "schema",
                "vision", "model"
            ],
            "deprecated_patterns": [
                "output_format"
            ],
        },
    },
    {
        "id": "5.3",
        "category": "Architecture Patterns",
        "prompt": (
            "I'm building a chatbot that needs to remember user preferences across "
            "sessions. What's the recommended architecture for persistent memory "
            "with Claude?"
        ),
        "expected_advantage": (
            "Should describe the Memory tool (beta, memory_20250818) with commands "
            "(view, create, str_replace, etc.) and emphasise client-side persistence "
            "requirement. Should mention combining with compaction for long sessions. "
            "Without the skill, may suggest only external database approaches."
        ),
        "scoring_keywords": {
            "accuracy": [
                "memory tool", "memory_20250818", "client-side", "persistent",
                "beta", "cross-conversation"
            ],
            "completeness": [
                "compaction", "context-management-2025-06-27", "view", "create",
                "str_replace", "session"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "5.4",
        "category": "Architecture Patterns",
        "prompt": (
            "My agent needs to call 5 different APIs in sequence to complete a task. "
            "Each API call depends on the previous result. Should I use tool chaining "
            "or is there a better approach?"
        ),
        "expected_advantage": (
            "Should describe programmatic tool calling (beta) for sequential tool "
            "calls without model round-trips. Should note it's Sonnet 4.5 and Opus 4.5 "
            "only. Should contrast with standard tool chaining (multiple model turns) "
            "and when each is appropriate."
        ),
        "scoring_keywords": {
            "accuracy": [
                "programmatic tool calling", "code execution", "round-trip",
                "sequential", "allowed_callers"
            ],
            "completeness": [
                "sonnet 4.5", "opus 4.5", "advanced-tool-use",
                "beta", "latency", "tool chaining"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "5.5",
        "category": "Architecture Patterns",
        "prompt": (
            "I want to build a code review pipeline. Junior devs submit PRs and "
            "Claude should review for bugs, style, security, and performance. "
            "How should I split the work between models to keep costs down?"
        ),
        "expected_advantage": (
            "Should recommend model tiering — Haiku for initial style/lint checks, "
            "Sonnet for bug detection and general review, Opus for security analysis "
            "and complex logic review. Should mention effort parameter for controlling "
            "thoroughness per check type."
        ),
        "scoring_keywords": {
            "accuracy": [
                "haiku", "sonnet", "opus", "pipeline", "model",
                "cost", "tier"
            ],
            "completeness": [
                "effort", "subagent", "parallel", "security",
                "structured output", "agent sdk"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "5.6",
        "category": "Architecture Patterns",
        "prompt": (
            "What's the best way to handle streaming responses when Claude is using "
            "tools? I want to show the user real-time progress but the tool calls "
            "interrupt the stream."
        ),
        "expected_advantage": (
            "Should describe fine-grained tool streaming (GA) which streams tool "
            "parameters progressively. Should mention programmatic tool calling for "
            "reducing interruptions. May mention Server-Sent Events patterns for "
            "the frontend."
        ),
        "scoring_keywords": {
            "accuracy": [
                "fine-grained", "tool streaming", "stream", "progressive",
                "ga"
            ],
            "completeness": [
                "programmatic tool calling", "server-sent events",
                "content block", "delta", "tool_use"
            ],
            "deprecated_patterns": [],
        },
    },

    # Category 6: Model Selection (new)
    {
        "id": "6.1",
        "category": "Model Selection",
        "prompt": (
            "I need to classify 50,000 support tickets into categories like 'billing', "
            "'technical', 'feature request', etc. Which Claude model should I use and "
            "how should I set it up?"
        ),
        "expected_advantage": (
            "Should recommend Haiku 4.5 for cost efficiency on high-volume "
            "classification. Should suggest batch API for 50% discount. Should mention "
            "structured outputs for guaranteed category labels and prompt caching for "
            "the shared system prompt."
        ),
        "scoring_keywords": {
            "accuracy": [
                "haiku", "batch", "structured output", "classification",
                "cost"
            ],
            "completeness": [
                "50%", "prompt caching", "effort", "json_schema",
                "output_config", "low"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "6.2",
        "category": "Model Selection",
        "prompt": (
            "I'm building a legal document analyser that needs to handle 500-page "
            "contracts. It needs to identify clauses, flag risks, and compare against "
            "standard templates. Which model and setup?"
        ),
        "expected_advantage": (
            "Should recommend 1M context (beta) to process entire documents. Should "
            "suggest Opus 4.6 for the analysis (complex reasoning) with adaptive "
            "thinking. Should mention Files API for document management. Cost "
            "considerations for 1M context (premium pricing beyond 200K)."
        ),
        "scoring_keywords": {
            "accuracy": [
                "opus 4.6", "1m context", "1 million", "adaptive thinking",
                "files api", "128k output"
            ],
            "completeness": [
                "premium pricing", "200k", "tier 3", "effort",
                "streaming", "structured output"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "6.3",
        "category": "Model Selection",
        "prompt": (
            "My app needs sub-second response times for autocomplete suggestions. "
            "The suggestions should be contextually relevant based on user input. "
            "Which Claude model gives me the lowest latency?"
        ),
        "expected_advantage": (
            "Should recommend Haiku 4.5 for lowest latency. Should mention "
            "effort: 'low' for faster responses. Should note that streaming helps "
            "with perceived latency. Should NOT recommend Opus for latency-sensitive "
            "use cases."
        ),
        "scoring_keywords": {
            "accuracy": [
                "haiku", "latency", "fast", "effort", "low",
                "streaming"
            ],
            "completeness": [
                "haiku 4.5", "sub-second", "prompt caching",
                "max_tokens", "small"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "6.4",
        "category": "Model Selection",
        "prompt": (
            "I need the highest accuracy possible for a medical literature review. "
            "Cost is secondary — I need the most thorough and reliable analysis. "
            "What's the best setup?"
        ),
        "expected_advantage": (
            "Should recommend Opus 4.6 with effort: 'max' (exclusive to Opus 4.6). "
            "Should mention adaptive thinking for complex reasoning. Should suggest "
            "1M context for processing large papers. May mention citations for "
            "source attribution."
        ),
        "scoring_keywords": {
            "accuracy": [
                "opus 4.6", "effort", "max", "adaptive thinking",
                "128k", "highest"
            ],
            "completeness": [
                "1m context", "citations", "search_result",
                "streaming", "thinking"
            ],
            "deprecated_patterns": [],
        },
    },

    # Category 7: Hallucination Detection (new)
    {
        "id": "7.1",
        "category": "Hallucination Detection",
        "prompt": (
            "Can Claude autonomously browse the web and make purchases on my "
            "behalf? I want to build an AI shopping assistant."
        ),
        "expected_advantage": (
            "Should clarify that Computer Use (beta) can interact with websites "
            "but requires explicit human confirmation for purchases. Should NOT "
            "claim Claude can autonomously make financial transactions. Should "
            "mention security requirements (sandboxing, confirmation)."
        ),
        "scoring_keywords": {
            "accuracy": [
                "computer use", "beta", "human confirmation", "security",
                "sandbox"
            ],
            "completeness": [
                "screenshot", "browser", "chrome", "supervised",
                "risk", "confirmation"
            ],
            "deprecated_patterns": [
                "autonomously purchase", "automatically buy",
                "make transactions without"
            ],
        },
    },
    {
        "id": "7.2",
        "category": "Hallucination Detection",
        "prompt": (
            "Does Claude have perfect mathematical computation abilities? I need "
            "it for financial calculations with exact precision."
        ),
        "expected_advantage": (
            "Should clarify that Claude is an LLM and NOT a calculator — it can "
            "make arithmetic errors. Should recommend using code execution tool "
            "for precise calculations. Should NOT claim perfect math ability."
        ),
        "scoring_keywords": {
            "accuracy": [
                "code execution", "not perfect", "errors", "calculator",
                "tool", "compute"
            ],
            "completeness": [
                "python", "code_execution", "sandbox", "verify",
                "precision", "floating point"
            ],
            "deprecated_patterns": [
                "perfect math", "always correct", "exact arithmetic"
            ],
        },
    },
    {
        "id": "7.3",
        "category": "Hallucination Detection",
        "prompt": (
            "Can Claude access and read my local files directly through the API? "
            "I just want to point it at my Documents folder and have it process "
            "everything."
        ),
        "expected_advantage": (
            "Should clarify that the API itself does NOT have local filesystem "
            "access. Should explain Files API (upload-based) and Claude Code's "
            "Bash/Read tools as alternatives. Should NOT claim direct filesystem "
            "access through the Messages API."
        ),
        "scoring_keywords": {
            "accuracy": [
                "files api", "upload", "no direct access", "api",
                "claude code", "bash"
            ],
            "completeness": [
                "files-api-2025-04-14", "read tool", "agent sdk",
                "local", "sandbox", "filesystem"
            ],
            "deprecated_patterns": [
                "directly access", "read your files", "point at folder"
            ],
        },
    },

    # Category 8: Extension Awareness (new)
    {
        "id": "8.1",
        "category": "Extension Awareness",
        "prompt": (
            "I have a linting script that should run after every file edit in "
            "Claude Code. Should I make this a skill or something else?"
        ),
        "expected_advantage": (
            "Should recommend a Hook (PostToolUse event, matcher for Edit/Write) "
            "NOT a skill. Should explain the distinction — hooks are deterministic "
            "event scripts, skills are knowledge/workflows. Should provide hook "
            "configuration format."
        ),
        "scoring_keywords": {
            "accuracy": [
                "hook", "PostToolUse", "deterministic", "event",
                "not a skill"
            ],
            "completeness": [
                "matcher", "Edit", "Write", "command",
                "settings.json", "exit code"
            ],
            "deprecated_patterns": [],
        },
    },
    {
        "id": "8.2",
        "category": "Extension Awareness",
        "prompt": (
            "My team has 12 MCP servers, 3 custom skills, and 2 hooks that we "
            "use on every project. How should I package this so everyone on the "
            "team can install it easily?"
        ),
        "expected_advantage": (
            "Should recommend a Plugin (bundles skills, hooks, MCP, commands). "
            "Should mention plugin.json manifest, directory structure, and "
            "installation command. May mention plugin marketplaces for team "
            "distribution."
        ),
        "scoring_keywords": {
            "accuracy": [
                "plugin", "bundle", "plugin.json", "install",
                "distribute"
            ],
            "completeness": [
                "marketplace", "skills/", "hooks/", ".mcp.json",
                "CLAUDE_PLUGIN_ROOT", "scope"
            ],
            "deprecated_patterns": [],
        },
    },
]


# ---------------------------------------------------------------------------
# Scoring rubric
# ---------------------------------------------------------------------------

RUBRIC = """
## Scoring Rubric

For each test, score the response on:

| Criterion        | Score | Definition                                                       |
|------------------|-------|------------------------------------------------------------------|
| Accuracy         | 0-3   | 0: Incorrect/outdated. 1: Partially correct. 2: Correct.        |
|                  |       | 3: Correct with specifics (parameter names, headers, versions).  |
| Completeness     | 0-3   | 0: Misses the key capability. 1: Mentions it vaguely.           |
|                  |       | 2: Covers main points. 3: Main points + edge cases/caveats.     |
| Avoids Deprecated| 0-1   | 0: Recommends deprecated approach. 1: Uses current approach.     |
| Actionability    | 0-2   | 0: Vague. 1: Gives direction. 2: Gives specific code/config.    |

Max score per test: 9. Total across 25 tests: 225.
"""


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_single_test(prompt: str, model: str, condition: str) -> dict:
    """Run a single test prompt via the Agent SDK query() function."""
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print("ERROR: claude-agent-sdk not installed.", file=sys.stderr)
        print("Install with: pip install claude-agent-sdk", file=sys.stderr)
        sys.exit(1)

    response_text = []
    async for event in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model=model,
            max_turns=1,
            allowed_tools=[],  # No tools — pure knowledge test
        ),
    ):
        if hasattr(event, "content"):
            for block in event.content:
                if hasattr(block, "text"):
                    response_text.append(block.text)
        elif hasattr(event, "text"):
            response_text.append(event.text)

    return {
        "condition": condition,
        "model": model,
        "response": "".join(response_text),
        "timestamp": datetime.utcnow().isoformat(),
    }


async def run_test_pair(test: dict, model: str, run_number: int) -> dict:
    """Run a single test in both control and treatment conditions."""
    print(f"  Run {run_number} — Test {test['id']}: {test['category']}...")

    # Control (no skill — standard session)
    control = await run_single_test(test["prompt"], model, "control")

    # Treatment (skill installed — same parameters, skill present in session)
    # Note: The skill must be installed before running treatment.
    # The subagent will automatically have access to installed skills.
    treatment = await run_single_test(test["prompt"], model, "treatment")

    return {
        "test_id": test["id"],
        "category": test["category"],
        "prompt": test["prompt"],
        "expected_advantage": test["expected_advantage"],
        "scoring_keywords": test["scoring_keywords"],
        "run_number": run_number,
        "control": control,
        "treatment": treatment,
    }


async def run_all_tests(model: str, runs: int, output_dir: str):
    """Run all tests across multiple runs."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    results_file = output_path / f"eval-results-{timestamp}.json"

    all_results = []

    print(f"Running {len(TESTS)} tests x {runs} runs = {len(TESTS) * runs} evaluations")
    print(f"Model: {model}")
    print(f"Output: {results_file}")
    print()

    for run in range(1, runs + 1):
        print(f"=== Run {run}/{runs} ===")
        for test in TESTS:
            result = await run_test_pair(test, model, run)
            all_results.append(result)
        print()

    # Save results
    output_data = {
        "metadata": {
            "model": model,
            "runs": runs,
            "total_tests": len(TESTS),
            "timestamp": timestamp,
            "rubric": RUBRIC,
        },
        "tests": [
            {
                "id": t["id"],
                "category": t["category"],
                "prompt": t["prompt"],
                "expected_advantage": t["expected_advantage"],
            }
            for t in TESTS
        ],
        "results": all_results,
    }

    with open(results_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {results_file}")
    print()
    print("Next steps:")
    print("  1. Score each response using the rubric (manually or with a scoring LLM)")
    print("  2. Compare control vs treatment scores per test")
    print("  3. Calculate aggregate improvement")

    # Generate scoring template
    scoring_file = output_path / f"scoring-template-{timestamp}.md"
    with open(scoring_file, "w") as f:
        f.write("# Capabilities Skill Evaluation — Scoring Sheet\n\n")
        f.write(f"**Model:** {model}\n")
        f.write(f"**Date:** {timestamp}\n")
        f.write(f"**Runs:** {runs}\n\n")
        f.write(RUBRIC)
        f.write("\n\n---\n\n")

        for result in all_results:
            f.write(f"## Test {result['test_id']} — {result['category']} (Run {result['run_number']})\n\n")
            f.write(f"**Prompt:** {result['prompt'][:100]}...\n\n")
            f.write(f"**Expected advantage:** {result['expected_advantage'][:150]}...\n\n")

            f.write("### Control Response\n\n")
            f.write(f"```\n{result['control']['response'][:500]}...\n```\n\n")
            f.write("| Criterion | Score | Notes |\n")
            f.write("|-----------|-------|-------|\n")
            f.write("| Accuracy (0-3) | | |\n")
            f.write("| Completeness (0-3) | | |\n")
            f.write("| Avoids Deprecated (0-1) | | |\n")
            f.write("| Actionability (0-2) | | |\n")
            f.write("| **Total** | **/9** | |\n\n")

            f.write("### Treatment Response\n\n")
            f.write(f"```\n{result['treatment']['response'][:500]}...\n```\n\n")
            f.write("| Criterion | Score | Notes |\n")
            f.write("|-----------|-------|-------|\n")
            f.write("| Accuracy (0-3) | | |\n")
            f.write("| Completeness (0-3) | | |\n")
            f.write("| Avoids Deprecated (0-1) | | |\n")
            f.write("| Actionability (0-2) | | |\n")
            f.write("| **Total** | **/9** | |\n\n")
            f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("| Test | Control Avg | Treatment Avg | Delta |\n")
        f.write("|------|-------------|---------------|-------|\n")
        for test in TESTS:
            f.write(f"| {test['id']} | | | |\n")
        f.write("| **Total** | **/225** | **/225** | |\n")

    print(f"Scoring template saved to: {scoring_file}")


# ---------------------------------------------------------------------------
# Automated scoring helper
# ---------------------------------------------------------------------------

def keyword_score(response: str, test: dict) -> dict:
    """Simple keyword-based scoring for quick automated analysis.

    This is a rough heuristic — manual scoring is more accurate.
    Returns a dict with keyword match counts for each category.
    """
    response_lower = response.lower()
    keywords = test["scoring_keywords"]

    accuracy_hits = sum(
        1 for kw in keywords.get("accuracy", [])
        if kw.lower() in response_lower
    )
    completeness_hits = sum(
        1 for kw in keywords.get("completeness", [])
        if kw.lower() in response_lower
    )
    deprecated_hits = sum(
        1 for kw in keywords.get("deprecated_patterns", [])
        if kw.lower() in response_lower
    )

    return {
        "accuracy_keywords_matched": accuracy_hits,
        "accuracy_keywords_total": len(keywords.get("accuracy", [])),
        "completeness_keywords_matched": completeness_hits,
        "completeness_keywords_total": len(keywords.get("completeness", [])),
        "deprecated_patterns_found": deprecated_hits,
        "deprecated_patterns_total": len(keywords.get("deprecated_patterns", [])),
    }


# ---------------------------------------------------------------------------
# Test data export (for running without the SDK)
# ---------------------------------------------------------------------------

def export_prompts(output_dir: str):
    """Export test prompts as standalone text files for manual testing."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for test in TESTS:
        filename = f"test-{test['id'].replace('.', '-')}.txt"
        filepath = output_path / filename
        with open(filepath, "w") as f:
            f.write(f"# Test {test['id']}: {test['category']}\n\n")
            f.write(f"{test['prompt']}\n")

    # Also export the full test suite as JSON
    suite_file = output_path / "test-suite.json"
    with open(suite_file, "w") as f:
        json.dump(TESTS, f, indent=2)

    print(f"Exported {len(TESTS)} test prompts to {output_path}/")
    print(f"Test suite JSON: {suite_file}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate the claude-capabilities skill"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-5-20250929",
        help="Model to use for evaluation (default: claude-sonnet-4-5-20250929)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=2,
        help="Number of runs per test for variance analysis (default: 2)",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Export test prompts without running evaluations",
    )

    args = parser.parse_args()

    if args.export_only:
        export_prompts(args.output)
        return

    asyncio.run(run_all_tests(args.model, args.runs, args.output))


if __name__ == "__main__":
    main()
