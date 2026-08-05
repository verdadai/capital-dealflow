# EDGAR form types + mining stage capital signals

## Form type differences

| Form | Who files | Cadence | What it’s for | Financing use |
|---|---|---|---|---|
| **8-K** | Most US domestic issuers | Anytime a material event happens | Current report (new facility, placement, default, M&A, etc.) | **Best real-time capital / distress signal** |
| **6-K** | Foreign private issuers (many Canadian miners listed in US) | Anytime | Furnishes home-country news; exhibits often hold the press release | Same role as 8-K for Orla-style names |
| **10-Q** | US domestic | Quarterly | Unaudited interim financials + MD&A | Liquidity, debt maturities, going concern, covenant issues |
| **10-K** | US domestic | Annual | Full audited annual report | Deeper distress / capital structure picture |
| **20-F** | Many foreign private issuers | Annual | Foreign annual report (SEC equivalent of 10-K style) | Annual capital / risk disclosure |
| **40-F** | Often Canadian MJDS issuers | Annual | Canadian annual package furnished to SEC | Same idea as 20-F for many TSX names |

**Rule of thumb**
- Hunting **live raises / events** → start with **8-K / 6-K**
- Hunting **slow-burn distress / maturity walls** → add **10-Q / 10-K / 20-F / 40-F**
- Searching only `mining` returns noise (ops updates, M&A closes). Search **financing language** instead.

## Mining stages → language → capital

| Stage guess | Typical filing language | Ask guess | Who to target |
|---|---|---|---|
| `exploration` | drill program, flow-through, non-brokered PP, earn-in | equity | Retail/institutional equity, strategics |
| `pea` | preliminary economic assessment | equity (+ early royalty talk) | Equity, some royalty scouts |
| `pfs` | pre-feasibility / prefeasibility | equity / royalty_streaming | Equity, royalty/stream, offtake talks |
| `dfs` | feasibility / bankable feasibility, path to production | project_debt / royalty / offtake | Streamers, mine finance, late equity |
| `construction` | FID, construction financing, project financing, financial close | project_debt | Project finance / mine finance / streams |
| `producing` | credit facility, RBL, borrowing base | rbl / senior_debt | Banks, private credit |
| `distress_dip` | going concern, strategic alternatives, forbearance, default | equity or special situations | PE buyers, rescue credit, consolidators |
| `acquisition_ad` | acquisition financing, business combination, PSA | acquisition_finance | PE / strategics / acquisition debt |

## Mode guess (separate from stage)

| Mode | Meaning |
|---|---|
| `capital_raise` | Likely needs money (PP, study, stream, project finance) |
| `distress_sale` | May want capital **or to be acquired** |
| `refi` | Existing/amending debt facilities |
| `acquisition` | Buy/sell or combo process |

## Commands

```bash
# Junior mining / pre-FID focused scan
python -m src.edgar_watcher --mining-stages --lookback-days 30 --max-hits 25 --min-score 0.20

# Broader energy + mining financing scan
python -m src.edgar_watcher --energy-only --lookback-days 14 --max-hits 25
```
