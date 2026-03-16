# Chrome CDP Browser Eval Spec

**Status:** Draft
**Date:** 2026-03-16
**Author:** Claude (spec), Liam (PoC)

Replace the agent-browser backend in `evals/browser_eval.sh` with chrome-cdp for Claude.ai A/B testing. The migration yields a 5-6x speed improvement (25 min vs 135 min for a full 15-prompt A/B run) and eliminates auth state expiry, headless-mode bugs, and the agent-browser dependency.

---

## 1. Architecture

### Current (agent-browser)

```
browser_eval.sh
  └── agent-browser CLI (Playwright wrapper)
        └── managed Chromium instance (headless or headed)
              └── saved auth state JSON (cookies, localStorage)
```

The script launches a browser via `agent-browser --session`, loads saved auth state, and communicates through agent-browser's `open`, `snapshot`, `fill`, `click`, `eval`, `press`, `screenshot` commands. Each command shells out to the `agent-browser` CLI binary.

### Proposed (chrome-cdp)

```
browser_eval_cdp.sh
  └── cdp.mjs (Node.js CDP client)
        └── user's existing Chrome session (remote debugging enabled)
              └── already logged in to Claude.ai
```

The script connects to the user's running Chrome via DevToolsActivePort. No separate browser launch, no auth state management, no Playwright. Every interaction goes through `cdp.mjs` commands: `eval`, `snap`, `click`, `nav`, `shot`.

### Key Differences

| Aspect | agent-browser | chrome-cdp |
|--------|---------------|------------|
| Browser | Managed Chromium (headless/headed) | User's existing Chrome |
| Auth | Saved state JSON, expires periodically | Already logged in, never expires |
| Text input | Playwright `fill`/`type` (150s for long prompts) | `document.execCommand('insertText')` via eval (0.4s) |
| Submit | Playwright `press Enter` | Click send button via eval |
| Snapshots | agent-browser `snapshot` (Playwright accessibility) | `cdp.mjs snap` (CDP Accessibility.getFullAXTree) |
| Screenshots | agent-browser `screenshot` | `cdp.mjs shot` |
| Speed per prompt | 260-350s | 30-50s |
| Daemon model | Single session daemon, killed between conditions | Per-tab daemon, persistent, 20min idle timeout |

### File Layout

```
evals/
  browser_eval.sh           # existing — unchanged, agent-browser backend
  browser_eval_cdp.sh       # new — chrome-cdp backend
  browser_eval_report.py    # shared — no changes needed
  browser-eval-results.json # shared output format
```

The new script produces results in the exact same JSON format as the existing script, so `browser_eval_report.py` works without modification.

---

## 2. Prerequisites

### Required

1. **Chrome with remote debugging enabled**
   - Open `chrome://inspect/#remote-debugging` and toggle the switch ON
   - This writes `DevToolsActivePort` to Chrome's profile directory
   - Must be done once; persists across Chrome restarts

2. **Node.js 22+** (for built-in WebSocket support in cdp.mjs)

3. **Logged-in Claude.ai session** in the running Chrome instance
   - Navigate to `claude.ai` in Chrome and verify you are logged in
   - No separate auth state file needed

4. **chrome-cdp skill installed** at `~/.agents/skills/chrome-cdp/`
   - The script references `~/.agents/skills/chrome-cdp/scripts/cdp.mjs`

5. **Python 3** (for report generation and JSON assembly, same as current script)

### First-Run Setup

On the first CDP command to a tab, Chrome shows an "Allow debugging?" dialog. The eval script must:
1. Run `cdp.mjs list` to discover targets
2. Run one command against the Claude.ai tab (triggers the dialog)
3. User clicks "Allow" once
4. Subsequent commands to that tab work without prompts (daemon keeps session alive)

The script will include a `--setup` mode that walks through this process.

---

## 3. Implementation Plan

**Strategy: New file, not a flag.** Create `browser_eval_cdp.sh` as a standalone script.

Rationale:
- The two backends have fundamentally different prerequisites (managed browser vs existing Chrome)
- Auth flow is completely different (save/restore state vs already logged in)
- Mixing both behind a `--backend` flag would double the complexity of every function
- The scripts share: prompt definitions, JSON format, report generation, and the overall control/treatment flow
- Keeping `browser_eval.sh` unchanged means zero risk of regression

### Shared Components

Extract prompt definitions and JSON helpers into a sourceable file if the duplication bothers us later. For the initial implementation, copy them into the new script (15 prompts + helpers is ~100 lines — not worth the abstraction overhead yet).

### CLI Interface

```
browser_eval_cdp.sh [mode] [options]

Modes:
  --setup        Discover Claude.ai tab, trigger Allow dialog, verify
  --control      Run control condition only (skill OFF)
  --treatment    Run treatment condition only (skill ON)
  --report-only  Regenerate report from existing results
  (no flag)      Full run: control + treatment + report

Options:
  --yes          Skip interactive confirmations
```

No `--auth` mode (not needed). No `--headed` mode (Chrome is always visible).

---

## 4. Core Functions

### 4.1 `cdp_cmd` — Base wrapper

```bash
CDP_SCRIPT="$HOME/.agents/skills/chrome-cdp/scripts/cdp.mjs"
CDP_TARGET=""  # set during setup/discovery

cdp_cmd() {
  # Usage: cdp_cmd <command> [args...]
  # Returns: stdout from cdp.mjs, or sets $? to 1 on failure
  node "$CDP_SCRIPT" "$@"
}
```

### 4.2 `cdp_discover_target` — Find the Claude.ai tab

```bash
cdp_discover_target() {
  # Run cdp.mjs list, grep for claude.ai, extract target prefix
  local list_output
  list_output=$(cdp_cmd list)

  # Find the claude.ai line — match URL containing claude.ai
  local target_line
  target_line=$(echo "$list_output" | grep -i 'claude\.ai' | head -1)

  if [[ -z "$target_line" ]]; then
    log_error "No Claude.ai tab found. Open claude.ai in Chrome first."
    return 1
  fi

  # Extract the target prefix (first whitespace-delimited token)
  CDP_TARGET=$(echo "$target_line" | awk '{print $1}')
  log "Found Claude.ai tab: $CDP_TARGET"
}
```

### 4.3 `cdp_navigate` — SPA-friendly navigation

```bash
cdp_navigate() {
  local url="$1"
  # Use window.location.href assignment for SPA navigation
  # (cdp.mjs nav triggers full page load which can break SPA state)
  cdp_cmd eval "$CDP_TARGET" "window.location.href = '$url'"
  sleep 3  # wait for SPA route transition
  # Verify navigation
  local current_url
  current_url=$(cdp_cmd eval "$CDP_TARGET" "window.location.href")
  log "  Navigated to: $current_url"
}
```

Why not `cdp.mjs nav`? Claude.ai is a single-page app. `nav` (Page.navigate) triggers a full page load and waits for the load event, which works but is slower and can cause unnecessary re-authentication. SPA navigation via `window.location.href` assignment is faster and preserves session state.

For non-SPA pages (like the initial setup verification), `cdp.mjs nav` is fine.

### 4.4 `cdp_type` — ProseMirror-compatible text input

```bash
cdp_type() {
  local text="$1"
  # ProseMirror ignores Input.insertText (cdp.mjs type command).
  # Must use document.execCommand('insertText') which triggers ProseMirror's
  # input handling and state sync.
  #
  # The text must be JS-escaped for embedding in the eval expression.
  local escaped_text
  escaped_text=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read())[1:-1])" <<< "$text")

  # Focus the contenteditable div first
  cdp_cmd click "$CDP_TARGET" 'div[contenteditable="true"]'
  sleep 0.3

  # Insert text via execCommand
  cdp_cmd eval "$CDP_TARGET" "document.execCommand('insertText', false, \"$escaped_text\")"
}
```

**Critical discovery from PoC:** `cdp.mjs type` uses `Input.insertText` at the CDP level. ProseMirror (Claude.ai's editor) does NOT react to `Input.insertText` — it only sees native input events. `document.execCommand('insertText')` works because it triggers the browser's native editing pipeline, which ProseMirror intercepts.

### 4.5 `cdp_submit` — Click the Send button

```bash
cdp_submit() {
  # The Send button has aria-label="Send message" but only appears when
  # ProseMirror detects content in the editor. After cdp_type, it should
  # be visible.
  #
  # Enter key via CDP Input.dispatchKeyEvent does NOT work — ProseMirror
  # intercepts it for newline insertion, not form submission.
  cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var btn = document.querySelector('button[aria-label=\"Send message\"]');
      if (!btn) return 'NOT_FOUND';
      btn.click();
      return 'SENT';
    })()
  "
}
```

**Fallback if Send button not found:** Wait 500ms and retry once (ProseMirror state sync may be delayed). If still not found, try `button[aria-label="Send Message"]` (case variation) and `button[data-testid="send-button"]`.

### 4.6 `cdp_wait_for_response` — Poll for completion

```bash
cdp_wait_for_response() {
  local elapsed=0
  local timeout="${RESPONSE_TIMEOUT:-120}"

  log "  Waiting for response (timeout: ${timeout}s)..."

  # Initial wait for response to start
  sleep 5
  elapsed=5

  while [ "$elapsed" -lt "$timeout" ]; do
    local snap
    snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")

    # Primary signal: "Give positive feedback" or "Give negative feedback"
    # These thumbs-up/thumbs-down buttons only appear after response is complete.
    if echo "$snap" | grep -qi 'Give positive feedback\|Give negative feedback'; then
      log "  Response complete (feedback buttons detected at ${elapsed}s)"
      return 0
    fi

    # Secondary signal: "Copy" button present AND no "Stop" button
    if echo "$snap" | grep -qi 'Copy' && ! echo "$snap" | grep -qi 'Stop response'; then
      log "  Response complete (Copy present, Stop absent at ${elapsed}s)"
      return 0
    fi

    sleep "$POLL_INTERVAL"
    elapsed=$((elapsed + POLL_INTERVAL))
  done

  log_warn "  Response timeout after ${timeout}s — capturing partial"
  return 0  # capture what we have
}
```

**Why "Give positive/negative feedback"?** This is the most reliable completion signal discovered in the PoC. These are the thumbs-up/thumbs-down buttons that only render after streaming finishes. The existing script uses "Stop response button disappears" which requires two checks; the feedback button approach needs only one.

### 4.7 `cdp_extract_response` — Get response text from accessibility tree

```bash
cdp_extract_response() {
  # Strategy 1 (preferred): Extract via DOM selector
  local response_text
  response_text=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var selectors = [
        '[data-testid=\"chat-message-text\"]',
        'div.font-claude-message',
        'div.prose'
      ];
      for (var i = 0; i < selectors.length; i++) {
        var els = document.querySelectorAll(selectors[i]);
        if (els.length > 0) {
          var text = els[els.length - 1].innerText;
          if (text && text.trim().length > 50) return text;
        }
      }
      return 'EXTRACTION_FAILED';
    })()
  " 2>/dev/null || echo "EXTRACTION_FAILED")

  if [[ "$response_text" != "EXTRACTION_FAILED" && -n "$response_text" ]]; then
    echo "$response_text"
    return 0
  fi

  # Strategy 2: Parse snap output for the response content
  # The snap accessibility tree contains all text nodes. The last major
  # text block after the user's prompt is the response.
  log_warn "  DOM extraction failed, falling back to snap parsing"
  local snap
  snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")
  echo "$snap"
}
```

The extraction logic is identical to the existing script. The only difference is the transport: `cdp_cmd eval` instead of `ab eval`.

### 4.8 `cdp_extract_thinking` — Get thinking panel content

```bash
cdp_extract_thinking() {
  # Step 1: Check if a thinking panel exists via snap
  # The thinking toggle is a button with text like "Thinking about..." or
  # a summary like "Examined Claude's cross-conversation memory limitations"
  # In the accessibility tree it appears as:
  #   [button] <summary text>
  #   [status] <summary text>
  # or in newer versions:
  #   [button] Thinking for N seconds
  #   [button] <completed summary>
  #
  # Also check for "Analyzed", "Considered", "Examined", "Reviewed" etc.

  local snap
  snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")

  if [[ -z "$snap" ]]; then
    echo ""
    return 0
  fi

  # Save snap for debugging
  echo "$snap" > "$RESULTS_DIR/last_thinking_snapshot.txt" 2>/dev/null || true

  # Step 2: Expand the thinking panel by clicking the toggle button
  # Use eval to find and click the aria-expanded button associated with thinking
  local expanded
  expanded=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      // Find all buttons — the thinking toggle typically has aria-expanded
      var buttons = document.querySelectorAll('button[aria-expanded]');
      for (var i = 0; i < buttons.length; i++) {
        var text = buttons[i].textContent || '';
        // Match thinking summary patterns (not UI buttons like menus)
        if (text.length > 15 && text.length < 300 &&
            !text.match(/^(Copy|Retry|Edit|Send|Stop|Continue|Menu|More)/i)) {
          if (buttons[i].getAttribute('aria-expanded') === 'false') {
            buttons[i].click();
          }
          return 'FOUND';
        }
      }
      return 'NOT_FOUND';
    })()
  " 2>/dev/null || echo "NOT_FOUND")

  if [[ "$expanded" == *"NOT_FOUND"* ]]; then
    # No thinking panel found — this is normal for some responses
    echo ""
    return 0
  fi

  sleep 1.5

  # Step 3: Extract the expanded thinking content
  local thinking_text
  thinking_text=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var btn = document.querySelector('button[aria-expanded=\"true\"]');
      if (!btn) return '';

      var gp = btn.parentElement ? btn.parentElement.parentElement : null;
      if (!gp) return '';

      var parts = [];
      var children = gp.children;
      for (var i = 2; i < children.length; i++) {
        var text = children[i].innerText;
        if (text && text.trim().length > 0) {
          parts.push(text.trim());
        }
      }
      if (parts.length > 0) return parts.join('\\n');

      // Fallback: get the button's own text as the summary
      return '[Thinking summary] ' + btn.textContent.trim();
    })()
  " 2>/dev/null || echo "")

  echo "$thinking_text"
}
```

This is functionally identical to the existing `extract_thinking()` logic. The DOM structure navigation is the same — only the transport changes from `ab eval`/`ab snapshot`/`ab click` to `cdp_cmd eval`/`cdp_cmd snap`/`cdp_cmd click`.

---

## 5. Skill Toggle

Full flow for programmatically toggling the assistant-capabilities skill on/off.

### Flow

```
1. Navigate to https://claude.ai/customize/skills (SPA nav)
2. Wait for page to render (sleep 2s + verify snap contains skill list)
3. Find and click the "assistant-capabilities" skill entry
4. Wait for detail pane to load (sleep 1.5s)
5. Read current toggle state: input[aria-label="Enable skill"].checked
6. If already in desired state, return success
7. Click the toggle input element
8. Verify new state matches desired state
9. Navigate back to /new for the eval
```

### Implementation

```bash
SKILL_NAME="assistant-capabilities"
SKILL_URL="https://claude.ai/customize/skills"

cdp_toggle_skill() {
  local desired_state="$1"  # "on" or "off"

  log "Navigating to skill settings..."
  cdp_navigate "$SKILL_URL"
  sleep 2

  # Verify we're on the skills page
  local snap
  snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")
  if ! echo "$snap" | grep -qi 'skill'; then
    log_error "Skills page did not load"
    return 1
  fi

  # Click the skill name to open detail pane
  # Use eval to find the button/link containing our skill name
  cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var elements = document.querySelectorAll('button, a, div[role=\"button\"]');
      for (var i = 0; i < elements.length; i++) {
        if (elements[i].textContent.indexOf('$SKILL_NAME') !== -1) {
          elements[i].click();
          return 'clicked';
        }
      }
      return 'not_found';
    })()
  " 2>/dev/null || true
  sleep 1.5

  # Read current state
  local current_state
  current_state=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var el = document.querySelector('input[aria-label=\"Enable skill\"]');
      if (!el) return 'NOT_FOUND';
      return el.checked ? 'on' : 'off';
    })()
  " 2>/dev/null || echo "NOT_FOUND")
  current_state=$(echo "$current_state" | tr -d '"')

  if [[ "$current_state" == "NOT_FOUND" ]]; then
    log_error "Could not find skill toggle"
    return 1
  fi

  if [[ "$current_state" == "$desired_state" ]]; then
    log "Skill already $desired_state"
    return 0
  fi

  # Click the toggle
  cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var el = document.querySelector('input[aria-label=\"Enable skill\"]');
      if (el) { el.click(); return 'clicked'; }
      return 'not_found';
    })()
  " 2>/dev/null || true
  sleep 1.5

  # Verify
  local new_state
  new_state=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var el = document.querySelector('input[aria-label=\"Enable skill\"]');
      if (!el) return 'NOT_FOUND';
      return el.checked ? 'on' : 'off';
    })()
  " 2>/dev/null || echo "NOT_FOUND")
  new_state=$(echo "$new_state" | tr -d '"')

  if [[ "$new_state" == "$desired_state" ]]; then
    log "Skill toggled to: $desired_state"
    return 0
  else
    log_error "Toggle failed (wanted $desired_state, got $new_state)"
    return 1
  fi
}
```

This is a direct port of the existing `toggle_skill()` function. The logic is identical; only the transport commands change.

---

## 6. Skill Invocation Detection

### The Problem

Claude.ai has a built-in skill called "product self-knowledge" (or similar internal name) that provides basic platform awareness. Our installed skill is "assistant-capabilities". The thinking panel may reference either skill, and we must distinguish between them.

In the control condition (our skill OFF), Claude may still use the built-in product self-knowledge. In the treatment condition (our skill ON), Claude should use assistant-capabilities — and we need to verify it does.

### Detection Strategy

The thinking panel text reveals which skill was invoked. Key distinguishing patterns:

**assistant-capabilities (our skill) triggers:**
- `"assistant capabilities"` (the skill name itself)
- `"assistant-capabilities"` (hyphenated form)
- `"check assistant capabilities"` / `"consult assistant capabilities"`
- References to specific content from our SKILL.md (model parameters, tier-2 references, etc.)

**product self-knowledge (built-in) triggers:**
- `"product self-knowledge"` / `"product self knowledge"`
- `"check product self-knowledge"`
- Generic platform awareness without detailed model parameters

**Ambiguous (could be either):**
- `"capabilities skill"` — could refer to either
- `"check.*skill.*for"` — too generic
- `"reading.*skill"` — too generic

### Updated Detection Patterns

Update `browser_eval_report.py` to distinguish the two:

```python
# Patterns that specifically indicate OUR skill (assistant-capabilities)
OUR_SKILL_PATTERNS = [
    r"assistant.capabilities",           # skill name (with any separator)
    r"check assistant capabilities",
    r"consult assistant capabilities",
    r"assistant.capabilities skill",
    # Content markers unique to our skill
    r"tier.?[12]",                       # tier system is unique to our skill
    r"reference file",                   # our skill uses reference files
    r"SKILL\.md",                        # explicit reference to our skill file
]

# Patterns that indicate the BUILT-IN product self-knowledge
BUILTIN_SKILL_PATTERNS = [
    r"product self.knowledge",
    r"check product self.knowledge",
    r"self.knowledge skill",
]

# Generic patterns (could be either, lower confidence)
GENERIC_SKILL_PATTERNS = [
    r"capabilities skill",
    r"check.*skill.*for",
    r"consult.*skill",
    r"reading.*skill",
]
```

### Updated Detection Function

```python
def detect_skill_trigger(thinking: str) -> dict:
    """Detect if OUR skill (assistant-capabilities) was triggered."""
    if not thinking:
        return {
            "triggered": False,
            "which_skill": "unknown",
            "confidence": "no_thinking",
            "evidence": [],
        }

    thinking_lower = thinking.lower()

    our_evidence = []
    for pattern in OUR_SKILL_PATTERNS:
        matches = re.findall(pattern, thinking_lower)
        our_evidence.extend(matches)

    builtin_evidence = []
    for pattern in BUILTIN_SKILL_PATTERNS:
        matches = re.findall(pattern, thinking_lower)
        builtin_evidence.extend(matches)

    generic_evidence = []
    for pattern in GENERIC_SKILL_PATTERNS:
        matches = re.findall(pattern, thinking_lower)
        generic_evidence.extend(matches)

    if our_evidence:
        return {
            "triggered": True,
            "which_skill": "assistant-capabilities",
            "confidence": "high" if len(our_evidence) >= 2 else "medium",
            "evidence": our_evidence[:3],
        }

    if builtin_evidence:
        return {
            "triggered": True,
            "which_skill": "product-self-knowledge",
            "confidence": "high" if len(builtin_evidence) >= 2 else "medium",
            "evidence": builtin_evidence[:3],
        }

    if generic_evidence:
        return {
            "triggered": True,
            "which_skill": "ambiguous",
            "confidence": "low",
            "evidence": generic_evidence[:3],
        }

    return {
        "triggered": False,
        "which_skill": "none",
        "confidence": "low",
        "evidence": [],
    }
```

### Report Impact

The summary table gains a column:

```
| Prompt | Category | Skill? | Which Skill | Web Search | Status |
```

Treatment rows showing "product-self-knowledge" instead of "assistant-capabilities" indicate our skill was NOT invoked despite being enabled — a signal that the skill's trigger conditions need improvement.

### Note on Report Script Changes

The skill detection improvements (distinguishing our skill from the built-in one) should be applied to `browser_eval_report.py` regardless of which backend is used. This is a separate, additive change that benefits both `browser_eval.sh` and `browser_eval_cdp.sh`.

---

## 7. Response Extraction

### Strategy

Identical to the existing script. The CDP snap (accessibility tree) and eval (DOM queries) provide the same information as agent-browser's snapshot and eval.

### Selector Priority

1. `[data-testid="chat-message-text"]` — Claude.ai's test ID (most stable)
2. `div.font-claude-message` — class-based selector
3. `div.prose` — generic prose container

### Extraction Flow

```
1. cdp_cmd eval → try DOM selectors, get last element's innerText
2. If DOM extraction fails → cdp_cmd snap → parse accessibility tree
3. If snap parsing fails → return "EXTRACTION_FAILED"
```

### Cleaning

Response text may contain trailing UI elements (button labels, etc.) from the snap. The report generator should strip known UI strings:
- "Copy", "Retry", "Try again"
- "Give positive feedback", "Give negative feedback"
- "Message actions"

This post-processing belongs in `assemble_results()` or `browser_eval_report.py`, not in the extraction function itself.

---

## 8. Thinking Extraction

### DOM Structure (Claude.ai, as of March 2026)

```
grandparent DIV
  ├── DIV > BUTTON[aria-expanded="false"]   (thinking toggle)
  │         "Examined Claude's memory capabilities"
  ├── SPAN                                  (status text)
  │   "Examined Claude's memory capabilities"
  └── DIV                                   (expanded content, hidden until clicked)
      ├── P  "Let me check what I know about..."
      └── P  "Based on the assistant-capabilities skill..."
```

### Extraction Flow

```
1. Take snap to check if thinking panel exists
2. Find button[aria-expanded] with summary-like text (>15 chars, <300 chars,
   not a UI button like Copy/Retry)
3. If aria-expanded="false", click to expand
4. Wait 1.5s for expansion animation
5. Navigate grandparent → children[2+] → collect innerText
6. If expanded content is empty, return "[Thinking summary] <button text>"
```

### Accessibility Tree Pattern

In the CDP snap output, the thinking toggle appears as:

```
  [button] Examined Claude's cross-conversation memory limitations
  [status] Examined Claude's cross-conversation memory limitations
```

The `[status]` line immediately after a `[button]` is the key signal. This pattern is used in the existing script's grep-based detection and carries over unchanged.

---

## 9. Error Handling

### Target Tab Lost

The CDP daemon auto-detects when the tab closes (`Target.targetDestroyed` event) and shuts down. If the eval script tries to send a command after the tab is gone:

```
Error: Connection closed before response
```

**Recovery:**
1. Log the error
2. Attempt to rediscover the Claude.ai tab (`cdp_discover_target`)
3. If found, continue with the new target
4. If not found, fail the current prompt with `write_error_result` and continue to next prompt

```bash
cdp_cmd_with_retry() {
  local result
  if result=$(cdp_cmd "$@" 2>&1); then
    echo "$result"
    return 0
  fi

  # Check if it's a connection error (tab lost)
  if echo "$result" | grep -qi 'Connection closed\|Daemon failed\|No target'; then
    log_warn "  Tab connection lost. Rediscovering..."
    if cdp_discover_target; then
      # Retry with new target — but only if the command used CDP_TARGET
      result=$(cdp_cmd "$@" 2>&1) && { echo "$result"; return 0; }
    fi
  fi

  echo "$result"
  return 1
}
```

### Navigation Failure

SPA navigation (`window.location.href = ...`) can silently fail if Claude.ai's router doesn't handle it. Verify by checking `window.location.href` after navigation and retry with `cdp.mjs nav` (full page load) as fallback.

### Send Button Not Found

Causes: ProseMirror did not sync (text appears in DOM but ProseMirror state is empty).

**Recovery:**
1. Wait 500ms, retry `document.querySelector('button[aria-label="Send message"]')`
2. If still missing, clear the editor and re-type via eval, then retry
3. If still missing, fail the prompt with error

### Snap/Eval Timeout

cdp.mjs has a 15s default timeout. For large pages, snaps can be slow.

**Recovery:** Retry once. If it fails again, proceed with a partial result or write an error result.

### Chrome Not Running / Remote Debugging Off

```
Error: No DevToolsActivePort found
```

**Recovery:** Print a clear error message directing the user to enable remote debugging and exit. No automatic recovery possible.

### Rate Limiting / Claude.ai Errors

If Claude.ai returns an error (visible in the page as an error message), detect it in the snap:

```bash
# Check for error states in snap
if echo "$snap" | grep -qi 'Something went wrong\|rate limit\|too many\|error occurred'; then
  log_warn "  Claude.ai error detected"
  write_error_result ... "Claude.ai error"
fi
```

---

## 10. Report Generation

### No Changes to `browser_eval_report.py`

The report script reads `browser-eval-results.json` which has this structure:

```json
{
  "metadata": {
    "eval_type": "browser",
    "platform": "claude.ai",
    "timestamp": "...",
    "prompt_count": 15,
    "backend": "chrome-cdp"
  },
  "results": [
    {
      "prompt_id": "P1",
      "category": "Hallucination Detection",
      "prompt": "...",
      "control": {
        "response": "...",
        "thinking": "...",
        "screenshot": "...",
        "timestamp": "...",
        "status": "ok"
      },
      "treatment": { ... }
    }
  ]
}
```

The only addition is `"backend": "chrome-cdp"` in metadata (informational, not parsed by the report script).

### Updated Methodology Section

The report script's methodology section hardcodes "agent-browser". Add a conditional:

```python
backend = metadata.get("backend", "agent-browser")
if backend == "chrome-cdp":
    lines.append("- **Tool:** chrome-cdp (direct Chrome DevTools Protocol)")
    lines.append("- **Browser:** User's existing Chrome session (remote debugging)")
else:
    lines.append("- **Tool:** agent-browser (automated headless browser)")
```

This is a minor enhancement, not a blocker.

### Skill Detection Upgrade

The detection pattern changes from section 6 above should be applied to `browser_eval_report.py` as a separate commit. Both backends benefit from distinguishing our skill from the built-in one.

---

## 11. Migration Path

### Phase 1: Parallel Operation (this implementation)

- `browser_eval.sh` remains unchanged — agent-browser backend
- `browser_eval_cdp.sh` is the new script — chrome-cdp backend
- Both produce the same JSON format, both use `browser_eval_report.py`
- User chooses which to run based on their setup

### Phase 2: Validation (1-2 runs)

Run both scripts on the same prompts and compare:
- Response extraction fidelity (are responses identical?)
- Thinking extraction (does CDP capture more/less than agent-browser?)
- Timing (confirm the 5-6x speedup)
- Reliability (error rate comparison)

### Phase 3: Default Switch

Once validated:
- `browser_eval_cdp.sh` becomes the recommended script
- `browser_eval.sh` remains as fallback for environments without Chrome remote debugging
- Update CLAUDE.md to reference the CDP script as primary

### Phase 4: Consolidation (optional, not urgent)

If agent-browser is never used again:
- Remove `browser_eval.sh`
- Rename `browser_eval_cdp.sh` to `browser_eval.sh`
- Remove agent-browser from prerequisites in docs

### What NOT to Migrate

- `browser_eval_report.py` — shared, no backend-specific code (except the minor methodology text)
- Prompt definitions — copied into new script (could be extracted to shared file later)
- JSON format — unchanged

---

## 12. Estimated Implementation Effort

### Breakdown

| Task | Effort | Notes |
|------|--------|-------|
| Script skeleton (args, config, logging) | 30 min | Copy structure from browser_eval.sh |
| `cdp_discover_target` + `--setup` mode | 30 min | List, allow, verify |
| `cdp_navigate` | 15 min | SPA nav + verification |
| `cdp_type` + `cdp_submit` | 30 min | ProseMirror workaround, JS escaping edge cases |
| `cdp_wait_for_response` | 20 min | Polling loop, timeout |
| `cdp_extract_response` | 20 min | Port from existing, test selectors |
| `cdp_extract_thinking` | 30 min | Port from existing, test expansion |
| `cdp_toggle_skill` | 20 min | Port from existing |
| `run_prompt` / `run_condition` / `main` | 30 min | Wire everything together |
| JSON assembly + report integration | 15 min | Reuse existing, add backend field |
| Error handling + retry logic | 30 min | Tab loss, nav failure, send button |
| `browser_eval_report.py` skill detection | 30 min | Our-skill vs built-in patterns |
| End-to-end testing (1 full A/B run) | 30 min | At ~25 min for the run itself |
| **Total** | **~5 hours** | Single session |

### Risk Areas

1. **ProseMirror text input** — The `execCommand('insertText')` approach works in the PoC, but long prompts (>500 chars) should be tested. If execCommand truncates, fall back to chunked insertion.

2. **Thinking panel DOM structure** — Claude.ai's thinking panel markup can change between deployments. The `button[aria-expanded]` + grandparent navigation is fragile. If it breaks, fall back to snap text parsing.

3. **"Allow debugging" dialog** — First-time access to a tab requires user interaction. The `--setup` mode handles this, but if Chrome restarts mid-eval, the dialog may reappear. The daemon model mitigates this (daemon stays connected through the eval).

4. **Claude.ai SPA routing** — `window.location.href = '/new'` may not always trigger a clean new-conversation state. If the editor retains state from the previous conversation, test with the full absolute URL `https://claude.ai/new` and verify the editor is empty after navigation.

---

## Appendix A: Command Mapping

Quick reference for porting existing agent-browser calls to chrome-cdp equivalents.

| agent-browser | chrome-cdp | Notes |
|---------------|------------|-------|
| `ab open <url>` | `cdp_cmd eval $T "window.location.href='<url>'"` | SPA navigation |
| `ab snapshot` | `cdp_cmd snap $T` | Accessibility tree |
| `ab snapshot -i` | `cdp_cmd snap $T` | CDP snap is always compact |
| `ab click <ref>` | `cdp_cmd click $T '<selector>'` | CSS selector instead of ref ID |
| `ab fill <ref> <text>` | `cdp_type "<text>"` | execCommand workaround |
| `ab type <ref> <text>` | `cdp_type "<text>"` | execCommand workaround |
| `ab eval "<js>"` | `cdp_cmd eval $T "<js>"` | Direct equivalent |
| `ab press Enter` | `cdp_submit` | Click Send button instead |
| `ab screenshot <path>` | `cdp_cmd shot $T <path>` | Direct equivalent |
| `ab get url` | `cdp_cmd eval $T "window.location.href"` | Via eval |
| `ab close` | `cdp_cmd stop $T` | Stops daemon, does not close tab |
| `ab find role textbox fill <text>` | `cdp_type "<text>"` | Focus + execCommand |
| `ab_headed open <url>` | N/A | Chrome is always visible |
| `ab state save <path>` | N/A | No auth state management |

### Key Behavioral Differences

1. **No ref IDs.** agent-browser assigns `ref=eNN` IDs in snapshots for click/fill targeting. chrome-cdp uses CSS selectors. All click/fill operations must be rewritten to use `document.querySelector(...)` via eval.

2. **No headless mode.** Chrome must be visible. This is actually an advantage for debugging — you can watch the eval run in real time.

3. **No session management.** agent-browser has `--session` for isolating browser instances. chrome-cdp connects to whatever Chrome is running. Only one eval can run at a time (no concurrent sessions).

4. **Persistent tab.** agent-browser opens and closes tabs freely. chrome-cdp works with an existing tab. The script should not close the Claude.ai tab at the end of the eval.

---

## Appendix B: Full Prompt Cycle

Detailed sequence for one prompt, showing every CDP command:

```
1.  cdp_cmd eval $T "window.location.href = 'https://claude.ai/new'"
    sleep 3
2.  cdp_cmd snap $T                          → verify page loaded (check for textbox)
3.  cdp_cmd click $T 'div[contenteditable="true"]'  → focus editor
    sleep 0.3
4.  cdp_cmd eval $T "document.execCommand('insertText', false, '...')"  → type prompt
    sleep 0.5
5.  cdp_cmd eval $T "document.querySelector('button[aria-label=\"Send message\"]').click()"
    sleep 2
6.  POLL: cdp_cmd snap $T                    → check for "Give positive feedback"
    repeat every 3s until found or timeout
7.  cdp_cmd eval $T "..."                    → extract response text (DOM selectors)
8.  cdp_cmd snap $T                          → check for thinking panel
9.  cdp_cmd eval $T "..."                    → expand thinking, extract content
10. cdp_cmd shot $T <screenshot_path>        → save screenshot
11. write_result → JSON file
```

Total per prompt: 30-50s (depends on Claude's response time, typically 15-30s).
