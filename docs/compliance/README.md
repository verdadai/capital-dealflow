# Mining capital intermediary — verification & compliance pack

**Branch purpose:** verify how to underwrite mining companies and investors, and what broker-dealer (BD) / Capital Acquisition Broker (CAB) requirements apply before taking success fees on securities placements.

> **Not legal advice.** Use this as an operating checklist. Confirm with securities counsel before raising capital or collecting transaction-based compensation.

## Scope of this pack

| Doc | What it covers |
|---|---|
| [broker-dealer-requirements.md](./broker-dealer-requirements.md) | When BD registration is required; CAB vs traditional BD; exams; capital; mining-specific WSPs |
| [mining-company-verification.md](./mining-company-verification.md) | Issuer / project due diligence before taking a mandate |
| [investor-verification.md](./investor-verification.md) | Who you can solicit; accredited vs institutional; KYC/AML |
| [../../checklists/](../../checklists/) | Printable go/no-go checklists |

## Decision tree (start here)

```text
What capital is being raised?
│
├─ Commercial bank loan / RBL / project debt from a bank
│    (no securities sold to investors)
│    → Lower BD risk; still use engagement letter + counsel
│
└─ Equity, notes, convertibles, fund interests, royalty securities, etc.
     → Likely securities transaction
     → Transaction-based fee + solicitation ≈ broker activity
     → Need BD affiliation or own BD/CAB registration
```

## Recommended operating model (for this business)

Given the stated focus — **introducing/advisory placement for junior miners, private placements, not holding customer funds**:

1. **Short term:** affiliate as a registered rep / placement agent with an existing BD or CAB (fastest lawful path).
2. **Medium term (optional):** form own **CAB** or limited-purpose private-placement BD if volume justifies cost.
3. **Always separate:**
   - Bank-debt introductions (First Citizens–type) in one engagement template
   - Securities placements in a BD-supervised engagement template

## Verification status legend (use in CRM)

| Status | Meaning |
|---|---|
| `unverified` | Not reviewed |
| `desk_confirmed` | Counterparty verbally/written confirmed policy |
| `docs_on_file` | Supporting docs collected |
| `counsel_cleared` | Outside counsel signed off for this mandate type |
| `blocked` | Do not proceed |

`broker_friendly` in `data/seed_providers.json` should stay **`unknown`** until `desk_confirmed` or better.
