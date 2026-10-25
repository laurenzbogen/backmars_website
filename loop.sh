#!/usr/bin/env bash
LOG=/logs/build.log
INTERVAL=30
MAX_BYTES=$((5 * 1024 * 1024))   # rotate at 5 MB
KEEP=5                           # keep build.log.1 ... build.log.5

rotate_log() {
    [ -f "$LOG" ] || return
    local size
    size=$(stat -c %s "$LOG")    # macOS/BSD: stat -f %z
    [ "$size" -lt "$MAX_BYTES" ] && return

    for ((i = KEEP - 1; i >= 1; i--)); do
        [ -f "$LOG.$i" ] && mv -f "$LOG.$i" "$LOG.$((i + 1))"
    done
    mv -f "$LOG" "$LOG.1"
}

while true; do
    rotate_log
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
