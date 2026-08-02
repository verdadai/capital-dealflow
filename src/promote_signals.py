"""Promote high-scoring EDGAR signals into opportunity records."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR


def load_signals(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    return payload.get("signals", payload if isinstance(payload, list) else [])


def to_opportunity(signal: dict) -> dict:
    return {
        "project_name": signal.get("title") or signal.get("company_name"),
        "company_name": signal.get("company_name"),
        "ticker": signal.get("ticker"),
        "cik": signal.get("cik"),
        "sector": signal.get("sector_guess") or "other_energy",
        "stage": signal.get("stage_guess") or "unknown",
        "ask_type": signal.get("ask_type_guess") or "unknown",
        "ask_amount_min_usd": None,
        "ask_amount_max_usd": None,
        "status": "new",
        "warmth": "cold",
        "package_readiness": "signal_only",
        "confidence": signal.get("score") or 0,
        "summary": (
            f"EDGAR signal from {signal.get('form_type')} filed {signal.get('filed_at')}. "
            f"Keywords: {', '.join(signal.get('keywords_hit') or [])}. "
            f"{(signal.get('snippet') or '')[:280]}"
        ).strip(),
        "source": "edgar",
        "source_url": signal.get("filing_url"),
        "source_filing_accession": signal.get("external_id"),
        "signal_keywords": signal.get("keywords_hit") or [],
        "needs_bd_license": bool(signal.get("needs_bd_license")),
        "next_action": "Review filing; if energy/mining fit, request teaser or find CFO contact",
    }


def export_opportunities(opps: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(opps),
        "opportunities": opps,
    }
    (out_dir / f"opportunities_{stamp}.json").write_text(json.dumps(payload, indent=2))
    (out_dir / "opportunities.json").write_text(json.dumps(payload, indent=2))

    csv_path = out_dir / "exports" / "opportunities.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "company_name",
        "ticker",
        "cik",
        "sector",
        "stage",
        "ask_type",
        "confidence",
        "needs_bd_license",
        "status",
        "source_url",
        "source_filing_accession",
        "signal_keywords",
        "summary",
        "next_action",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for o in opps:
            row = {k: o.get(k) for k in fields}
            row["signal_keywords"] = "; ".join(o.get("signal_keywords") or [])
            w.writerow(row)
    print(f"Wrote {out_dir / 'opportunities.json'}")
    print(f"Wrote {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signals", type=Path, default=DATA_DIR / "signals.json")
    parser.add_argument("--min-score", type=float, default=0.35)
    parser.add_argument(
        "--sectors",
        default="oil_gas_upstream,oil_gas_midstream,mining,power_renewables",
        help="Comma-separated sector_guess values to keep",
    )
    args = parser.parse_args()

    if not args.signals.exists():
        raise SystemExit(f"Missing signals file: {args.signals}. Run edgar_watcher first.")

    allowed = {s.strip() for s in args.sectors.split(",") if s.strip()}
    signals = load_signals(args.signals)
    opps = []
    for s in signals:
        if (s.get("score") or 0) < args.min_score:
            continue
        if allowed and s.get("sector_guess") not in allowed:
            strong = {
                "reserve-based",
                "bankable feasibility",
                "preliminary economic assessment",
                "pre-feasibility",
                "project financing",
                "streaming agreement",
            }
            if not strong.intersection(s.get("keywords_hit") or []):
                continue
        opps.append(to_opportunity(s))

    export_opportunities(opps, DATA_DIR)
    print(f"Promoted {len(opps)} opportunities (min_score={args.min_score})")


if __name__ == "__main__":
    main()