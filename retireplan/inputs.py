from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal
import yaml

Filing = Literal["MFJ", "Single"]
DrawOrder = Literal[
    "IRA, Brokerage, Roth",
    "Brokerage, Roth, IRA",
    "Brokerage, IRA, Roth",
    "Roth, Brokerage, IRA",
]


@dataclass
class Inputs:
    # Personal
    birth_year_person1: int
    birth_year_person2: Optional[int]
    final_age_person1: int
    final_age_person2: Optional[int]
    filing_status: Filing

    # Balances
    balances_brokerage: float
    balances_roth: float
    balances_ira: float

    # Spending (Start Year is now under spending)
    start_year: int
    year1_spend: float
    year1_cash_events: float
    year1_brokerage_draw: float
    year1_ira_draw: float
    year1_roth_draw: float
    target_spend: float
    gogo_percent: float
    slow_percent: float
    nogo_percent: float
    gogo_years: int
    slow_years: int
    survivor_percent: float

    # Social Security
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


def load_yaml(path: str) -> Inputs:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    b = raw["balances"]
    s = raw["spending"]
    ss = raw["social_security"]
    r = raw["rates"]
    th = raw["tax_health"]

    i = Inputs(
        birth_year_person1=raw["birth_year_person1"],
        birth_year_person2=raw.get("birth_year_person2"),
        final_age_person1=raw["final_age_person1"],
        final_age_person2=raw.get("final_age_person2"),
        filing_status=raw["filing_status"],
        balances_brokerage=b["brokerage"],
        balances_roth=b["roth"],
        balances_ira=b["ira"],
        # start_year now from spending
        start_year=s["start_year"],
        year1_spend=s.get("year1_spend", 0),
        year1_cash_events=s.get("year1_cash_events", 0),
        year1_brokerage_draw=s.get("year1_brokerage_draw", 0),
        year1_ira_draw=s.get("year1_ira_draw", 0),
        year1_roth_draw=s.get("year1_roth_draw", 0),
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
    )
    validate(i)
    return i


def validate(i: Inputs) -> None:
    def rng(name: str, val: float, lo: float, hi: float) -> None:
        if not (lo <= val <= hi):
            raise ValueError(f"{name} out of range [{lo},{hi}]: {val}")

    for name, y in (
        ("birth_year_person1", i.birth_year_person1),
        ("start_year", i.start_year),
    ):
        rng(name, y, 1900, 2100)
    if i.birth_year_person2 is not None:
        rng("birth_year_person2", i.birth_year_person2, 1900, 2100)
    rng("final_age_person1", i.final_age_person1, 60, 105)
    if i.final_age_person2 is not None:
        rng("final_age_person2", i.final_age_person2, 60, 105)
    if i.filing_status not in ("MFJ", "Single"):
        raise ValueError("filing_status must be MFJ or Single")
    for name, p in (
        ("inflation", i.inflation),
        ("brokerage_growth", i.brokerage_growth),
        ("roth_growth", i.roth_growth),
        ("ira_growth", i.ira_growth),
    ):
        rng(name, p, -0.2, 0.2)
    rng("ss_person1_start_age", i.ss_person1_start_age, 62, 70)
    if i.ss_person2_start_age is not None:
        rng("ss_person2_start_age", i.ss_person2_start_age, 62, 70)
    rng("survivor_percent", i.survivor_percent, 50, 100)
    rng("rmd_start_age", i.rmd_start_age, 70, 80)
    valid_orders = [
        "IRA, Brokerage, Roth",
        "Brokerage, Roth, IRA",
        "Brokerage, IRA, Roth",
        "Roth, Brokerage, IRA",
    ]
    if i.draw_order not in valid_orders:
        raise ValueError(f"draw_order must be one of: {valid_orders}")
