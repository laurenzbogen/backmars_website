#!/usr/bin/env bash
LOG=/logs/build.log
INTERVAL=30

while true; do
    echo "=== $(date -Iseconds) build start ===" >> "$LOG"
    if python build.py >> "$LOG" 2>&1; then
        echo "=== $(date -Iseconds) build ok ===" >> "$LOG"
    else
        echo "=== $(date -Iseconds) build FAILED (exit $?) ===" >> "$LOG"
    fi
    sleep "$INTERVAL"
done
