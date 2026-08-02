# Mining-by-stage EDGAR hits — Aug 2026 pull

Generated with:

```bash
python -m src.edgar_watcher --mining-stages --lookback-days 220 --max-hits 15 --min-score 0.18
```

See also: [`../research/EDGAR_Form_Types_and_Mining_Stages.md`](../research/EDGAR_Form_Types_and_Mining_Stages.md)  
CSV: [`edgar_mining_by_stage_2026-08-02.csv`](edgar_mining_by_stage_2026-08-02.csv)

## Form cheat-sheet (short)

| Form | Meaning |
|---|---|
| **8-K** | US issuer current event (best live financing/distress alert) |
| **6-K** | Foreign issuer current report (Canadian miners often use this) |
| **10-Q** | US quarterly (liquidity, covenants, going concern) |
| **10-K** | US annual |
| **20-F / 40-F** | Foreign annual packages |

## Notable mining-leaning hits (curated)

| Stage | Mode | Company | Why it surfaced |
|---|---|---|---|
| dfs | capital_raise | **Hycroft Mining** | feasibility / flow-through language |
| dfs | capital_raise | **Ramaco Resources** | credit facility + feasibility / PEA language |
| dfs | capital_raise | **Contango ORE** | feasibility / mineral resource language |
| pea | capital_raise | **U.S. GoldMining** | preliminary economic assessment |
| construction | capital_raise | **Coeur Mining** | streaming agreement |
| exploration | capital_raise | **Coeur Mining** | flow-through mention |
| unknown | capital_raise | **Hecla Mining** | royalty language |
| unknown | capital_raise | **Contango Silver & Gold** | royalty language |
| distress_dip | distress_sale | **ReAlloys** / **Z Squared** | going concern + mining terms (verify manually) |

## Important limits

1. **Many junior miners are on SEDAR+ (Canada), not EDGAR.** EDGAR alone under-samples TSXV pre-FID names.
2. Boolean `mining AND "private placement"` still admits false positives (filings that mention both words). Always open the filing.
3. `distress_sale` mode is for PE/buyers as well as rescue capital — not only equity raises.
4. Orla-style M&A closes appear under broad `mining` search but not under financing-keyword mode (by design).
