#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
export SEC_USER_AGENT="${SEC_USER_AGENT:-CapitalDealflow/0.1 (you@example.com)}"

python -m src.edgar_watcher --lookback-days "${LOOKBACK_DAYS:-7}" --max-hits "${MAX_HITS:-25}" --energy-only --min-score 0.25
python -m src.promote_signals --min-score "${MIN_SCORE:-0.35}"
python -m src.matcher --top-n "${TOP_N:-5}"

echo
echo "Done. Import CSVs from data/exports/ into Airtable, or review JSON in data/."