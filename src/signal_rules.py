"""Keyword rules that turn filing text into funding-need hypotheses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalRule:
    keyword: str
    weight: float
    ask_type_guess: str
    stage_guess: str
    needs_bd_license: bool = False
    note: str = ""


RULES: list[SignalRule] = [
    SignalRule("reserve-based", 0.35, "rbl", "producing", note="RBL language"),
    SignalRule("borrowing base", 0.30, "rbl", "producing", note="RBL redetermination"),
    SignalRule("credit facility", 0.22, "senior_debt", "producing", note="Credit facility mention"),
    SignalRule("credit agreement", 0.20, "senior_debt", "unknown", note="Credit agreement"),
    SignalRule("amended and restated credit", 0.25, "senior_debt", "producing"),
    SignalRule("liquidity", 0.12, "unknown", "unknown"),
    SignalRule("going concern", 0.28, "equity", "distress_dip", needs_bd_license=True),
    SignalRule("strategic alternatives", 0.30, "equity", "distress_dip", needs_bd_license=True),
    SignalRule("private placement", 0.24, "equity", "unknown", needs_bd_license=True),
    SignalRule("registered direct offering", 0.22, "equity", "unknown", needs_bd_license=True),
    SignalRule("at-the-market", 0.15, "equity", "unknown", needs_bd_license=True),
    SignalRule("project financing", 0.30, "project_debt", "construction"),
    SignalRule("construction financing", 0.28, "project_debt", "construction"),
    SignalRule("acquisition financing", 0.28, "acquisition_finance", "acquisition_ad"),
    SignalRule("purchase and sale agreement", 0.18, "acquisition_finance", "acquisition_ad"),
    SignalRule("debtor-in-possession", 0.40, "senior_debt", "distress_dip"),
    SignalRule("dip financing", 0.40, "senior_debt", "distress_dip"),
    SignalRule("preliminary economic assessment", 0.20, "equity", "pea", needs_bd_license=True),
    SignalRule("pre-feasibility", 0.22, "equity", "pfs", needs_bd_license=True),
    SignalRule("feasibility study", 0.24, "project_debt", "dfs"),
    SignalRule("bankable feasibility", 0.30, "project_debt", "dfs"),
    SignalRule("offtake agreement", 0.18, "project_debt", "dfs"),
    SignalRule("royalty", 0.12, "royalty_streaming", "unknown"),
    SignalRule("streaming agreement", 0.22, "royalty_streaming", "construction"),
    SignalRule("maturity date", 0.10, "senior_debt", "unknown"),
    SignalRule("unable to refinance", 0.32, "senior_debt", "distress_dip"),
    SignalRule("seeking additional capital", 0.34, "equity", "unknown", needs_bd_license=True),
    SignalRule("working capital facility", 0.20, "senior_debt", "producing"),
]

SECTOR_HINTS = {
    "oil_gas_upstream": [
        "oil and gas",
        "crude oil",
        "natural gas",
        "exploration and production",
        "e&p",
        "permian",
        "bakken",
        "eagle ford",
        "proved reserves",
        "drilling",
    ],
    "oil_gas_midstream": [
        "pipeline",
        "midstream",
        "gathering and processing",
        "terminal",
        "lng",
    ],
    "mining": [
        "mining",
        "mineral",
        "gold",
        "copper",
        "lithium",
        "nickel",
        "silver",
        "ore",
        "mill",
        "feasibility study",
        "preliminary economic assessment",
    ],
    "power_renewables": [
        "solar",
        "wind",
        "battery storage",
        "renewable",
        "power purchase agreement",
        "ppa",
    ],
}


def guess_sector(text: str) -> str:
    t = text.lower()
    scores: dict[str, int] = {}
    for sector, hints in SECTOR_HINTS.items():
        scores[sector] = sum(1 for h in hints if h in t)
    if not scores or max(scores.values()) == 0:
        return "other_energy"
    return max(scores, key=scores.get)


def score_text(text: str) -> dict:
    """Return score, keywords, guesses from filing title+snippet."""
    t = text.lower()
    hits: list[str] = []
    ask_votes: dict[str, float] = {}
    stage_votes: dict[str, float] = {}
    needs_license = False
    score = 0.0
    notes: list[str] = []

    for rule in RULES:
        if rule.keyword in t:
            hits.append(rule.keyword)
            score += rule.weight
            ask_votes[rule.ask_type_guess] = ask_votes.get(rule.ask_type_guess, 0) + rule.weight
            stage_votes[rule.stage_guess] = stage_votes.get(rule.stage_guess, 0) + rule.weight
            needs_license = needs_license or rule.needs_bd_license
            if rule.note:
                notes.append(rule.note)

    ask_type = max(ask_votes, key=ask_votes.get) if ask_votes else "unknown"
    stage = max(stage_votes, key=stage_votes.get) if stage_votes else "unknown"
    sector = guess_sector(t)

    score = min(score, 1.0)
    return {
        "score": round(score, 3),
        "keywords_hit": hits,
        "ask_type_guess": ask_type,
        "stage_guess": stage,
        "sector_guess": sector,
        "needs_bd_license": needs_license,
        "notes": notes,
    }