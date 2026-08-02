# Capital Dealflow Toolkit

Starter tools for a mining / oil & gas capital intermediary:

1. **Schema** — Postgres + Airtable model for opportunities, providers, matches, signals
2. **EDGAR watcher** — scans SEC filings for “needs capital” language
3. **Promote + match** — turns signals into opportunities and ranks likely capital desks

This is an MVP research workflow, not a PitchBook replacement.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Use your real email in the User-Agent (SEC requirement)
export SEC_USER_AGENT="CapitalDealflow/0.1 (you@example.com)"

# 1) Pull funding-need signals from EDGAR
python -m src.edgar_watcher --lookback-days 7 --max-hits 25 --energy-only

# Optional: slower but better keyword hits from filing text
# python -m src.edgar_watcher --lookback-days 5 --max-hits 15 --fetch-text --energy-only

# 2) Promote stronger signals into opportunities
python -m src.promote_signals --min-score 0.35

# 3) Match opportunities to seed capital providers
python -m src.matcher --top-n 5
```

Or run:

```bash
./scripts/run_pipeline.sh
```

Outputs land in `data/`:

- `signals.json` + `exports/signals.csv`
- `opportunities.json` + `exports/opportunities.csv`
- `matches.json` + `exports/matches.csv`

Import the CSVs into Airtable, or load `schema/postgres.sql` into Postgres.

## Schema

| Table | Purpose |
|---|---|
| `companies` | Sponsors / issuers |
| `signals` | Raw EDGAR (or other) alerts |
| `opportunities` | Deals that may need funding |
| `providers` | Capital desks (e.g. First Citizens Energy Finance) |
| `provider_contacts` | People |
| `matches` | Ranked opportunity ↔ provider suggestions |
| `interactions` | Outreach log |

See `schema/airtable.md` for the Airtable field map.

## Matching logic

Score boosts for:

- ask type ↔ capital type (RBL → bank_rbl / private credit)
- sector fit
- stage fit
- check-size overlap (when known)
- broker-friendly flag (only when verified)

`broker_friendly` in seed data defaults to **unknown** until a desk confirms they take intermediary intros.

Equity / securities signals flip `needs_bd_license=true` so you don’t casually commission those without proper licensing.

## Seed providers

`data/seed_providers.json` includes First Citizens desks plus placeholders. Replace generics with real funds/banks from PitchBook, Preqin, or Mergr.

## Compliance note

Bank commercial loan introductions ≠ securities placement. Success fees on equity / note placements can require broker-dealer registration. Get counsel before taking % fees on securities deals.
