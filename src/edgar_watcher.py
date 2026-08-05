"""Scan SEC EDGAR full-text search for likely funding-need signals."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from .config import (
    DATA_DIR,
    EDGAR_LOOKBACK_DAYS,
    EDGAR_MAX_HITS_PER_QUERY,
    ENERGY_MINING_SICS,
    SEC_USER_AGENT,
)
from .signal_rules import MINING_STAGE_QUERIES, RULES, score_text

EFTS_URL = "https://efts.sec.gov/LATEST/search-index"
FORMS = "8-K,8-K/A,10-Q,10-K,6-K,20-F,40-F,S-1,S-3,424B5"


def _headers() -> dict[str, str]:
    return {
        "User-Agent": SEC_USER_AGENT,
        "Accept": "application/json",
    }


def _parse_display_name(display: str) -> tuple[str, str | None]:
    """'ACME CORP  (ACME)  (CIK 0001234567)' -> name, ticker."""
    ticker = None
    m = re.search(r"\(([A-Z][A-Z0-9.\-]{0,10})\)", display)
    if m and not m.group(1).startswith("CIK"):
        ticker = m.group(1)
    name = re.sub(r"\s*\(CIK\s+\d+\)\s*$", "", display)
    name = re.sub(r"\s*\([A-Z][A-Z0-9.\-]{0,10}(?:,\s*[A-Z0-9.\-]+)*\)\s*", " ", name)
    return re.sub(r"\s+", " ", name).strip(), ticker


def _query_string(keyword: str) -> str:
    """Quote simple phrases; pass through boolean queries unchanged."""
    if any(op in keyword for op in (" AND ", " OR ", '"')):
        return keyword
    return f'"{keyword}"'


def search_edgar(keyword: str, start: date, end: date, max_hits: int) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    page_size = min(max_hits, 100)
    frm = 0
    session = requests.Session()
    session.headers.update(_headers())

    while len(hits) < max_hits:
        url = (
            f"{EFTS_URL}?q={quote(_query_string(keyword))}"
            f"&dateRange=custom&startdt={start.isoformat()}&enddt={end.isoformat()}"
            f"&forms={FORMS}&from={frm}"
        )
        try:
            resp = session.get(url, timeout=45)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as exc:
            print(f"  EDGAR query failed for {keyword!r} (from={frm}): {exc}")
            break
        batch = payload.get("hits", {}).get("hits", [])
        if not batch:
            break
        for h in batch:
            src = h.get("_source", {})
            hits.append(
                {
                    "keyword_query": keyword,
                    "adsh": src.get("adsh"),
                    "ciks": src.get("ciks") or [],
                    "display_names": src.get("display_names") or [],
                    "form": src.get("form") or src.get("file_type"),
                    "file_date": src.get("file_date"),
                    "sics": [str(s) for s in (src.get("sics") or [])],
                    "items": src.get("items") or [],
                    "file_description": src.get("file_description") or "",
                    "biz_locations": src.get("biz_locations") or [],
                    "doc_id": h.get("_id"),
                    "search_score": h.get("_score"),
                }
            )
            if len(hits) >= max_hits:
                break
        frm += len(batch)
        time.sleep(0.25)
        if len(batch) < page_size:
            break
    return hits


def filing_url(cik: str, adsh: str, doc_id: str | None) -> str:
    cik_num = str(int(cik))
    adsh_nodash = adsh.replace("-", "")
    if doc_id and ":" in doc_id:
        filename = doc_id.split(":", 1)[1]
        return f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{adsh_nodash}/{filename}"
    return f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{adsh_nodash}/{adsh}-index.htm"


def fetch_snippet(url: str, session: requests.Session, max_chars: int = 1200) -> str:
    try:
        r = session.get(url, timeout=30)
        if r.status_code != 200:
            return ""
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except requests.RequestException:
        return ""


def normalize_hit(raw: dict[str, Any], fetch_text: bool, session: requests.Session) -> dict[str, Any] | None:
    if not raw.get("adsh") or not raw.get("ciks"):
        return None
    cik = raw["ciks"][0]
    display = (raw.get("display_names") or [""])[0]
    company_name, ticker = _parse_display_name(display)
    url = filing_url(cik, raw["adsh"], raw.get("doc_id"))

    base_text = " ".join(
        [
            company_name,
            raw.get("file_description") or "",
            raw.get("keyword_query") or "",
            " ".join(raw.get("items") or []),
        ]
    )
    snippet = ""
    if fetch_text:
        snippet = fetch_snippet(url, session)
        time.sleep(0.15)

    scored = score_text(f"{base_text} {snippet}")
    if raw["keyword_query"] not in scored["keywords_hit"]:
        scored["keywords_hit"].append(raw["keyword_query"])
        scored["score"] = min(1.0, round(scored["score"] + 0.08, 3))

    if any(s in ENERGY_MINING_SICS for s in raw.get("sics") or []):
        scored["score"] = min(1.0, round(scored["score"] + 0.15, 3))
        if scored["sector_guess"] == "other_energy":
            sic = (raw.get("sics") or [""])[0]
            if sic.startswith("13") or sic in {"2911", "5171", "5172"}:
                scored["sector_guess"] = "oil_gas_upstream"
            elif sic.startswith("10") or sic.startswith("14") or sic.startswith("33"):
                scored["sector_guess"] = "mining"
            elif sic.startswith("49"):
                scored["sector_guess"] = "power_renewables"

    return {
        "source": "edgar",
        "external_id": raw["adsh"],
        "company_name": company_name,
        "cik": cik,
        "ticker": ticker,
        "form_type": raw.get("form"),
        "filed_at": raw.get("file_date"),
        "title": f"{company_name} {raw.get('form')} ({raw.get('file_date')})",
        "snippet": snippet,
        "filing_url": url,
        "keywords_hit": scored["keywords_hit"],
        "sector_guess": scored["sector_guess"],
        "stage_guess": scored["stage_guess"],
        "ask_type_guess": scored["ask_type_guess"],
        "mode_guess": scored.get("mode_guess") or "capital_raise",
        "needs_bd_license": scored["needs_bd_license"],
        "score": scored["score"],
        "sics": raw.get("sics") or [],
        "items": raw.get("items") or [],
        "notes": scored["notes"],
        "raw": {
            "keyword_query": raw.get("keyword_query"),
            "search_score": raw.get("search_score"),
            "biz_locations": raw.get("biz_locations"),
        },
    }


def run_watch(
    lookback_days: int = EDGAR_LOOKBACK_DAYS,
    max_hits_per_query: int = EDGAR_MAX_HITS_PER_QUERY,
    fetch_text: bool = False,
    energy_only: bool = False,
    mining_stages: bool = False,
) -> list[dict[str, Any]]:
    end = date.today()
    start = end - timedelta(days=lookback_days)
    if mining_stages:
        queries = list(MINING_STAGE_QUERIES)
    else:
        priority = [
            "reserve-based",
            "borrowing base",
            "seeking additional capital",
            "debtor-in-possession",
            "project financing",
            "acquisition financing",
            "strategic alternatives",
            "going concern",
            "bankable feasibility",
            "credit facility",
            "private placement",
            "feasibility study",
            "preliminary economic assessment",
        ]
        queries = [k for k in priority if k in {r.keyword for r in RULES}]

    print(f"Scanning EDGAR {start} → {end} for {len(queries)} keywords…")
    raw_hits: list[dict[str, Any]] = []
    for kw in queries:
        batch = search_edgar(kw, start, end, max_hits_per_query)
        print(f"  {kw!r}: {len(batch)} hits")
        raw_hits.extend(batch)

    session = requests.Session()
    session.headers.update(_headers())

    by_adsh: dict[str, dict[str, Any]] = {}
    for raw in raw_hits:
        norm = normalize_hit(raw, fetch_text=fetch_text, session=session)
        if not norm:
            continue
        if mining_stages:
            strong_mining = {
                "preliminary economic assessment",
                "pre-feasibility",
                "prefeasibility",
                "feasibility study",
                "bankable feasibility",
                "royalty financing",
                "streaming agreement",
                "metal stream",
                "nsr royalty",
                "drill program",
                "exploration program",
                "path to production",
                "final investment decision",
                "earn-in",
                "farm-in",
            }
            name_blob = (norm.get("company_name") or "").lower()
            name_mining = any(
                t in name_blob
                for t in ("mining", "miner", "gold", "copper", "lithium", "silver", "ore", "resources", "metals")
            )
            if not (
                norm["sector_guess"] == "mining"
                or strong_mining.intersection(norm["keywords_hit"])
                or name_mining
                or any(s in ENERGY_MINING_SICS for s in norm.get("sics") or [])
            ):
                continue
        elif energy_only and not (
            any(s in ENERGY_MINING_SICS for s in norm.get("sics") or [])
            or norm["sector_guess"]
            in {"oil_gas_upstream", "oil_gas_midstream", "mining", "power_renewables"}
        ):
            if not any(
                k in norm["keywords_hit"]
                for k in (
                    "reserve-based",
                    "borrowing base",
                    "bankable feasibility",
                    "preliminary economic assessment",
                    "project financing",
                )
            ):
                continue
        prev = by_adsh.get(norm["external_id"])
        if not prev or norm["score"] > prev["score"]:
            if prev:
                merged = sorted(set(prev["keywords_hit"]) | set(norm["keywords_hit"]))
                norm["keywords_hit"] = merged
                norm["score"] = min(
                    1.0,
                    round(max(prev["score"], norm["score"]) + 0.05 * max(0, len(merged) - 1), 3),
                )
            by_adsh[norm["external_id"]] = norm

    return sorted(by_adsh.values(), key=lambda s: (-s["score"], s.get("filed_at") or ""))


def export_signals(signals: list[dict[str, Any]], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"signals_{stamp}.json"
    latest = out_dir / "signals.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(signals),
        "signals": signals,
    }
    path.write_text(json.dumps(payload, indent=2))
    latest.write_text(json.dumps(payload, indent=2))

    csv_path = out_dir / "exports" / "signals.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "external_id",
        "company_name",
        "ticker",
        "cik",
        "form_type",
        "filed_at",
        "score",
        "sector_guess",
        "stage_guess",
        "ask_type_guess",
        "mode_guess",
        "needs_bd_license",
        "keywords_hit",
        "filing_url",
        "title",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for s in signals:
            row = {k: s.get(k) for k in fields}
            row["keywords_hit"] = "; ".join(s.get("keywords_hit") or [])
            w.writerow(row)
    print(f"Wrote {path}")
    print(f"Wrote {latest}")
    print(f"Wrote {csv_path}")
    return latest


def main() -> None:
    parser = argparse.ArgumentParser(description="EDGAR funding-need signal watcher")
    parser.add_argument("--lookback-days", type=int, default=EDGAR_LOOKBACK_DAYS)
    parser.add_argument("--max-hits", type=int, default=EDGAR_MAX_HITS_PER_QUERY)
    parser.add_argument("--fetch-text", action="store_true", help="Fetch filing HTML for better scoring")
    parser.add_argument("--energy-only", action="store_true", help="Keep energy/mining-leaning hits")
    parser.add_argument(
        "--mining-stages",
        action="store_true",
        help="Junior mining / pre-FID keyword set; keep mining-leaning hits",
    )
    parser.add_argument("--min-score", type=float, default=0.2)
    args = parser.parse_args()

    signals = run_watch(
        lookback_days=args.lookback_days,
        max_hits_per_query=args.max_hits,
        fetch_text=args.fetch_text,
        energy_only=args.energy_only,
        mining_stages=args.mining_stages,
    )
    signals = [s for s in signals if s["score"] >= args.min_score]
    export_signals(signals, DATA_DIR)
    print(f"\nTop signals by stage:")
    by_stage: dict[str, list] = {}
    for s in signals:
        by_stage.setdefault(s.get("stage_guess") or "unknown", []).append(s)
    for stage, rows in sorted(by_stage.items(), key=lambda kv: -len(kv[1])):
        print(f"\n[{stage}] {len(rows)} hits")
        for s in rows[:5]:
            print(
                f"  {s['score']:.2f} | {s.get('mode_guess','?'):14} | {s['ask_type_guess']:18} | "
                f"{s['company_name'][:36]:36} | {s['form_type']} | {', '.join(s['keywords_hit'][:3])}"
            )


if __name__ == "__main__":
    main()