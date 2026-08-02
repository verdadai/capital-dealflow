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
    # capital_raise | distress_sale | refi | acquisition
    mode_hint: str = "capital_raise"


RULES: list[SignalRule] = [
    # --- Producing / bank debt ---
    SignalRule("reserve-based", 0.35, "rbl", "producing", note="RBL language", mode_hint="refi"),
    SignalRule("borrowing base", 0.30, "rbl", "producing", note="RBL redetermination", mode_hint="refi"),
    SignalRule("credit facility", 0.22, "senior_debt", "producing", note="Credit facility mention", mode_hint="refi"),
    SignalRule("credit agreement", 0.20, "senior_debt", "unknown", note="Credit agreement", mode_hint="refi"),
    SignalRule("amended and restated credit", 0.25, "senior_debt", "producing", mode_hint="refi"),
    SignalRule("working capital facility", 0.20, "senior_debt", "producing", mode_hint="refi"),
    SignalRule("liquidity", 0.12, "unknown", "unknown", mode_hint="capital_raise"),
    # --- Distress / possible sale ---
    SignalRule("going concern", 0.28, "equity", "distress_dip", needs_bd_license=True, mode_hint="distress_sale"),
    SignalRule("strategic alternatives", 0.34, "equity", "distress_dip", needs_bd_license=True, mode_hint="distress_sale"),
    SignalRule("forbearance", 0.32, "senior_debt", "distress_dip", mode_hint="distress_sale"),
    SignalRule("event of default", 0.33, "senior_debt", "distress_dip", mode_hint="distress_sale"),
    SignalRule("restructuring", 0.22, "senior_debt", "distress_dip", mode_hint="distress_sale"),
    SignalRule("debtor-in-possession", 0.40, "senior_debt", "distress_dip", mode_hint="distress_sale"),
    SignalRule("dip financing", 0.40, "senior_debt", "distress_dip", mode_hint="distress_sale"),
    SignalRule("unable to refinance", 0.32, "senior_debt", "distress_dip", mode_hint="distress_sale"),
    # --- Equity / securities raises ---
    SignalRule("private placement", 0.24, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("non-brokered private placement", 0.28, "equity", "exploration", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("flow-through", 0.26, "equity", "exploration", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("registered direct offering", 0.22, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("at-the-market", 0.15, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("bought deal", 0.24, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("seeking additional capital", 0.34, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("funding alternatives", 0.26, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("financing options", 0.24, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("strategic investment", 0.24, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("cornerstone investor", 0.22, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("drill program", 0.18, "equity", "exploration", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("exploration program", 0.18, "equity", "exploration", needs_bd_license=True, mode_hint="capital_raise"),
    # --- Mining study stages (pre-FID) ---
    SignalRule("preliminary economic assessment", 0.26, "equity", "pea", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("pre-feasibility", 0.26, "equity", "pfs", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("prefeasibility", 0.26, "equity", "pfs", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("feasibility study", 0.28, "project_debt", "dfs", mode_hint="capital_raise"),
    SignalRule("bankable feasibility", 0.32, "project_debt", "dfs", mode_hint="capital_raise"),
    SignalRule("path to production", 0.20, "equity", "dfs", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("advance toward", 0.12, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    # --- Construction / FID ---
    SignalRule("project financing", 0.30, "project_debt", "construction", mode_hint="capital_raise"),
    SignalRule("construction financing", 0.30, "project_debt", "construction", mode_hint="capital_raise"),
    SignalRule("final investment decision", 0.28, "project_debt", "construction", mode_hint="capital_raise"),
    SignalRule("financial close", 0.24, "project_debt", "construction", mode_hint="capital_raise"),
    # --- Royalty / stream / offtake / JV ---
    SignalRule("offtake agreement", 0.22, "project_debt", "dfs", mode_hint="capital_raise"),
    SignalRule("offtake financing", 0.28, "project_debt", "construction", mode_hint="capital_raise"),
    SignalRule("royalty financing", 0.28, "royalty_streaming", "dfs", mode_hint="capital_raise"),
    SignalRule("streaming agreement", 0.28, "royalty_streaming", "construction", mode_hint="capital_raise"),
    SignalRule("metal stream", 0.26, "royalty_streaming", "construction", mode_hint="capital_raise"),
    SignalRule("nsr royalty", 0.24, "royalty_streaming", "pfs", mode_hint="capital_raise"),
    SignalRule("earn-in", 0.22, "equity", "exploration", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("farm-in", 0.22, "equity", "exploration", needs_bd_license=True, mode_hint="capital_raise"),
    SignalRule("joint venture", 0.16, "equity", "unknown", needs_bd_license=True, mode_hint="capital_raise"),
    # --- A&D / acquisition ---
    SignalRule("acquisition financing", 0.28, "acquisition_finance", "acquisition_ad", mode_hint="acquisition"),
    SignalRule("purchase and sale agreement", 0.18, "acquisition_finance", "acquisition_ad", mode_hint="acquisition"),
    SignalRule("business combination", 0.16, "equity", "acquisition_ad", needs_bd_license=True, mode_hint="acquisition"),
    SignalRule("maturity date", 0.10, "senior_debt", "unknown", mode_hint="refi"),
]

# Query set for junior mining / pre-FID focused scans.
# Prefer AND mining/mineral/gold to cut non-mining private placement noise.
# Note: many TSXV juniors appear on SEDAR+, not EDGAR.
MINING_STAGE_QUERIES = [
    'mining AND "private placement"',
    'mining AND "flow-through"',
    'mining AND "going concern"',
    'mining AND "strategic alternatives"',
    'mining AND "credit facility"',
    'mining AND "feasibility study"',
    'mining AND "preliminary economic assessment"',
    'mining AND "pre-feasibility"',
    'mining AND "construction financing"',
    'mining AND "project financing"',
    'mining AND "streaming agreement"',
    'mining AND "royalty"',
    'mining AND "offtake"',
    'mining AND "earn-in"',
    '"mineral resource"',
    '"preliminary economic assessment"',
    '"feasibility study"',
    "prefeasibility",
    'gold AND "private placement"',
    'copper AND "feasibility"',
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
        "pre-feasibility",
        "flow-through",
        "nsr",
        "drill program",
        "mineral resource",
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
    mode_votes: dict[str, float] = {}
    needs_license = False
    score = 0.0
    notes: list[str] = []

    for rule in RULES:
        if rule.keyword in t:
            hits.append(rule.keyword)
            score += rule.weight
            ask_votes[rule.ask_type_guess] = ask_votes.get(rule.ask_type_guess, 0) + rule.weight
            stage_votes[rule.stage_guess] = stage_votes.get(rule.stage_guess, 0) + rule.weight
            mode_votes[rule.mode_hint] = mode_votes.get(rule.mode_hint, 0) + rule.weight
            needs_license = needs_license or rule.needs_bd_license
            if rule.note:
                notes.append(rule.note)

    ask_type = max(ask_votes, key=ask_votes.get) if ask_votes else "unknown"
    stage = max(stage_votes, key=stage_votes.get) if stage_votes else "unknown"
    mode = max(mode_votes, key=mode_votes.get) if mode_votes else "capital_raise"
    sector = guess_sector(t)

    score = min(score, 1.0)
    return {
        "score": round(score, 3),
        "keywords_hit": hits,
        "ask_type_guess": ask_type,
        "stage_guess": stage,
        "sector_guess": sector,
        "mode_guess": mode,
        "needs_bd_license": needs_license,
        "notes": notes,
    }