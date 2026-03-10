#!/bin/bash
# Inject condensed capabilities reference into Claude's session context.
# Called by SessionStart hook — outputs JSON with additionalContext.

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$0")")}"
QUICK_REF="$PLUGIN_ROOT/data/quick-reference.md"

if [ ! -f "$QUICK_REF" ]; then
  exit 0
fi

CONTENT=$(cat "$QUICK_REF")

# Output as JSON with additionalContext for SessionStart
# Uses jq if available, falls back to python3
if command -v jq &>/dev/null; then
  jq -Rs '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: .}}' <<< "$CONTENT"
else
  python3 -c "
import json, sys
content = sys.stdin.read()
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': content
    }
}))
" <<< "$CONTENT"
fi
