from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))

# SEC requires a descriptive User-Agent with a contact email.
SEC_USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "CapitalDealflow/0.1 (research@example.com)",
)

EDGAR_LOOKBACK_DAYS = int(os.getenv("EDGAR_LOOKBACK_DAYS", "7"))
EDGAR_MAX_HITS_PER_QUERY = int(os.getenv("EDGAR_MAX_HITS_PER_QUERY", "40"))

# Energy / mining-ish SIC codes (approximate buckets used for scoring boosts)
ENERGY_MINING_SICS = {
    "1000",
    "1040",
    "1090",
    "1220",
    "1221",
    "1311",
    "1381",
    "1382",
    "1389",
    "1400",
    "2911",
    "3330",
    "3334",
    "4911",
    "4931",
    "5171",
    "5172",
}