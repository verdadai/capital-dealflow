# Investor verification

Before introducing a mining securities deal to a capital source, verify (1) they are allowed to receive the offering, and (2) they are a real, mandate-fit investor — not a tire-kicker or restricted person.

## 1) Match investor type to your licensing path

| Investor type | Typical definition (simplified) | CAB-friendly? | Traditional PP BD? |
|---|---|---|---|
| Institutional / QIB / qualified purchaser | Funds, banks, large orgs, certain wealthy entities | Usually yes | Yes |
| Issuer “eligible employees” (CAB context) | Certain officers/directors/knowledgeable employees under CAB rules | Possibly (confirm RN 26-04 / CAB 016) | Yes |
| Accredited investor (Reg D) | Income/net-worth or entity tests | Often **no** if purely retail accredited | Yes |
| Retail non-accredited | General public | No | Generally no for typical junior mining PPM |

If the business plan is “family offices + mining PE + institutional credit,” CAB or BD affiliation can work.  
If the plan is “angel dentists and Facebook mining groups,” you need a traditional private-placement BD and heavy suitability controls — or don’t do it.

## 2) Investor identity KYC (minimum)

- [ ] Legal name / entity type / jurisdiction
- [ ] Beneficial owners (for entities)
- [ ] Authorized signer
- [ ] Contact diligence (website, LinkedIn, references, prior deals)
- [ ] Sanctions / PEP / adverse media screen
- [ ] Source-of-funds narrative for individuals where appropriate

**Red flags:** won’t identify beneficial owners, only personal Gmail + no verifiable deal history, asks for upfront “processing fees” from issuer, wants exclusive without proof of funds.

## 3) Accreditation / institutional status

Collect **written representation** plus support where practical:

### Accredited investor (Reg D context)
- [ ] Individual income or net-worth representation
- [ ] Entity assets / owner accreditation representation
- [ ] Form of questionnaire + signature + date
- [ ] Re-verify if stale (e.g. older than policy limit)

### Institutional / CAB-eligible
- [ ] Category under CAB institutional definition (bank, insurance, QP, etc.)
- [ ] AUM / investment discretion evidence if relied upon
- [ ] If “eligible employee,” document which CAB rule category applies

Store questionnaires in the deal file. Do not rely on “they seem rich.”

## 4) Mandate fit (investment diligence)

- [ ] Check size min/max
- [ ] Sectors: mining commodities they actually do
- [ ] Stages: exploration vs PFS vs DFS vs producing
- [ ] Geographies / jurisdiction exclusions
- [ ] Instrument preference: equity, royalty/stream, convertible, project debt
- [ ] Recent comparable deals (last 24 months)
- [ ] Decision process + timing
- [ ] Will they work via intermediary? (`broker_friendly`: yes/no/unknown)

Only mark `broker_friendly=yes` after explicit confirmation.

## 5) Offering mechanics checks

- [ ] Offering exemption relied on (e.g. Reg D 506(b)/506(c), Reg S, etc.) — counsel driven
- [ ] General solicitation rules (506(c) verification is stricter)
- [ ] Bad actor disqualification checks on issuer/covered persons
- [ ] State blue-sky notice filings as required
- [ ] If BD channel: FINRA Rule 5123 filing responsibility assigned

## 6) Interaction rules for an intermediary

**Do**
- Send anonymous teaser first under NDA path
- Log every solicitation in Interactions CRM
- Route securities conversations through BD supervision if registered that way

**Don’t**
- Promise returns or “guaranteed offtake finance”
- Share non-public technical data without NDA
- Take personal success-fee wires outside the BD if the deal is a securities placement
- Solicit in states where you/your firm are not registered

## 7) Investor verification record (CRM fields)

Suggested fields to add in Airtable/Postgres later:

- `investor_category` — institutional | accredited | eligible_employee | other
- `accreditation_status` — unverified | questionnaire_on_file | counsel_cleared
- `kyc_status` — unverified | passed | failed
- `broker_friendly` — unknown | yes | no
- `last_verified_at`
- `verification_notes`
