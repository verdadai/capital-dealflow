# Free-first data & tech stack

Run this before paying for PitchBook / Preqin / Mergr.

## What we can pull for free (and automation status)

| Source | Public? | Automation today | Notes |
|---|---|---|---|
| **EDGAR (US SEC)** | Yes | **Yes** — `python -m src.edgar_watcher` | Best free machine-readable filing search |
| **SEDAR+ (Canada)** | Yes (web UI) | **Manual / light scrape later** | No stable public API like EDGAR; search juniors for PPMs, PEA/PFS/DFS |
| **Lender / PE / royalty websites** | Yes | Semi — fetch criteria pages by hand/script | Best for provider DB rows |
| **Press releases (Business Wire, Newsfile, company IR)** | Yes | Search + weekly review | Financing closings = reverse-engineer capital stack |
| **Junior Mining Network / mining newswires** | Yes | Manual watchlist | High noise; good for PPM announcements |
| **Referrals** | Private | CRM only | Still highest-quality dealflow |
| **Conferences / associations** | Paid travel | Manual | See [`CONFERENCES_AND_LEAD_VENUES.md`](CONFERENCES_AND_LEAD_VENUES.md) |
| PitchBook / Preqin / Mergr | Paid | Later | Only after free list is too slow |

## Weekly free workflow

1. Run EDGAR watcher (30-day lookback, energy/mining keywords).
2. SEDAR+ search (manual): `private placement`, `feasibility`, `stream`, `royalty`, commodity names.
3. Skim mining financing headlines → log issuer + capital providers into Opportunities / Providers.
4. Add/update provider rows from public investment-criteria pages.
5. Run matcher; outreach top desks.
6. Ask dad: producing vs pre-FID → route RBL banks vs royalty/PE/pre-FID capital.

## Honest limits

- EDGAR full-text sometimes returns HTTP 500 on busy queries; watcher continues other keywords.
- SEDAR+ is not as script-friendly as EDGAR; start manual, automate later if needed.
- Most **private** juniors and **true pre-public** deals will not show in EDGAR/SEDAR+ — referrals still matter.
- `broker_friendly` stays unknown until desks confirm.
