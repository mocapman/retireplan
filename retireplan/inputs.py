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
    brokerage_cash: float
    brokerage_cost_basis: float
    brokerage_unrealized_gain: float
    balances_roth: float
    balances_ira: float

    # Spending (Start Year is now under spending)
    start_year: int
    year1_spend: float
    year1_brokerage_draw: float
    year1_ira_draw: float
    year1_roth_draw: float
    year1_magi_floor: float
    year1_magi_target: float
    year1_magi_ceiling: float
    year1_extra_magi_income: float
    year1_magi_loss_offset: float
    year1_planned_roth_conversion: float
    year1_roth_conversion: float
    year1_magi_income: float
    year1_magi_losses: float
    year1_income_to_date: float
    year1_projected_income: float
    year1_capital_gains_to_date: float
    year1_projected_capital_gains: float
    year1_capital_losses_to_date: float
    year1_projected_capital_losses: float
    aca_magi_floor: float
    aca_magi_target: float
    aca_magi_ceiling: float
    aca_extra_magi_income: float
    aca_magi_loss_offset: float
    aca_planned_roth_conversion: float
    aca_annual_magi_income: float
    aca_annual_magi_loss: float
    aca_annual_roth_conversion: float
    medicare_magi_floor: float
    medicare_magi_target: float
    medicare_magi_ceiling: float
    medicare_extra_magi_income: float
    medicare_magi_loss_offset: float
    medicare_planned_roth_conversion: float
    medicare_annual_magi_income: float
    medicare_annual_magi_loss: float
    medicare_annual_roth_conversion: float
    magi_income_ytd: float
    magi_income_projected: float
    magi_income_annual: float
    magi_income_years: float
    magi_gains_ytd: float
    magi_gains_projected: float
    magi_gains_annual: float
    magi_gains_years: float
    magi_losses_ytd: float
    magi_losses_projected: float
    magi_losses_annual: float
    magi_losses_years: float
    magi_conversions_ytd: float
    magi_conversions_projected: float
    magi_conversions_annual: float
    magi_conversions_years: float
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
    estimated_state_deduction: float
    estimated_state_tax_rate: float
    rmd_start_age: int
    aca_end_age: int
    magi_floor_base: float
    magi_ceiling_base: float
    medicare_magi_ceiling_base: float

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
    brokerage_cash = b.get("brokerage_cash")
    brokerage_cost_basis = b.get("brokerage_cost_basis")
    brokerage_unrealized_gain = b.get("brokerage_unrealized_gain")
    if (
        brokerage_cash is None
        and brokerage_cost_basis is None
        and brokerage_unrealized_gain is None
    ):
        brokerage_cash = b.get("brokerage", 0)
        brokerage_cost_basis = 0
        brokerage_unrealized_gain = 0
    else:
        brokerage_cash = brokerage_cash or 0
        brokerage_cost_basis = brokerage_cost_basis or 0
        brokerage_unrealized_gain = brokerage_unrealized_gain or 0
    balances_brokerage = (
        brokerage_cash + brokerage_cost_basis + brokerage_unrealized_gain
    )

    i = Inputs(
        birth_year_person1=raw["birth_year_person1"],
        birth_year_person2=raw.get("birth_year_person2"),
        final_age_person1=raw["final_age_person1"],
        final_age_person2=raw.get("final_age_person2"),
        filing_status=raw["filing_status"],
        balances_brokerage=balances_brokerage,
        brokerage_cash=brokerage_cash,
        brokerage_cost_basis=brokerage_cost_basis,
        brokerage_unrealized_gain=brokerage_unrealized_gain,
        balances_roth=b["roth"],
        balances_ira=b["ira"],
        # start_year now from spending
        start_year=s["start_year"],
        year1_spend=s.get("year1_spend", 0),
        year1_brokerage_draw=s.get("year1_brokerage_draw", 0),
        year1_ira_draw=s.get("year1_ira_draw", 0),
        year1_roth_draw=s.get("year1_roth_draw", 0),
        year1_magi_floor=s.get("year1_magi_floor", th.get("magi_floor_base", 0)),
        year1_magi_target=s.get("year1_magi_target", th.get("magi_target_base", 0)),
        year1_magi_ceiling=s.get("year1_magi_ceiling", th.get("magi_ceiling_base", 0)),
        year1_extra_magi_income=s.get(
            "year1_extra_magi_income", s.get("year1_magi_income", 0)
        ),
        year1_magi_loss_offset=s.get(
            "year1_magi_loss_offset", s.get("year1_magi_losses", 0)
        ),
        year1_planned_roth_conversion=s.get(
            "year1_planned_roth_conversion", s.get("year1_roth_conversion", 0)
        ),
        year1_roth_conversion=s.get(
            "year1_roth_conversion", s.get("year1_planned_roth_conversion", 0)
        ),
        year1_magi_income=s.get(
            "year1_magi_income", s.get("year1_extra_magi_income", 0)
        ),
        year1_magi_losses=s.get(
            "year1_magi_losses", s.get("year1_magi_loss_offset", 0)
        ),
        year1_income_to_date=s.get("year1_income_to_date", 0),
        year1_projected_income=s.get("year1_projected_income", 0),
        year1_capital_gains_to_date=s.get("year1_capital_gains_to_date", 0),
        year1_projected_capital_gains=s.get("year1_projected_capital_gains", 0),
        year1_capital_losses_to_date=s.get("year1_capital_losses_to_date", 0),
        year1_projected_capital_losses=s.get("year1_projected_capital_losses", 0),
        aca_magi_floor=s.get("aca_magi_floor", th.get("magi_floor_base", 0)),
        aca_magi_target=s.get("aca_magi_target", th.get("magi_target_base", 0)),
        aca_magi_ceiling=s.get("aca_magi_ceiling", th.get("magi_ceiling_base", 0)),
        aca_extra_magi_income=s.get(
            "aca_extra_magi_income", s.get("aca_annual_magi_income", 0)
        ),
        aca_magi_loss_offset=s.get(
            "aca_magi_loss_offset", s.get("aca_annual_magi_loss", 0)
        ),
        aca_planned_roth_conversion=s.get(
            "aca_planned_roth_conversion", s.get("aca_annual_roth_conversion", 0)
        ),
        aca_annual_magi_income=s.get(
            "aca_annual_magi_income", s.get("aca_extra_magi_income", 0)
        ),
        aca_annual_magi_loss=s.get(
            "aca_annual_magi_loss", s.get("aca_magi_loss_offset", 0)
        ),
        aca_annual_roth_conversion=s.get(
            "aca_annual_roth_conversion", s.get("aca_planned_roth_conversion", 0)
        ),
        medicare_magi_floor=s.get("medicare_magi_floor", th.get("magi_floor_base", 0)),
        medicare_magi_target=s.get(
            "medicare_magi_target",
            th.get("medicare_magi_ceiling_base", th.get("magi_target_base", 0)),
        ),
        medicare_magi_ceiling=s.get(
            "medicare_magi_ceiling",
            th.get("medicare_magi_ceiling_base", th.get("magi_ceiling_base", 0)),
        ),
        medicare_extra_magi_income=s.get(
            "medicare_extra_magi_income", s.get("medicare_annual_magi_income", 0)
        ),
        medicare_magi_loss_offset=s.get(
            "medicare_magi_loss_offset", s.get("medicare_annual_magi_loss", 0)
        ),
        medicare_planned_roth_conversion=s.get(
            "medicare_planned_roth_conversion",
            s.get("medicare_annual_roth_conversion", 0),
        ),
        medicare_annual_magi_income=s.get(
            "medicare_annual_magi_income", s.get("medicare_extra_magi_income", 0)
        ),
        medicare_annual_magi_loss=s.get(
            "medicare_annual_magi_loss", s.get("medicare_magi_loss_offset", 0)
        ),
        medicare_annual_roth_conversion=s.get(
            "medicare_annual_roth_conversion",
            s.get("medicare_planned_roth_conversion", 0),
        ),
        magi_income_ytd=s.get("magi_income_ytd", 0),
        magi_income_projected=s.get("magi_income_projected", 0),
        magi_income_annual=s.get("magi_income_annual", 0),
        magi_income_years=s.get("magi_income_years", 0),
        magi_gains_ytd=s.get("magi_gains_ytd", 0),
        magi_gains_projected=s.get("magi_gains_projected", 0),
        magi_gains_annual=s.get("magi_gains_annual", 0),
        magi_gains_years=s.get("magi_gains_years", 0),
        magi_losses_ytd=s.get("magi_losses_ytd", 0),
        magi_losses_projected=s.get("magi_losses_projected", 0),
        magi_losses_annual=s.get("magi_losses_annual", 0),
        magi_losses_years=s.get("magi_losses_years", 0),
        magi_conversions_ytd=s.get("magi_conversions_ytd", 0),
        magi_conversions_projected=s.get("magi_conversions_projected", 0),
        magi_conversions_annual=s.get("magi_conversions_annual", 0),
        magi_conversions_years=s.get("magi_conversions_years", 0),
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
        estimated_state_deduction=th.get("estimated_state_deduction", 0),
        estimated_state_tax_rate=th.get("estimated_state_tax_rate", 0.0875),
        rmd_start_age=th["rmd_start_age"],
        aca_end_age=th["aca_end_age"],
        magi_floor_base=th.get("magi_floor_base", 0),
        magi_ceiling_base=th.get("magi_ceiling_base", 0),
        medicare_magi_ceiling_base=th.get(
            "medicare_magi_ceiling_base", th.get("magi_ceiling_base", 0)
        ),
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
