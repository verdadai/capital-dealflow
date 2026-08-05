#!/usr/bin/env bash
# Runs the EDGAR scan at 6:30 PM America/New_York daily.
# Uses short sleeps + clock checks so a frozen/resumed VM still fires after 18:30.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export TZ=America/New_York
export SEC_USER_AGENT="${SEC_USER_AGENT:-CapitalDealflow/0.1 (albert.c.ellis3@gmail.com)}"
export PYTHONPATH="$ROOT"
export PATH="$HOME/.local/bin:$PATH"

LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR"
STATE_FILE="$LOG_DIR/last_scheduled_run_day.txt"

echo "[scheduler] started $(date) — target daily 18:30 America/New_York"

last_run_day=""
if [[ -f "$STATE_FILE" ]]; then
  last_run_day="$(cat "$STATE_FILE" || true)"
fi

while true; do
  day="$(date +%F)"
  hm="$(date +%H%M)"

  # Fire once per local day at/after 18:30
  if (( 10#$hm >= 1830 )) && [[ "$day" != "$last_run_day" ]]; then
    echo "[scheduler] firing scan at $(date)"
    if LOOKBACK_DAYS=3 MAX_HITS=20 "$ROOT/scripts/daily_edgar_scan.sh" \
      >> "$LOG_DIR/scheduler.log" 2>&1; then
      echo "$day" > "$STATE_FILE"
      last_run_day="$day"
      echo "[scheduler] success for $day at $(date)"
    else
      echo "[scheduler] scan failed at $(date)" | tee -a "$LOG_DIR/scheduler.log"
      # Retry in 15 minutes if failed
      sleep 900
      continue
    fi
  fi

  # Sleep in short chunks so resume-from-freeze can't miss the window forever
  sleep 60
done
