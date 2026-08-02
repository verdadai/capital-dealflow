"""Rule-based matcher: opportunities x capital providers."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR, ROOT

ASK_TO_CAPITAL = {
    "rbl": ["bank_rbl", "private_credit"],
    "project_debt": ["bank_project_finance", "private_credit", "bank_abl"],
    "senior_debt": ["bank_rbl", "bank_project_finance", "bank_abl", "private_credit"],
    "private_credit": ["private_credit"],
    "acquisition_finance": ["bank_rbl", "private_credit", "pe_equity"],
    "equity": ["pe_equity", "family_office"],
    "royalty_streaming": ["royalty_streaming"],
    "mezz": ["private_credit", "special_situations"],
    "unknown": ["private_credit", "pe_equity", "bank_rbl"],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def score_match(opp: dict, provider: dict) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    ask = opp.get("ask_type") or "unknown"
    capital_ok = ASK_TO_CAPITAL.get(ask, ASK_TO_CAPITAL["unknown"])
    if provider.get("capital_type") in capital_ok:
        score += 0.35
        reasons.append(f"capital type {provider['capital_type']} fits ask {ask}")
    else:
        return 0.0, [f"capital type {provider.get('capital_type')} does not fit ask {ask}"]

    sectors = set(provider.get("sectors") or [])
    if opp.get("sector") in sectors:
        score += 0.25
        reasons.append(f"sector fit: {opp.get('sector')}")
    else:
        score -= 0.15
        reasons.append(f"sector mismatch: opp={opp.get('sector')}")

    stages = set(provider.get("stages") or [])
    if opp.get("stage") in stages:
        score += 0.20
        reasons.append(f"stage fit: {opp.get('stage')}")
    elif opp.get("stage") in {None, "unknown"}:
        score += 0.05
        reasons.append("stage unknown; weak stage credit")
    else:
        score -= 0.10
        reasons.append(f"stage mismatch: opp={opp.get('stage')}")

    amin = opp.get("ask_amount_min_usd")
    amax = opp.get("ask_amount_max_usd")
    pmin = provider.get("check_size_min_usd") or 0
    pmax = provider.get("check_size_max_usd") or 10**15
    if amin is not None or amax is not None:
        lo = amin if amin is not None else amax
        hi = amax if amax is not None else amin
        if hi >= pmin and lo <= pmax:
            score += 0.15
            reasons.append("check size overlaps provider range")
        else:
            score -= 0.25
            reasons.append("check size outside provider range")
    else:
        score += 0.05
        reasons.append("ask size unknown; skipped hard size filter")

    if provider.get("broker_friendly") == "yes":
        score += 0.08
        reasons.append("broker-friendly")
    elif provider.get("broker_friendly") == "no":
        score -= 0.05
        reasons.append("historically not broker-friendly")

    if opp.get("needs_bd_license") and provider.get("capital_type") in {
        "bank_rbl",
        "bank_project_finance",
        "bank_abl",
    }:
        score -= 0.12
        reasons.append("securities/equity signal — bank debt desk may be wrong primary target")

    return round(max(score, 0.0), 3), reasons


def run_match(opportunities: list[dict], providers: list[dict], top_n: int = 8) -> list[dict]:
    matches: list[dict] = []
    for opp in opportunities:
        scored = []
        for p in providers:
            if p.get("active") is False:
                continue
            s, reasons = score_match(opp, p)
            if s <= 0:
                continue
            scored.append((s, reasons, p))
        scored.sort(key=lambda x: -x[0])
        for s, reasons, p in scored[:top_n]:
            matches.append(
                {
                    "opportunity_company": opp.get("company_name"),
                    "opportunity_ask_type": opp.get("ask_type"),
                    "opportunity_sector": opp.get("sector"),
                    "opportunity_stage": opp.get("stage"),
                    "opportunity_source_url": opp.get("source_url"),
                    "provider_firm": p.get("firm_name"),
                    "provider_desk": p.get("desk_name"),
                    "provider_capital_type": p.get("capital_type"),
                    "score": s,
                    "reasons": reasons,
                    "status": "suggested",
                    "needs_bd_license": opp.get("needs_bd_license"),
                }
            )
    matches.sort(key=lambda m: (-m["score"], m.get("opportunity_company") or ""))
    return matches


def export_matches(matches: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(matches),
        "matches": matches,
    }
    (out_dir / "matches.json").write_text(json.dumps(payload, indent=2))
    csv_path = out_dir / "exports" / "matches.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "score",
        "opportunity_company",
        "opportunity_ask_type",
        "opportunity_sector",
        "opportunity_stage",
        "provider_firm",
        "provider_desk",
        "provider_capital_type",
        "needs_bd_license",
        "status",
        "reasons",
        "opportunity_source_url",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for m in matches:
            row = {k: m.get(k) for k in fields}
            row["reasons"] = " | ".join(m.get("reasons") or [])
            w.writerow(row)
    print(f"Wrote {out_dir / 'matches.json'}")
    print(f"Wrote {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--opportunities", type=Path, default=DATA_DIR / "opportunities.json")
    parser.add_argument("--providers", type=Path, default=ROOT / "data" / "seed_providers.json")
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    if not args.opportunities.exists():
        raise SystemExit("Missing opportunities.json — run promote_signals first.")
    opps = load_json(args.opportunities).get("opportunities", [])
    providers = load_json(args.providers).get("providers", [])
    matches = run_match(opps, providers, top_n=args.top_n)
    export_matches(matches, DATA_DIR)
    print(f"Created {len(matches)} match rows for {len(opps)} opportunities x {len(providers)} providers")
    print("\nTop matches:")
    for m in matches[:12]:
        print(
            f"  {m['score']:.2f} | {m['opportunity_company'][:28]:28} | "
            f"{m['provider_firm']} ({m['provider_desk']}) | {m['opportunity_ask_type']}"
        )


if __name__ == "__main__":
    main()