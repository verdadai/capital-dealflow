# Airtable schema (same model as Postgres)

Create one Airtable **base**: `Capital Dealflow`.

## Tables

### 1) Companies
| Field | Type | Notes |
|---|---|---|
| Name | Single line text | Primary field |
| Website | URL | |
| Ticker | Single line text | |
| CIK | Single line text | SEC CIK |
| Jurisdiction | Single line text | |
| HQ Location | Single line text | |
| Sector | Single select | oil_gas_upstream, oil_gas_midstream, mining, power_renewables, other_energy |
| Notes | Long text | |
| Opportunities | Link to Opportunities | |

### 2) Opportunities
| Field | Type | Notes |
|---|---|---|
| Title | Formula / text | Company + project name |
| Company | Link to Companies | |
| Project Name | Single line text | |
| Sector | Single select | same as Companies |
| Stage | Single select | exploration, pea, pfs, dfs, construction, producing, acquisition_ad, distress_dip, unknown |
| Ask Type | Single select | rbl, project_debt, senior_debt, private_credit, acquisition_finance, equity, royalty_streaming, mezz, unknown |
| Ask Min USD | Currency | |
| Ask Max USD | Currency | |
| Commodity | Single line text | |
| Geography | Single line text | |
| Status | Single select | new → closed/dead/pass |
| Warmth | Single select | cold, warm, mandated |
| Package Readiness | Single select | signal_only, teaser, partial_package, lender_ready |
| Confidence | Number (0–1) | |
| Summary | Long text | |
| Source | Single select | edgar, referral, conference, manual, ad_market |
| Source URL | URL | |
| Signal Keywords | Multiple select or text | |
| Needs BD License | Checkbox | equity/securities |
| Fee % | Percent | |
| Next Action | Single line text | |
| Next Action Due | Date | |
| Matches | Link to Matches | |

### 3) Providers
| Field | Type | Notes |
|---|---|---|
| Firm Name | Single line text | Primary |
| Desk Name | Single line text | e.g. Energy Finance / Oil & Gas |
| Capital Type | Single select | bank_rbl, bank_project_finance, bank_abl, private_credit, pe_equity, royalty_streaming, family_office, offtake_trader, special_situations, other |
| Check Min USD | Currency | |
| Check Max USD | Currency | |
| Sectors | Multiple select | |
| Stages | Multiple select | |
| Geographies | Multiple select / text | |
| Broker Friendly | Single select | yes, unknown, no |
| Website | URL | |
| Active | Checkbox | |
| Notes | Long text | |
| Contacts | Link to Contacts | |
| Matches | Link to Matches | |

### 4) Contacts
| Field | Type | |
|---|---|---|
| Full Name | Single line text | |
| Provider | Link to Providers | |
| Title | Single line text | |
| Email | Email | |
| LinkedIn | URL | |
| Phone | Phone | |
| Primary | Checkbox | |

### 5) Matches
| Field | Type | |
|---|---|---|
| Name | Formula | Opportunity + Provider |
| Opportunity | Link to Opportunities | |
| Provider | Link to Providers | |
| Score | Number | |
| Reasons | Long text | |
| Status | Single select | suggested, queued, contacted, interested, passed, term_sheet, won |

### 6) Signals (EDGAR inbox)
| Field | Type | |
|---|---|---|
| Title | Single line text | |
| Company Name | Single line text | |
| CIK | Single line text | |
| Ticker | Single line text | |
| Form Type | Single line text | |
| Filed At | Date | |
| Snippet | Long text | |
| Filing URL | URL | |
| Keywords Hit | Multiple select / text | |
| Score | Number | |
| Sector Guess | Single select | |
| Stage Guess | Single select | |
| Ask Type Guess | Single select | |
| Promoted Opportunity | Link to Opportunities | |
| Raw JSON | Long text | optional |

### 7) Interactions
| Field | Type | |
|---|---|---|
| Subject | Single line text | |
| Opportunity | Link to Opportunities | |
| Provider | Link to Providers | |
| Contact | Link to Contacts | |
| Channel | Single select | email, linkedin, call, meeting |
| Direction | Single select | outbound, inbound |
| Body | Long text | |
| Interacted At | Date/time | |

## Airtable views to create
- **Signals → Review**: Signals where Promoted Opportunity is empty, sorted by Score desc
- **Hot Opportunities**: Status in (new, researching, mandated)
- **RBL Targets**: Opportunities Ask Type = rbl
- **Provider Coverage Gaps**: Opportunities with fewer than 3 Matches
- **Needs License Care**: Needs BD License checked

## Import path from this repo
1. Run `python -m src.edgar_watcher` → writes `data/signals.json`
2. Run `python -m src.promote_signals` → writes `data/opportunities.json`
3. Run `python -m src.matcher` → writes `data/matches.json`
4. Import CSVs from `data/exports/` into Airtable
