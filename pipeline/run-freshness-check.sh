#!/bin/bash
# run-freshness-check.sh -- Launchd wrapper for freshness pipeline
# Called by: ~/Library/LaunchAgents/com.claude-capabilities.freshness-check.plist
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONUNBUFFERED=1

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env" 2>/dev/null || true
    set +a
fi

# Ensure log directory exists
mkdir -p "$PROJECT_DIR/logs"
LOG_FILE="$PROJECT_DIR/logs/freshness-check.log"

# Activate virtualenv if present
if [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
fi

echo ""
echo "=========================================="
echo "Freshness Check -- $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# Run the pipeline (as a module so relative imports work)
python3 -m pipeline.freshness_check 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "Finished at $(date '+%Y-%m-%d %H:%M:%S') (exit code: $EXIT_CODE)"

# Log rotation: keep last 10,000 lines
if [ -f "$LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$LOG_FILE")
    if [ "$LINE_COUNT" -gt 10000 ]; then
        tail -5000 "$LOG_FILE" > "$LOG_FILE.tmp"
        mv "$LOG_FILE.tmp" "$LOG_FILE"
        echo "[log-rotation] Trimmed log to 5000 lines (was $LINE_COUNT)"
    fi
fi

exit $EXIT_CODE
