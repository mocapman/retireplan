from __future__ import annotations

from typing import Iterable, Tuple

from retireplan.policy import rmd_factor
from retireplan.social_security import ss_for_year
from retireplan.spending import spend_target
from retireplan.taxes import compute_tax_magi
from retireplan.timeline import make_years


def _infl_factor(rate: float, idx: int) -> float:
    return (1.0 + rate) ** idx


def _withdraw_local(
    b: float, r: float, i: float, need: float, order: Tuple[str, str, str]
) -> tuple[float, float, float, float, float, float, float]:
    """Withdraw in the given order; returns draws, end balances, and remaining unmet need."""
    remaining = max(0.0, need)
    draws = {"Brokerage": 0.0, "Roth": 0.0, "IRA": 0.0}
    for leg in order:
        cap = b if leg == "Brokerage" else r if leg == "Roth" else i
        take = min(cap, remaining)
        if leg == "Brokerage":
            b -= take
        elif leg == "Roth":
            r -= take
        else:
            i -= take
        draws[leg] += take
        remaining -= take
        if remaining <= 1e-9:
            break
    return draws["Brokerage"], draws["Roth"], draws["IRA"], b, r, i, remaining


def run_plan(cfg, events: Iterable[dict] | None = None) -> list[dict]:
    # Events by year (amount >0 = extra spend; <0 = inflow). Cash-only.
    ev_by_year: dict[int, list[dict]] = {}
    for e in events or []:
        ev_by_year.setdefault(int(e["year"]), []).append(e)

    years = make_years(
        cfg.start_year,
        cfg.birth_year_person1,
        cfg.birth_year_person2,
        cfg.final_age_person1,
        cfg.final_age_person2,
        cfg.gogo_years,
        cfg.slow_years,
    )

    # Running end balances
    brokerage_end = float(cfg.balances_brokerage)
    roth_end = float(cfg.balances_roth)
    ira_end = float(cfg.balances_ira)

    order = (
        ("IRA", "Brokerage", "Roth")
        if cfg.draw_order == "IRA, Brokerage, Roth"
        else ("Brokerage", "Roth", "IRA")
    )

    rows: list[dict] = []

    for idx, yc in enumerate(years):
        infl = _infl_factor(cfg.inflation, idx)
        std_ded = cfg.standard_deduction_base * infl

        # Filing for this year is MFJ only if elected MFJ and both alive; else Single
        filing_status = (
            "MFJ"
            if (cfg.filing_status == "MFJ" and yc.person1_alive and yc.person2_alive)
            else "Single"
        )

        # Pre-Medicare MAGI target inflates; otherwise zero
        target_magi = (
            cfg.magi_target_base * infl
            if (yc.person1_alive and yc.age_person1 < cfg.aca_end_age)
            else 0.0
        )

        # Annual budget (includes taxes and events), inflation + survivor adjust
        total_spend = spend_target(
            phase=yc.phase,
            year_index=idx,
            infl=cfg.inflation,
            gogo=cfg.gogo_annual,
            slow=cfg.slow_annual,
            nogo=cfg.nogo_annual,
            survivor_pct=cfg.survivor_percent,
            person1_alive=yc.person1_alive,
            person2_alive=yc.person2_alive,
        )

        # Social Security with survivor step-up
        ss_person1 = ss_for_year(
            yc.age_person1,
            cfg.ss_person1_start_age,
            cfg.ss_person1_annual_at_start,
            idx,
            cfg.inflation,
        )
        ss_person2 = ss_for_year(
            yc.age_person2,
            cfg.ss_person2_start_age,
            cfg.ss_person2_annual_at_start,
            idx,
            cfg.inflation,
        )
        if yc.person1_alive and yc.person2_alive:
            ss_income = ss_person1 + ss_person2
        elif yc.person1_alive and not yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
        elif (not yc.person1_alive) and yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
        else:
            ss_income = 0.0

        # Events (inside the budget; they reduce discretionary)
        events_cash = sum(
            float(e.get("amount", 0.0)) for e in ev_by_year.get(yc.year, [])
        )

        # RMD if owner alive and ≥ start age
        rmd = 0.0
        if yc.person1_alive and yc.age_person1 >= cfg.rmd_start_age and ira_end > 0.0:
            rmd = ira_end / rmd_factor(yc.age_person1)

        # Cash needed to meet the budget (taxes are inside the budget)
        need_for_budget = max(0.0, total_spend - ss_income - rmd)

        # Withdraw to meet budget; IRA reduced by RMD before draws
        draw_broke, draw_roth, draw_ira, b1, r1, i1, unmet = _withdraw_local(
            brokerage_end, roth_end, ira_end - rmd, need_for_budget, order
        )

        # Provided cash and shortfall against budget
        provided_cash = ss_income + rmd + draw_broke + draw_roth + draw_ira
        shortfall = max(0.0, total_spend - provided_cash)

        # Taxes/MAGI for composition; conversions next
        def tax_and_magi(conv: float) -> tuple[float, float]:
            tax, _ss_tax, _taxable, magi = compute_tax_magi(
                ira_ordinary=(rmd + draw_ira),
                roth_conversion=conv,
                ss_total=ss_income,
                std_deduction=std_ded,
                filing=filing_status,
            )
            return tax, magi

        # Fill conversions up to MAGI target (pre-Medicare), limited by post-draw IRA capacity
        conv = 0.0
        for _ in range(8):
            tax0, magi0 = tax_and_magi(conv)
            if (
                target_magi <= 0.0
                or not yc.person1_alive
                or yc.age_person1 >= cfg.aca_end_age
            ):
                break
            gap = target_magi - magi0
            if gap <= 1.0:
                break
            cap = max(0.0, i1)
            step = min(gap, cap - conv)
            if step <= 1.0:
                break
            conv += step

        tax, magi = tax_and_magi(conv)

        # Apply conversion (IRA -> Roth)
        roth_conv = min(conv, max(0.0, i1))
        i1 -= roth_conv
        r1 += roth_conv

        # Sweep ONLY RMD surplus (no SS sweep)
        need_after_ss = max(0.0, total_spend - ss_income)
        rmd_surplus = max(0.0, rmd - need_after_ss)
        b1 += rmd_surplus

        # Year-end growth
        broke_bal = b1 * (1.0 + cfg.brokerage_growth)
        roth_bal = r1 * (1.0 + cfg.roth_growth)
        ira_bal = i1 * (1.0 + cfg.ira_growth)

        # Commit running balances
        brokerage_end, roth_end, ira_end = broke_bal, roth_bal, ira_bal

        # Discretionary inside the gross budget
        base_spend = max(0.0, total_spend - tax - events_cash)

        # Emit canon-aligned row
        rows.append(
            {
                # Timeline
                "Year": yc.year,
                "Person1_Age": yc.age_person1,
                "Person2_Age": yc.age_person2,
                "Lifestyle": yc.phase,
                "Filing": filing_status,
                # Budgeting
                "Total_Spend": round(total_spend),
                "Taxes_Due": round(tax),
                "Cash_Events": round(events_cash),
                "Base_Spend": round(base_spend),
                # Flows
                "Social_Security": round(ss_income),
                "IRA_Draw": round(draw_ira),  # excludes RMD
                "Brokerage_Draw": round(draw_broke),
                "Roth_Draw": round(draw_roth),
                "Roth_Conversion": round(roth_conv),
                "RMD": round(rmd),
                "MAGI": round(magi),
                "Std_Deduction": round(std_ded),
                # Balances
                "IRA_Balance": round(ira_bal),
                "Brokerage_Balance": round(broke_bal),
                "Roth_Balance": round(roth_bal),
                "Total_Assets": round(broke_bal + roth_bal + ira_bal),
                # Shortfall
                "Shortfall": round(shortfall),
            }
        )

    return rows
