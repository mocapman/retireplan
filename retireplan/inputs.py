# inputs.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal, List, Dict, Any
import yaml

Filing = Literal["MFJ", "Single"]
DrawOrder = Literal[
    "IRA, Brokerage, Roth",
    "Brokerage, Roth, IRA",
    "Brokerage, IRA, Roth",
    "Roth, Brokerage, IRA",
]


@dataclass
class Year1Inputs:
    spend: float
    income: float
    cash_events: List[Dict[str, Any]]
    draws: Dict[str, float]  # keys: ira, brokerage, roth
    taxes: float
    roth_conversion: float


@dataclass
class Inputs:
    # Personal
    birth_year_person1: int
    birth_year_person2: Optional[int]
    final_age_person1: int
    final_age_person2: Optional[int]
    filing_status: Filing
    start_year: int

    # Balances
    balances_brokerage: float
    balances_roth: float
    balances_ira: float

    # Spending phases - New model: target spend + percentages
    target_spend: float  # Annual spending target in today's dollars
    gogo_percent: float  # Percentage of target spend for GoGo phase (default 100)
    slow_percent: float  # Percentage of target spend for Slow phase (default 80)  
    nogo_percent: float  # Percentage of target spend for NoGo phase (default 70)
    gogo_years: int
    slow_years: int
    survivor_percent: float

    # Social Security (annual at start age, today's $)
    ss_person1_start_age: int
    ss_person1_annual_at_start: float
    ss_person2_start_age: Optional[int]
    ss_person2_annual_at_start: Optional[float]

    # Rates
    inflation: float
    brokerage_growth: float
    roth_growth: float
    ira_growth: float

    # Tax/health
    magi_target_base: float
    standard_deduction_base: float
    rmd_start_age: int
    aca_end_age: int
    aca_subsidy_annual: Optional[float]

    # Strategy
    draw_order: DrawOrder

    # Year 1 specific inputs
    year1: Year1Inputs


def load_yaml(path: str) -> Inputs:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    b = raw["balances"]
    s = raw["spending"]
    ss = raw["social_security"]
    r = raw["rates"]
    th = raw["tax_health"]
    y1 = raw["year1"]

    i = Inputs(
        birth_year_person1=raw["birth_year_person1"],
        birth_year_person2=raw.get("birth_year_person2"),
        final_age_person1=raw["final_age_person1"],
        final_age_person2=raw.get("final_age_person2"),
        filing_status=raw["filing_status"],
        start_year=raw["start_year"],
        balances_brokerage=b["brokerage"],
        balances_roth=b["roth"],
        balances_ira=b["ira"],
        target_spend=s["target_spend"],
        gogo_percent=s.get("gogo_percent", 100.0),
        slow_percent=s.get("slow_percent", 80.0),
        nogo_percent=s.get("nogo_percent", 70.0),
        gogo_years=s["gogo_years"],
        slow_years=s["slow_years"],
        survivor_percent=s["survivor_percent"],
        ss_person1_start_age=ss["person1_start_age"],
        ss_person1_annual_at_start=ss["person1_annual_at_start"],
        ss_person2_start_age=ss.get("person2_start_age"),
        ss_person2_annual_at_start=ss.get("person2_annual_at_start"),
        inflation=r["inflation"],
        brokerage_growth=r["brokerage_growth"],
        roth_growth=r["roth_growth"],
        ira_growth=r["ira_growth"],
        magi_target_base=th["magi_target_base"],
        standard_deduction_base=th["standard_deduction_base"],
        rmd_start_age=th["rmd_start_age"],
        aca_end_age=th["aca_end_age"],
        aca_subsidy_annual=th.get("aca_subsidy_annual"),
        draw_order=raw.get("draw_order", "IRA, Brokerage, Roth"),
        year1=Year1Inputs(
            spend=y1["spend"],
            income=y1["income"],
            cash_events=y1.get("cash_events", []),
            draws=y1["draws"],
            taxes=y1["taxes"],
            roth_conversion=y1["roth_conversion"],
        ),
    )
    validate(i)
    return i


def validate(i: Inputs) -> None:
    def rng(name: str, val: float, lo: float, hi: float) -> None:
        if not (lo <= val <= hi):
            raise ValueError(f"{name} out of range [{lo},{hi}]: {val}")

    # Years
    for name, y in (
        ("birth_year_person1", i.birth_year_person1),
        ("start_year", i.start_year),
    ):
        rng(name, y, 1900, 2100)
    if i.birth_year_person2 is not None:
        rng("birth_year_person2", i.birth_year_person2, 1900, 2100)

    # Ages
    rng("final_age_person1", i.final_age_person1, 60, 105)
    if i.final_age_person2 is not None:
        rng("final_age_person2", i.final_age_person2, 60, 105)

    # Filing
    if i.filing_status not in ("MFJ", "Single"):
        raise ValueError("filing_status must be MFJ or Single")

    # Rates
    for name, p in (
        ("inflation", i.inflation),
        ("brokerage_growth", i.brokerage_growth),
        ("roth_growth", i.roth_growth),
        ("ira_growth", i.ira_growth),
    ):
        rng(name, p, -0.2, 0.2)

    # Social Security ages
    rng("ss_person1_start_age", i.ss_person1_start_age, 62, 70)
    if i.ss_person2_start_age is not None:
        rng("ss_person2_start_age", i.ss_person2_start_age, 62, 70)

    # Survivor %
    rng("survivor_percent", i.survivor_percent, 50, 100)

    # RMD start
    rng("rmd_start_age", i.rmd_start_age, 70, 80)

    # Draw order
    valid_orders = [
        "IRA, Brokerage, Roth",
        "Brokerage, Roth, IRA",
        "Brokerage, IRA, Roth",
        "Roth, Brokerage, IRA",
    ]
    if i.draw_order not in valid_orders:
        raise ValueError(f"draw_order must be one of: {valid_orders}")

    # Year 1 validation
    if i.year1.spend < 0:
        raise ValueError("year1.spend must be non-negative")
    if i.year1.income < 0:
        raise ValueError("year1.income must be non-negative")
    if i.year1.taxes < 0:
        raise ValueError("year1.taxes must be non-negative")
    if i.year1.roth_conversion < 0:
        raise ValueError("year1.roth_conversion must be non-negative")

    # Validate draws
    for account, amount in i.year1.draws.items():
        if account not in ["ira", "brokerage", "roth"]:
            raise ValueError(
                f"year1.draws key must be one of: ira, brokerage, roth. Got: {account}"
            )
        if amount < 0:
            raise ValueError(f"year1.draws.{account} must be non-negative")

    # Validate cash events
    for event in i.year1.cash_events:
        if "amount" not in event:
            raise ValueError("year1.cash_events must have an 'amount' field")
        if "from_account" in event and event["from_account"] not in [
            "IRA",
            "Brokerage",
            "Roth",
        ]:
            raise ValueError(
                "year1.cash_events.from_account must be one of: IRA, Brokerage, Roth"
            )
