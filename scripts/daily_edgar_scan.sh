#!/usr/bin/env bash
# Daily EDGAR mining-stage lead scan (intended for 6:30 PM America/New_York)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export SEC_USER_AGENT="${SEC_USER_AGENT:-CapitalDealflow/0.1 (albert.c.ellis3@gmail.com)}"
export PYTHONPATH="$ROOT"
export TZ="${TZ:-America/New_York}"

LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR" "$ROOT/data/exports" "$ROOT/docs/leads"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/edgar_daily_${STAMP}.log"

{
  echo "=== EDGAR daily scan start $(date) ==="

  export PATH="$HOME/.local/bin:$PATH"
  PY="python3"
  if [[ -x "$ROOT/.venv/bin/python" ]] && "$ROOT/.venv/bin/python" -c "import requests" 2>/dev/null; then
    PY="$ROOT/.venv/bin/python"
  fi
  if ! "$PY" -c "import requests" 2>/dev/null; then
    pip3 install --user -q requests python-dateutil
  fi

  "$PY" -m src.edgar_watcher \
    --mining-stages \
    --lookback-days "${LOOKBACK_DAYS:-3}" \
    --max-hits "${MAX_HITS:-20}" \
    --min-score "${MIN_SCORE:-0.18}"

  # Curate mining-leaning rows into dated + latest CSV under docs/leads
  "$PY" - <<'PY'
import csv
import json
from pathlib import Path
from datetime import datetime

root = Path(".")
signals = json.loads((root / "data" / "signals.json").read_text()).get("signals", [])
allow = (
    "mining", "miner", "gold", "copper", "ore", "resources", "metals",
    "hycroft", "ramaco", "contango", "hecla", "coeur", "lithium", "silver",
)
strong = {
    "preliminary economic assessment",
    "pre-feasibility",
    "prefeasibility",
    "feasibility study",
    "bankable feasibility",
    "streaming agreement",
    "metal stream",
    "royalty financing",
    "nsr royalty",
    "mineral resource",
    "drill program",
    "earn-in",
    "farm-in",
}
deny = (
    "mortgage", "bank5", "transmission", "electro sensors", "contextlogic",
    "csw industrials", "hyperliquid", "wells fargo commercial", "pharmaceutical",
    "therapies", "superfood", "shrimp", "heartsciences", "naturalshrimp",
)

curated = []
for s in signals:
    name = (s.get("company_name") or "").lower()
    if any(d in name for d in deny):
        continue
    if (
        s.get("sector_guess") == "mining"
        or any(a in name for a in allow)
        or strong.intersection(s.get("keywords_hit") or [])
    ):
        curated.append(s)

curated.sort(key=lambda s: (-(s.get("score") or 0), s.get("stage_guess") or ""))
fields = [
    "score", "stage_guess", "mode_guess", "ask_type_guess", "company_name",
    "ticker", "form_type", "filed_at", "keywords_hit", "filing_url",
]
stamp = datetime.now().strftime("%Y-%m-%d")
out_dated = root / "docs" / "leads" / f"edgar_daily_{stamp}.csv"
out_latest = root / "docs" / "leads" / "edgar_daily_latest.csv"
for path in (out_dated, out_latest):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for s in curated:
            row = {k: s.get(k) for k in fields}
            row["keywords_hit"] = "; ".join(
                k for k in (s.get("keywords_hit") or [])
                if " AND " not in k and not k.startswith('"')
            )
            w.writerow(row)
print(f"Curated {len(curated)} mining-leaning leads -> {out_latest}")
for s in curated[:15]:
    print(
        f"  {s.get('score',0):.2f} | {s.get('stage_guess')} | {s.get('mode_guess')} | "
        f"{(s.get('company_name') or '')[:40]} | {', '.join((s.get('keywords_hit') or [])[:3])}"
    )
PY

  echo "=== EDGAR daily scan end $(date) ==="
} 2>&1 | tee "$LOG"

# Keep only last 30 logs
ls -1t "$LOG_DIR"/edgar_daily_*.log 2>/dev/null | tail -n +31 | xargs -r rm --
