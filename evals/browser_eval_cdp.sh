#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# browser_eval_cdp.sh — Automated Claude.ai A/B testing via Chrome DevTools
#
# Replaces agent-browser with chrome-cdp for 5-6x faster eval runs.
# Connects to the user's running Chrome via remote debugging.
#
# Modes:
#   --setup          Discover Claude.ai tab, verify CDP connection
#   --control        Run control condition only (skill OFF)
#   --treatment      Run treatment condition only (skill ON)
#   --report-only    Regenerate report from existing results JSON
#   (no flag)        Full run: control + treatment + report
#
# Options:
#   --yes            Skip interactive confirmations
#   --prompts N      Run only first N prompts (for smoke testing)
#
# Requirements:
#   - Chrome with remote debugging enabled (chrome://inspect/#remote-debugging)
#   - Node.js 22+ (for cdp.mjs)
#   - Logged into Claude.ai in the running Chrome instance
#   - Python 3 (for report generation)
#
# Compatible with bash 3.2+ (macOS default).
###############################################################################

# --- Configuration -----------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

CDP_SCRIPT="$HOME/.agents/skills/chrome-cdp/scripts/cdp.mjs"
CDP_TARGET=""  # set during discovery

RESULTS_DIR="$SCRIPT_DIR/browser-eval-run-$(date +%Y%m%d-%H%M%S)"
RESULTS_FILE="$SCRIPT_DIR/browser-eval-results.json"
INTER_PROMPT_DELAY=8     # seconds between prompts
RESPONSE_TIMEOUT=120     # max seconds to wait for response completion
POLL_INTERVAL=3          # seconds between completion polls
SCREENSHOT_DIR=""        # set after RESULTS_DIR is created
YES_MODE=false           # --yes: skip interactive confirmations
MAX_PROMPTS=0            # --prompts N: limit prompt count (0 = all)

# --- Test Prompts (P1-P15) ---------------------------------------------------
# 15 prompts selected from the 65-test eval suite for maximum browser eval value.
# Stored as parallel indexed arrays for bash 3.2 compatibility.

PROMPT_COUNT=15

PROMPT_IDS_0="P1"; PROMPT_IDS_1="P2"; PROMPT_IDS_2="P3"; PROMPT_IDS_3="P4"; PROMPT_IDS_4="P5"
PROMPT_IDS_5="P6"; PROMPT_IDS_6="P7"; PROMPT_IDS_7="P8"; PROMPT_IDS_8="P9"; PROMPT_IDS_9="P10"
PROMPT_IDS_10="P11"; PROMPT_IDS_11="P12"; PROMPT_IDS_12="P13"; PROMPT_IDS_13="P14"; PROMPT_IDS_14="P15"

PROMPT_CATEGORIES_0="Hallucination Detection"
PROMPT_CATEGORIES_1="Hallucination Detection"
PROMPT_CATEGORIES_2="Can Claude Do X"
PROMPT_CATEGORIES_3="Can Claude Do X"
PROMPT_CATEGORIES_4="Can Claude Do X"
PROMPT_CATEGORIES_5="Extension Awareness"
PROMPT_CATEGORIES_6="Extension Awareness"
PROMPT_CATEGORIES_7="Cross-Platform Awareness"
PROMPT_CATEGORIES_8="Cross-Platform Awareness"
PROMPT_CATEGORIES_9="Model Selection"
PROMPT_CATEGORIES_10="Architecture Decisions"
PROMPT_CATEGORIES_11="Implementation Guidance"
PROMPT_CATEGORIES_12="Competitor Migration"
PROMPT_CATEGORIES_13="Conversational Platform"
PROMPT_CATEGORIES_14="Conversational Platform"

PROMPT_TEXTS_0="Does Claude remember things between conversations by default? I've been chatting with it for weeks and want to make sure it knows my preferences."
PROMPT_TEXTS_1="I have a production system using Claude Sonnet 3.7. A teammate says we need to migrate urgently. Is Sonnet 3.7 still available? What should we move to?"
PROMPT_TEXTS_2="Can I get Claude to remember things between separate conversations? I'm building a tool where Claude helps with ongoing projects and it's frustrating that it loses context each time."
PROMPT_TEXTS_3="Is there a way to make Claude use tools without me having to define every single one upfront? I have hundreds of MCP tools and the context window overhead is killing me."
PROMPT_TEXTS_4="I heard Claude can now review my pull requests automatically. How does Code Review work? What does it check and how much does it cost?"
PROMPT_TEXTS_5="Every time I edit a Python file, I want to make sure it passes our linting rules and type checks. Right now I keep forgetting to run the checks. Is there a way to automate this?"
PROMPT_TEXTS_6="My team discusses bugs in Slack and then someone has to context-switch to fix them. Is there a way to go straight from a Slack conversation to a code fix?"
PROMPT_TEXTS_7="I installed a skill on Claude.ai by uploading a ZIP file. It works when I ask about the topic, but I can't figure out how to invoke it directly by name. Is there a way to trigger a specific skill on demand?"
PROMPT_TEXTS_8="I'm on Claude.ai and I want to build a multi-step workflow where Claude reviews code, runs tests, and then creates a PR. Is this possible on Claude.ai, or do I need something else?"
PROMPT_TEXTS_9="I need to choose the right Claude model for my app. It needs to handle long documents - 200+ pages - produce detailed analysis, and keep costs reasonable. What would you recommend?"
PROMPT_TEXTS_10="I need to build a quality assurance system that reviews AI-generated content before it goes to customers. The system should check for accuracy, tone, and compliance with our style guide. How would I architect this?"
PROMPT_TEXTS_11="I have a working Claude integration that uses assistant message prefilling to start responses in a specific format. I want to upgrade to Opus 4.6. Anything I should know?"
PROMPT_TEXTS_12="My company uses ChatGPT Teams with custom GPTs. We're considering switching to Claude. What's the equivalent of custom GPTs in the Claude ecosystem?"
PROMPT_TEXTS_13="I need to create a PowerPoint presentation for a client pitch and an Excel spreadsheet with project costings. Can Claude actually generate these file types, or can it only do text?"
PROMPT_TEXTS_14="We want Claude to learn our company's specific terminology and always follow our house style. Can we fine-tune Claude on our company data? What's the best way to customise it for our needs?"

get_prompt_id() { eval echo "\$PROMPT_IDS_$1"; }
get_prompt_category() { eval echo "\$PROMPT_CATEGORIES_$1"; }
get_prompt_text() { eval echo "\$PROMPT_TEXTS_$1"; }

# --- Helpers ------------------------------------------------------------------

log() { echo "[$(date +%H:%M:%S)] $*"; }
log_error() { echo "[$(date +%H:%M:%S)] ERROR: $*" >&2; }
log_warn() { echo "[$(date +%H:%M:%S)] WARN: $*" >&2; }

# --- CDP Core Functions -------------------------------------------------------

cdp_cmd() {
  # Base wrapper: runs cdp.mjs with arguments
  node "$CDP_SCRIPT" "$@"
}

cdp_cmd_with_retry() {
  # Run a CDP command with automatic retry on connection loss
  local result
  if result=$(cdp_cmd "$@" 2>&1); then
    echo "$result"
    return 0
  fi

  # Check if it's a connection error (tab lost)
  if echo "$result" | grep -qi 'Connection closed\|Daemon failed\|No target\|ECONNREFUSED\|socket hang up'; then
    log_warn "  Tab connection lost. Rediscovering..."
    sleep 2
    if cdp_discover_target; then
      # Retry — replace old target in args if present
      local new_args=()
      local replaced=false
      for arg in "$@"; do
        if [[ "$replaced" == "false" && "$arg" != "list" && "$arg" != "--help" && ${#arg} -ge 4 && ! "$arg" =~ ^- ]]; then
          # This might be the old target ID — check if it looks like a hex prefix
          if [[ "$arg" =~ ^[0-9A-Fa-f] ]]; then
            new_args+=("$CDP_TARGET")
            replaced=true
            continue
          fi
        fi
        new_args+=("$arg")
      done
      result=$(cdp_cmd "${new_args[@]}" 2>&1) && { echo "$result"; return 0; }
    fi
  fi

  echo "$result"
  return 1
}

cdp_discover_target() {
  # Find the Claude.ai tab from cdp.mjs list
  local list_output
  list_output=$(cdp_cmd list 2>&1)

  if [[ $? -ne 0 ]] || [[ -z "$list_output" ]]; then
    log_error "CDP list failed. Is Chrome running with remote debugging enabled?"
    log_error "Enable at: chrome://inspect/#remote-debugging"
    return 1
  fi

  # Find the claude.ai line
  local target_line
  target_line=$(echo "$list_output" | grep -i 'claude\.ai' | head -1 || echo "")

  if [[ -z "$target_line" ]]; then
    log_error "No Claude.ai tab found. Open claude.ai in Chrome first."
    log_error "Available tabs:"
    echo "$list_output" >&2
    return 1
  fi

  # Extract the target prefix (first whitespace-delimited token)
  CDP_TARGET=$(echo "$target_line" | awk '{print $1}')
  log "Found Claude.ai tab: $CDP_TARGET"
  log "  $target_line"
}

cdp_navigate() {
  # SPA-friendly navigation via window.location.href
  local url="$1"
  cdp_cmd eval "$CDP_TARGET" "window.location.href = '$url'" >/dev/null 2>&1 || true
  sleep 3
  # Verify
  local current_url
  current_url=$(cdp_cmd eval "$CDP_TARGET" "window.location.href" 2>/dev/null || echo "unknown")
  log "  Navigated to: $current_url"
}

cdp_type() {
  # Type text into ProseMirror editor using document.execCommand
  local text="$1"

  # JS-escape the text for embedding in eval expression
  local escaped_text
  escaped_text=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read())[1:-1])" <<< "$text")

  # Focus the contenteditable div
  cdp_cmd click "$CDP_TARGET" 'div[contenteditable="true"]' >/dev/null 2>&1 || true
  sleep 0.5

  # Insert text via execCommand (ProseMirror intercepts this correctly)
  local result
  result=$(cdp_cmd eval "$CDP_TARGET" "document.execCommand('insertText', false, \"$escaped_text\")" 2>/dev/null || echo "false")

  if [[ "$result" == *"false"* ]]; then
    log_warn "  execCommand returned false — text may not have been inserted"
    # Retry: click again and try once more
    sleep 0.5
    cdp_cmd click "$CDP_TARGET" 'div[contenteditable="true"]' >/dev/null 2>&1 || true
    sleep 0.3
    cdp_cmd eval "$CDP_TARGET" "document.execCommand('insertText', false, \"$escaped_text\")" >/dev/null 2>&1 || true
  fi
}

cdp_submit() {
  # Click the Send button (Enter key doesn't work with ProseMirror)
  local result
  result=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var btn = document.querySelector('button[aria-label=\"Send message\"]');
      if (!btn) {
        btn = document.querySelector('button[aria-label=\"Send Message\"]');
      }
      if (!btn) {
        btn = document.querySelector('button[data-testid=\"send-button\"]');
      }
      if (!btn) return 'NOT_FOUND';
      btn.click();
      return 'SENT';
    })()
  " 2>/dev/null || echo "NOT_FOUND")

  if [[ "$result" == *"NOT_FOUND"* ]]; then
    # Retry after a short wait (ProseMirror may need to sync)
    sleep 0.5
    result=$(cdp_cmd eval "$CDP_TARGET" "
      (function() {
        var btn = document.querySelector('button[aria-label=\"Send message\"]');
        if (!btn) btn = document.querySelector('button[aria-label=\"Send Message\"]');
        if (!btn) btn = document.querySelector('button[data-testid=\"send-button\"]');
        if (!btn) return 'NOT_FOUND';
        btn.click();
        return 'SENT';
      })()
    " 2>/dev/null || echo "NOT_FOUND")

    if [[ "$result" == *"NOT_FOUND"* ]]; then
      log_error "  Send button not found after retry"
      return 1
    fi
  fi

  log "  Prompt submitted"
  return 0
}

# --- Response Detection & Extraction -----------------------------------------

cdp_wait_for_response() {
  local elapsed=0

  log "  Waiting for response (timeout: ${RESPONSE_TIMEOUT}s)..."

  # Initial wait for response to start
  sleep 5
  elapsed=5

  while [ "$elapsed" -lt "$RESPONSE_TIMEOUT" ]; do
    local snap
    snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")

    # Primary signal: feedback buttons only appear after response is complete
    if echo "$snap" | grep -qi 'Give positive feedback\|Give negative feedback'; then
      log "  Response complete (feedback buttons at ${elapsed}s)"
      return 0
    fi

    # Secondary: "Copy" present AND no "Stop" button
    if echo "$snap" | grep -qi 'Copy' && ! echo "$snap" | grep -qi 'Stop response'; then
      # Extra verify: check there's substantial content
      local has_content
      has_content=$(cdp_cmd eval "$CDP_TARGET" "
        (function() {
          var els = document.querySelectorAll('[data-testid=\"chat-message-text\"], div.font-claude-message, div.prose');
          for (var i = 0; i < els.length; i++) {
            if (els[i].innerText && els[i].innerText.length > 50) return 'yes';
          }
          return 'no';
        })()
      " 2>/dev/null || echo "no")
      if [[ "$has_content" == *"yes"* ]]; then
        log "  Response complete (Copy present, no Stop at ${elapsed}s)"
        return 0
      fi
    fi

    # Check for Claude.ai error states
    if echo "$snap" | grep -qi 'Something went wrong\|rate limit\|too many requests\|error occurred'; then
      log_warn "  Claude.ai error detected at ${elapsed}s"
      return 1
    fi

    sleep "$POLL_INTERVAL"
    elapsed=$((elapsed + POLL_INTERVAL))
  done

  log_warn "  Response timeout after ${RESPONSE_TIMEOUT}s — capturing partial"
  return 0
}

cdp_extract_response() {
  # Strategy 1: Find assistant message via action-bar-copy anchor
  # Only assistant messages contain the copy button (data-testid="action-bar-copy")
  local response_text
  response_text=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      var copyBtns = document.querySelectorAll('[data-testid=\"action-bar-copy\"]');
      if (copyBtns.length === 0) return 'EXTRACTION_FAILED';

      // The last copy button is in the most recent assistant message
      var copyBtn = copyBtns[copyBtns.length - 1];

      // Walk up to the message container (a direct child of the conversation div)
      var el = copyBtn;
      for (var i = 0; i < 10; i++) {
        el = el.parentElement;
        if (!el) break;
        if (el.innerText && el.innerText.length > 100) {
          var allText = el.innerText;

          // Strip the thinking summary that appears at top of assistant message
          var btns = el.querySelectorAll('button[aria-expanded]');
          for (var j = 0; j < btns.length; j++) {
            var t = btns[j].textContent || '';
            if (t.length > 15 && t.length < 300) {
              // Remove thinking summary (appears twice: button + static text)
              allText = allText.replace(t, '').replace(t, '');
              break;
            }
          }

          // Strip trailing UI button labels
          allText = allText.replace(/Copy\\s*$/m, '').replace(/Retry\\s*$/m, '').trim();
          if (allText.length > 50) return allText;
        }
      }
      return 'EXTRACTION_FAILED';
    })()
  " 2>/dev/null || echo "EXTRACTION_FAILED")

  if [[ "$response_text" != "EXTRACTION_FAILED" && -n "$response_text" ]]; then
    echo "$response_text"
    return 0
  fi

  # Strategy 2: Parse snap output
  log_warn "  DOM extraction failed, falling back to snap"
  local snap
  snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")
  if [[ -n "$snap" ]]; then
    echo "$snap"
    return 0
  fi

  log_warn "  All extraction strategies failed"
  echo "EXTRACTION_FAILED"
}

cdp_extract_thinking() {
  local snap
  snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")

  if [[ -z "$snap" ]]; then
    echo ""
    return 0
  fi

  # Save snap for debugging
  echo "$snap" > "$RESULTS_DIR/last_thinking_snapshot.txt" 2>/dev/null || true

  # Step 1: Find the thinking toggle button via DOM
  # The thinking toggle is a button[aria-expanded] whose textContent is a summary
  # sentence (e.g. "Investigated persistent memory solutions and API-level approaches").
  # It's NOT a UI button like Copy/Retry — those have short or empty text.
  # We also scope to the assistant message container using action-bar-copy as anchor.
  local expanded
  expanded=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      // Scope to the most recent assistant message
      var copyBtns = document.querySelectorAll('[data-testid=\"action-bar-copy\"]');
      var scope = document;
      if (copyBtns.length > 0) {
        var el = copyBtns[copyBtns.length - 1];
        for (var i = 0; i < 10; i++) {
          el = el.parentElement;
          if (!el) break;
          if (el.innerText && el.innerText.length > 100) { scope = el; break; }
        }
      }

      var buttons = scope.querySelectorAll('button[aria-expanded]');
      for (var i = 0; i < buttons.length; i++) {
        var text = (buttons[i].textContent || '').trim();
        // Thinking summaries are 15-300 chars and read like sentences
        if (text.length > 15 && text.length < 300 &&
            !text.match(/^(Copy|Retry|Edit|Send|Stop|Continue|Menu|More|New|Share|Search|LJ)/i)) {
          if (buttons[i].getAttribute('aria-expanded') === 'false') {
            buttons[i].click();
          }
          return 'FOUND:' + text;
        }
      }
      return 'NOT_FOUND';
    })()
  " 2>/dev/null || echo "NOT_FOUND")

  if [[ "$expanded" == *"NOT_FOUND"* ]]; then
    echo ""
    return 0
  fi

  # Extract the summary from the FOUND: prefix
  local thinking_summary="${expanded#FOUND:}"
  sleep 1.5

  # Step 2: Extract expanded thinking content
  local thinking_text
  thinking_text=$(cdp_cmd eval "$CDP_TARGET" "
    (function() {
      // Find the expanded thinking button within the assistant message
      var copyBtns = document.querySelectorAll('[data-testid=\"action-bar-copy\"]');
      var scope = document;
      if (copyBtns.length > 0) {
        var el = copyBtns[copyBtns.length - 1];
        for (var i = 0; i < 10; i++) {
          el = el.parentElement;
          if (!el) break;
          if (el.innerText && el.innerText.length > 100) { scope = el; break; }
        }
      }

      var btns = scope.querySelectorAll('button[aria-expanded=\"true\"]');
      for (var b = 0; b < btns.length; b++) {
        var btn = btns[b];
        var text = (btn.textContent || '').trim();
        if (text.length < 15 || text.length > 300) continue;
        if (text.match(/^(Copy|Retry|Edit|Send|Stop|Continue|Menu|More|LJ)/i)) continue;

        var gp = btn.parentElement ? btn.parentElement.parentElement : null;
        if (!gp) continue;

        var parts = [];
        var children = gp.children;
        for (var i = 2; i < children.length; i++) {
          var ct = children[i].innerText;
          if (ct && ct.trim().length > 0) {
            parts.push(ct.trim());
          }
        }
        if (parts.length > 0) return parts.join('\\n');

        // Fallback: return the button text as summary
        return '[Thinking summary] ' + text;
      }
      return '';
    })()
  " 2>/dev/null || echo "")

  # If expanded content extraction failed, use the summary
  if [[ -z "$thinking_text" || "$thinking_text" == '""' ]]; then
    if [[ -n "$thinking_summary" ]]; then
      thinking_text="[Thinking summary] $thinking_summary"
    fi
  fi

  echo "$thinking_text"
}

# --- Skill Toggle -------------------------------------------------------------

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
  " >/dev/null 2>&1 || true
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
  " >/dev/null 2>&1 || true
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

# --- Run Single Prompt --------------------------------------------------------

run_prompt() {
  local prompt_id="$1"
  local condition="$2"  # "control" or "treatment"
  local prompt_text="$3"
  local category="$4"

  local result_file="$RESULTS_DIR/${prompt_id}_${condition}.json"
  local screenshot_path="$SCREENSHOT_DIR/${prompt_id}_${condition}.png"

  log "--- $prompt_id ($condition): $category ---"
  log "  Prompt: $(echo "$prompt_text" | cut -c1-80)..."

  # Navigate to new chat
  log "  Navigating to claude.ai/new..."
  cdp_navigate "https://claude.ai/new"
  sleep 2

  # Verify page loaded — check for editor
  local page_snap
  page_snap=$(cdp_cmd snap "$CDP_TARGET" 2>/dev/null || echo "")
  if [[ -z "$page_snap" ]]; then
    log_error "  Empty snapshot — page may not have loaded"
    write_error_result "$result_file" "$prompt_id" "$condition" "$category" "$prompt_text" "Empty snapshot"
    return 0
  fi

  # Type the prompt
  log "  Typing prompt..."
  cdp_type "$prompt_text"
  sleep 0.5

  # Submit
  log "  Submitting..."
  if ! cdp_submit; then
    log_error "  Submit failed"
    write_error_result "$result_file" "$prompt_id" "$condition" "$category" "$prompt_text" "Submit failed"
    return 0
  fi
  sleep 2

  # Wait for response
  if ! cdp_wait_for_response; then
    log_warn "  Response detection returned error — capturing what we have"
  fi

  # Extract response
  log "  Extracting response..."
  local response_text
  response_text=$(cdp_extract_response)

  # Extract thinking
  log "  Extracting thinking..."
  local thinking_text
  thinking_text=$(cdp_extract_thinking)

  # Screenshot
  log "  Taking screenshot..."
  cdp_cmd shot "$CDP_TARGET" "$screenshot_path" >/dev/null 2>&1 || log_warn "  Screenshot failed"

  # Write result
  write_result "$result_file" "$prompt_id" "$condition" "$category" "$prompt_text" \
    "$response_text" "$thinking_text" "$screenshot_path"

  log "  Result saved: $result_file"
}

# --- JSON Output Helpers ------------------------------------------------------

json_escape() {
  python3 -c "
import json, sys
text = sys.stdin.read()
print(json.dumps(text), end='')
" <<< "$1"
}

write_result() {
  local file="$1" pid="$2" condition="$3" category="$4" prompt="$5"
  local response="$6" thinking="$7" screenshot="$8"

  local j_prompt j_response j_thinking j_screenshot j_category
  j_prompt=$(json_escape "$prompt")
  j_response=$(json_escape "$response")
  j_thinking=$(json_escape "$thinking")
  j_screenshot=$(json_escape "$screenshot")
  j_category=$(json_escape "$category")

  cat > "$file" << ENDJSON
{
  "prompt_id": "$pid",
  "condition": "$condition",
  "category": $j_category,
  "prompt": $j_prompt,
  "response": $j_response,
  "thinking": $j_thinking,
  "screenshot": $j_screenshot,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "ok"
}
ENDJSON
}

write_error_result() {
  local file="$1" pid="$2" condition="$3" category="$4" prompt="$5" error="$6"

  local j_prompt j_error j_category
  j_prompt=$(json_escape "$prompt")
  j_error=$(json_escape "$error")
  j_category=$(json_escape "$category")

  cat > "$file" << ENDJSON
{
  "prompt_id": "$pid",
  "condition": "$condition",
  "category": $j_category,
  "prompt": $j_prompt,
  "response": "",
  "thinking": "",
  "screenshot": "",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "error",
  "error": $j_error
}
ENDJSON
}

# --- Assemble Results ---------------------------------------------------------

assemble_results() {
  log "Assembling results into $RESULTS_FILE..."

  python3 -c "
import json, glob, os, sys

results_dir = sys.argv[1]
output_file = sys.argv[2]
prompt_count = int(sys.argv[3])

fragments = sorted(glob.glob(os.path.join(results_dir, 'P*_*.json')))

if not fragments:
    print('No result fragments found', file=sys.stderr)
    sys.exit(1)

by_prompt = {}
for f in fragments:
    with open(f) as fh:
        data = json.load(fh)
    pid = data['prompt_id']
    cond = data['condition']
    if pid not in by_prompt:
        by_prompt[pid] = {
            'prompt_id': pid,
            'category': data.get('category', ''),
            'prompt': data.get('prompt', ''),
        }
    by_prompt[pid][cond] = {
        'response': data.get('response', ''),
        'thinking': data.get('thinking', ''),
        'screenshot': data.get('screenshot', ''),
        'timestamp': data.get('timestamp', ''),
        'status': data.get('status', 'unknown'),
        'error': data.get('error', ''),
    }

output = {
    'metadata': {
        'eval_type': 'browser',
        'platform': 'claude.ai',
        'backend': 'chrome-cdp',
        'timestamp': max(
            d.get(c, {}).get('timestamp', '')
            for d in by_prompt.values()
            for c in ('control', 'treatment')
        ),
        'prompt_count': len(by_prompt),
        'note': f'n={prompt_count} qualitative assessment',
    },
    'results': [by_prompt[pid] for pid in sorted(by_prompt.keys())],
}

with open(output_file, 'w') as fh:
    json.dump(output, fh, indent=2)

print(f'Assembled {len(fragments)} fragments into {output_file}')
" "$RESULTS_DIR" "$RESULTS_FILE" "$effective_prompt_count"
}

# --- Run Condition (control or treatment) -------------------------------------

run_condition() {
  local condition="$1"

  log "========================================="
  log "  Running condition: $condition ($effective_prompt_count prompts)"
  log "========================================="

  local succeeded=0
  local failed=0
  local i=0
  local start_time
  start_time=$(date +%s)

  while [ "$i" -lt "$effective_prompt_count" ]; do
    local pid category prompt_text
    pid=$(get_prompt_id "$i")
    category=$(get_prompt_category "$i")
    prompt_text=$(get_prompt_text "$i")

    log ""
    if run_prompt "$pid" "$condition" "$prompt_text" "$category"; then
      local result_file="$RESULTS_DIR/${pid}_${condition}.json"
      if [[ -f "$result_file" ]]; then
        local status
        status=$(python3 -c "import json; print(json.load(open('$result_file'))['status'])" 2>/dev/null || echo "unknown")
        if [[ "$status" == "ok" ]]; then
          succeeded=$((succeeded + 1))
        else
          failed=$((failed + 1))
        fi
      fi
    else
      failed=$((failed + 1))
    fi

    # Inter-prompt delay (skip after last prompt)
    local last_idx=$((effective_prompt_count - 1))
    if [ "$i" -ne "$last_idx" ]; then
      log "  Waiting ${INTER_PROMPT_DELAY}s before next prompt..."
      sleep "$INTER_PROMPT_DELAY"
    fi

    i=$((i + 1))
  done

  local end_time elapsed_total
  end_time=$(date +%s)
  elapsed_total=$((end_time - start_time))

  log ""
  log "$condition complete: $succeeded succeeded, $failed failed (${elapsed_total}s total)"
}

# --- Report Generation --------------------------------------------------------

generate_report() {
  if [[ ! -f "$RESULTS_FILE" ]]; then
    log_error "No results file found at $RESULTS_FILE"
    exit 1
  fi

  log "Generating report..."
  python3 "$SCRIPT_DIR/browser_eval_report.py" "$RESULTS_FILE"
}

# --- Setup Mode ---------------------------------------------------------------

do_setup() {
  log "=== Chrome CDP Setup ==="
  log ""
  log "Checking prerequisites..."

  # Check Node.js version
  local node_version
  node_version=$(node --version 2>/dev/null || echo "")
  if [[ -z "$node_version" ]]; then
    log_error "Node.js not found. Install Node.js 22+."
    exit 1
  fi
  log "Node.js: $node_version"

  # Check cdp.mjs exists
  if [[ ! -f "$CDP_SCRIPT" ]]; then
    log_error "cdp.mjs not found at $CDP_SCRIPT"
    log_error "Install chrome-cdp skill first."
    exit 1
  fi
  log "CDP script: $CDP_SCRIPT"

  # Try to list tabs
  log ""
  log "Discovering Chrome tabs..."
  local list_output
  list_output=$(cdp_cmd list 2>&1) || true

  if [[ -z "$list_output" ]] || echo "$list_output" | grep -qi 'error\|ECONNREFUSED\|not found'; then
    log_error "Cannot connect to Chrome."
    log_error ""
    log_error "Ensure remote debugging is enabled:"
    log_error "  1. Open chrome://inspect/#remote-debugging in Chrome"
    log_error "  2. Toggle the switch ON"
    log_error "  3. Re-run this setup"
    exit 1
  fi

  log "Available tabs:"
  echo "$list_output"
  log ""

  # Find Claude.ai tab
  if cdp_discover_target; then
    log ""
    log "Testing CDP connection..."

    # Run a simple eval to trigger the "Allow debugging?" dialog
    local test_result
    test_result=$(cdp_cmd eval "$CDP_TARGET" "document.title" 2>&1 || echo "FAILED")

    if [[ "$test_result" == *"FAILED"* ]] || [[ -z "$test_result" ]]; then
      log_warn "First command failed — Chrome may be showing 'Allow debugging?' dialog."
      log "Click 'Allow' in Chrome, then press Enter here."
      read -r
      test_result=$(cdp_cmd eval "$CDP_TARGET" "document.title" 2>/dev/null || echo "FAILED")
    fi

    if [[ "$test_result" != *"FAILED"* && -n "$test_result" ]]; then
      log "Connection verified! Page title: $test_result"
      log ""
      log "Setup complete. Run the eval with:"
      log "  ./browser_eval_cdp.sh           # Full A/B run"
      log "  ./browser_eval_cdp.sh --prompts 3  # Smoke test (3 prompts)"
    else
      log_error "Could not connect to Claude.ai tab."
      log_error "Ensure Chrome's debugging dialog is accepted."
    fi
  fi
}

# --- Main ---------------------------------------------------------------------

show_usage() {
  echo "Usage: $0 [mode] [options]"
  echo ""
  echo "Automated Claude.ai A/B testing via Chrome DevTools Protocol."
  echo ""
  echo "Modes:"
  echo "  (no flag)      Full run: control + treatment + report"
  echo "  --setup        Verify Chrome connection, trigger Allow dialog"
  echo "  --control      Run control condition only (skill OFF)"
  echo "  --treatment    Run treatment condition only (skill ON)"
  echo "  --report-only  Regenerate report from existing browser-eval-results.json"
  echo ""
  echo "Options:"
  echo "  --yes          Skip interactive confirmations"
  echo "  --prompts N    Run only first N prompts (default: all 15)"
}

# Effective prompt count (may be overridden by --prompts)
effective_prompt_count=$PROMPT_COUNT

main() {
  local mode="full"

  # Parse flags
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --yes|-y)
        YES_MODE=true
        shift
        ;;
      --prompts)
        MAX_PROMPTS="$2"
        shift 2
        ;;
      --help|-h)
        show_usage
        exit 0
        ;;
      *)
        mode="$1"
        shift
        ;;
    esac
  done

  # Apply prompt limit
  if [[ "$MAX_PROMPTS" -gt 0 ]] && [[ "$MAX_PROMPTS" -lt "$PROMPT_COUNT" ]]; then
    effective_prompt_count=$MAX_PROMPTS
  fi

  case "$mode" in
    --setup)
      do_setup
      exit 0
      ;;
    --report-only)
      generate_report
      exit 0
      ;;
    --control)
      mkdir -p "$RESULTS_DIR"
      SCREENSHOT_DIR="$RESULTS_DIR/screenshots"
      mkdir -p "$SCREENSHOT_DIR"
      cdp_discover_target
      run_condition "control"
      assemble_results
      generate_report
      ;;
    --treatment)
      mkdir -p "$RESULTS_DIR"
      SCREENSHOT_DIR="$RESULTS_DIR/screenshots"
      mkdir -p "$SCREENSHOT_DIR"
      cdp_discover_target
      run_condition "treatment"
      assemble_results
      generate_report
      ;;
    full)
      mkdir -p "$RESULTS_DIR"
      SCREENSHOT_DIR="$RESULTS_DIR/screenshots"
      mkdir -p "$SCREENSHOT_DIR"
      cdp_discover_target

      local run_start
      run_start=$(date +%s)

      log ""
      log "========================================="
      log "  PHASE 1: CONTROL (skill OFF)"
      log "========================================="
      log ""

      # Toggle skill OFF
      log "Disabling skill for control condition..."
      if ! cdp_toggle_skill "off"; then
        log_error "Failed to disable skill automatically."
        if [[ "$YES_MODE" != "true" ]]; then
          echo -n "Manually disable the skill, then press Enter (or Ctrl+C to abort)... "
          read -r
        else
          log_error "Cannot proceed in --yes mode without working toggle. Aborting."
          exit 1
        fi
      fi

      # Navigate back to chat
      cdp_navigate "https://claude.ai/new"
      sleep 2

      run_condition "control"

      log ""
      log "========================================="
      log "  PHASE 2: TREATMENT (skill ON)"
      log "========================================="
      log ""

      # Toggle skill ON
      log "Enabling skill for treatment condition..."
      if ! cdp_toggle_skill "on"; then
        log_error "Failed to enable skill automatically."
        if [[ "$YES_MODE" != "true" ]]; then
          echo -n "Manually enable the skill, then press Enter (or Ctrl+C to abort)... "
          read -r
        else
          log_error "Cannot proceed in --yes mode without working toggle. Aborting."
          exit 1
        fi
      fi

      # Navigate back to chat
      cdp_navigate "https://claude.ai/new"
      sleep 2

      run_condition "treatment"

      assemble_results
      generate_report

      local run_end run_elapsed
      run_end=$(date +%s)
      run_elapsed=$((run_end - run_start))

      log ""
      log "========================================="
      log "  EVAL COMPLETE (${run_elapsed}s total)"
      log "========================================="
      log "Results:    $RESULTS_FILE"
      log "Run dir:    $RESULTS_DIR"
      log "Prompts:    $effective_prompt_count"
      ;;
    *)
      show_usage
      exit 1
      ;;
  esac
}

main "$@"
