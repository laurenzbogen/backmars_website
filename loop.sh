#!/usr/bin/env bash
LOG=/logs/build.log
INTERVAL=30

while true; do
    echo "=== $(date -Iseconds) build start ===" >> "$LOG"
    python build.py >> "$LOG" 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then
        echo "=== $(date -Iseconds) build ok ===" >> "$LOG"
    else
        echo "=== $(date -Iseconds) build FAILED (exit $rc) ===" >> "$LOG"
    fi
    sleep "$INTERVAL"
done
