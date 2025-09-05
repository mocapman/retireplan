from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any

import yaml

Filing = Literal["MFJ", "Single"]


@dataclass
class Inputs:
    birth_year_you: int
    birth_year_spouse: Optional[int]
    final_age_you: int
    final_age_spouse: Optional[int]
    filing_status: Filing
    start_year: int
    balances_brokerage: float
    balances_roth: float
    balances_ira: float
    gogo_annual: float
    slow_annual: float
    nogo_annual: float
    gogo_years: int
    slow_years: int
    survivor_percent: float
    ss_you_start_age: int
    ss_you_annual_at_start: float
    ss_spouse_start_age: Optional[int]
    ss_spouse_annual_at_start: Optional[float]
    inflation: float
    brokerage_growth: float
    roth_growth: float
    ira_growth: float
    magi_target_base: float
    standard_deduction_base: float
    rmd_start_age: int
    aca_end_age: int
    aca_subsidy_annual: Optional[float] = None


def _req(d: Dict[str, Any], path: str):
    for key in path.split("."):
        d = d[key]
    return d


def load_yaml(path: str) -> Inputs:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    b = raw["balances"]
    s = raw["spending"]
    ss = raw["social_security"]
    r = raw["rates"]
    th = raw["tax_health"]

    i = Inputs(
        birth_year_you=raw["birth_year_you"],
        birth_year_spouse=raw.get("birth_year_spouse"),
        final_age_you=raw["final_age_you"],
        final_age_spouse=raw.get("final_age_spouse"),
        filing_status=raw["filing_status"],
        start_year=raw["start_year"],
        balances_brokerage=b["brokerage"],
        balances_roth=b["roth"],
        balances_ira=b["ira"],
        gogo_annual=s["gogo_annual"],
        slow_annual=s["slow_annual"],
        nogo_annual=s["nogo_annual"],
        gogo_years=s["gogo_years"],
        slow_years=s["slow_years"],
        survivor_percent=s["survivor_percent"],
        ss_you_start_age=ss["you_start_age"],
        ss_you_annual_at_start=ss["you_annual_at_start"],
        ss_spouse_start_age=ss.get("spouse_start_age"),
        ss_spouse_annual_at_start=ss.get("spouse_annual_at_start"),
        inflation=r["inflation"],
        brokerage_growth=r["brokerage_growth"],
        roth_growth=r["roth_growth"],
        ira_growth=r["ira_growth"],
        magi_target_base=th["magi_target_base"],
        standard_deduction_base=th["standard_deduction_base"],
        rmd_start_age=th["rmd_start_age"],
        aca_end_age=th["aca_end_age"],
        aca_subsidy_annual=th.get("aca_subsidy_annual"),
    )
    validate(i)
    return i


def validate(i: Inputs) -> None:
    def rng(name, val, lo, hi):
        if not (lo <= val <= hi):
            raise ValueError(f"{name} out of range [{lo},{hi}]: {val}")

    for y in (i.birth_year_you, i.start_year):
        rng("year", y, 1900, 2100)
    if i.birth_year_spouse is not None:
        rng("birth_year_spouse", i.birth_year_spouse, 1900, 2100)

    for age in (i.final_age_you,):
        rng("final_age_you", age, 60, 105)
    if i.final_age_spouse is not None:
        rng("final_age_spouse", i.final_age_spouse, 60, 105)

    if i.filing_status not in ("MFJ", "Single"):
        raise ValueError("filing_status must be MFJ or Single")

    for p in (i.inflation, i.brokerage_growth, i.roth_growth, i.ira_growth):
        rng("rate", p, -0.2, 0.2)

    rng("ss_you_start_age", i.ss_you_start_age, 62, 70)
    if i.ss_spouse_start_age is not None:
        rng("ss_spouse_start_age", i.ss_spouse_start_age, 62, 70)

    rng("survivor_percent", i.survivor_percent, 50, 100)
    rng("rmd_start_age", i.rmd_start_age, 70, 80)
