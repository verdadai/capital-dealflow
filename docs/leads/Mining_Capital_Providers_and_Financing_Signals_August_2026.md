# Mining capital providers & financing signals — August 2026

Compiled from **public** sources (company sites, press releases, EDGAR).  
Confidence = how clearly the site/release shows they deploy capital into mining projects.

> Not investment advice. Verify criteria before outreach. `broker_friendly` unknown unless noted.

---

## A) Strong-confidence capital providers (public criteria / active deployers)

| Firm | Type | Stage fit (public positioning) | Website | Notes |
|---|---|---|---|---|
| **Denham Capital — Mining** | PE / flexible stack | Near-production (≤~2 yrs), construction, ramp, producing | https://www.denhamcapital.com/mining/ | Equity → sub/senior debt; critical metals focus |
| **Orion Resource Partners** | Mine finance / royalties | Construction & acquisition of strategic metals | https://www.orionresourcepartners.com/ | Large mine-finance funds; institutional |
| **Appian Capital Advisory** | Mining PE / operating investor | Metals & mining assets / companies | https://appiancapitaladvisory.com/ | Technical + capital; earlier than some banks |
| **Franco-Nevada** | Royalty / streaming | Producing + development (selective) | https://www.franco-nevada.com/ | Non-operating capital partner |
| **Wheaton Precious Metals** | Streaming | Producing + development streams | https://wheatonpm.com/ | Precious metals streaming |
| **OR Royalties** (ex-Osisko) | Royalty / streaming | Operating → earlier stage selective | https://orroyalties.com/ | Recent project financings with juniors |
| **Triple Flag** | Royalty / streaming | Prefer producing / construction-ready; some earlier | https://www.tripleflagpm.com/ | Americas / Australia focus publicly |
| **Sandstorm Gold** | Royalty / streaming | Diversified royalty book; capital to operators | https://www.sandstormgold.com/ | Gold-focused royalties/streams |
| **Breakwall / Valor Mining Credit** | Mining credit | Refi, acquisition, development credit | https://www.breakwallcap.com/ | Private credit; Vitol-backed mining credit vehicles |
| **LunR Royalties** | Royalty / streaming | Producing mine streams (example deal) | https://www.lunrroyalties.com/ | Active stream buyer (see press) |

### O&G producing lenders (only if dad confirms post-production)

| Firm | Type | Stage | Website |
|---|---|---|---|
| Production Lending | Private lender | **Existing production** | https://www.productionlending.com/investment-criteria/ |
| Riverbend Energy Group | Energy investor | See site | https://www.riverbendenergygroup.com/ |
| First Citizens Energy Finance | Bank | Producing / project debt large | https://www.firstcitizens.com/commercial/expertise/energy |

---

## B) Recent public mining financing signals (press) — reverse-engineer providers

| Date (approx) | Issuer / project | Signal | Capital parties named | Link / source type |
|---|---|---|---|---|
| Jul 2026 | **Canadian Copper** / Bathurst–Murray Brook | Stream + equity project financing (~C$44M package piece; larger stack w/ debt) | **OR Royalties**; also Ocean Partners project debt (announced) | Junior Mining Network / Newsfile |
| Jul 2026 | **Tintina Mines** | C$91M subscription receipts toward FID | Gignac family, **Sumitomo**, **Franco-Nevada**, G Mining Capital; Canaccord finder on portion | Company PR |
| Feb 2026 | **LunR Royalties** / Fruta del Norte | US$670M life-of-mine silver stream (share consideration) | LunR ← Lundin Gold | LunR PR PDF |
| Jan 2026 | **Silver Valley Metals** | C$2M private placement (exploration/development) | Equity PP | Newsfile |
| Mar 2026 | **Breakwall + Vitol** | Valor Mining Credit Partners II close | Breakwall / Vitol mining credit | Business Wire |
| Mar 2026 | **Orion** | Mine Finance Fund IV ~$2.2B close | Orion dry powder | PR Newswire |

**How to use:** each named capital party becomes a Provider row; each issuer becomes an Opportunity / case study for similar stage deals.

---

## C) EDGAR mining/energy hits (last ~30 days, automated)

Pulled via `python -m src.edgar_watcher` on 2026-08-02. Filtered to mining/energy-leaning:

| Score | Company | Sector guess | Keywords | Ask guess |
|---|---|---|---|---|
| 0.44 | **Ramaco Resources, Inc.** | mining | credit facility, feasibility study | project_debt |
| 0.43 | **Royale Energy, Inc.** | oil_gas_upstream | going concern | equity |
| 0.29 | Solstice Advanced Materials Inc. | power_renewables | credit facility, private placement | equity |

CSV export (local run): `data/exports/mining_energy_signals.csv`  
Raw: `data/mining_energy_signals.json`

**Caveat:** Quiet mid-summer window + EDGAR keyword noise. Ramaco is the cleanest mining hit in this batch.

---

## D) SEDAR+ (Canada) — what to do manually this week

SEDAR+ has no stable free API comparable to EDGAR. Weekly manual search:

1. https://www.sedarplus.ca → search issuers / documents  
2. Keywords: `private placement`, `feasibility study`, `preliminary economic assessment`, `stream`, `royalty`, `credit facility`  
3. Log: issuer, document date, raise size if stated, finders named, use of proceeds  
4. Add to Opportunities with `source=sedar`

Juniors on TSXV are often **pre-FID equity / royalty** stories — high relevance if dad’s book is early-stage mining.

---

## E) Suggested outreach buckets

1. **Pre-FID / development mining** → Orion, Appian, Denham (near-prod), royalty/streaming shops, offtakers  
2. **Construction / near-prod** → Denham, Orion mine finance, OR Royalties-style packages, private credit (Breakwall)  
3. **Producing O&G** (only if confirmed) → Production Lending, regional RBLs, First Citizens  

---

## F) Next automation steps (still free)

- [ ] Weekly cron for EDGAR watcher → append CSV  
- [ ] Script to fetch a watchlist of provider “investment criteria” pages for changes  
- [ ] Manual SEDAR+ log template in Airtable  
- [ ] Expand provider seed JSON from section A  
