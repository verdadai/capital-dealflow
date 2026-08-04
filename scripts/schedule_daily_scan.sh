#!/usr/bin/env bash
# Keeps a loop alive that runs the EDGAR scan at 6:30 PM America/New_York daily.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export TZ=America/New_York
export SEC_USER_AGENT="${SEC_USER_AGENT:-CapitalDealflow/0.1 (albert.c.ellis3@gmail.com)}"
export PYTHONPATH="$ROOT"
export PATH="$HOME/.local/bin:$PATH"

LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR"

echo "[scheduler] started $(date) — will fire daily at 18:30 America/New_York"

while true; do
  NOW_EPOCH="$(date +%s)"
  # next 18:30 local
  TARGET="$(date -d 'today 18:30' +%s)"
  if (( NOW_EPOCH >= TARGET )); then
    TARGET="$(date -d 'tomorrow 18:30' +%s)"
  fi
  SLEEP=$(( TARGET - NOW_EPOCH ))
  echo "[scheduler] sleeping ${SLEEP}s until $(date -d "@$TARGET") ($(date))"
  sleep "$SLEEP"
  echo "[scheduler] firing scan at $(date)"
  LOOKBACK_DAYS=3 MAX_HITS=20 "$ROOT/scripts/daily_edgar_scan.sh" \
    >> "$LOG_DIR/scheduler.log" 2>&1 || echo "[scheduler] scan failed at $(date)" >> "$LOG_DIR/scheduler.log"
done
