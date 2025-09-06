# engine.py
from __future__ import annotations

from typing import Iterable, Tuple
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 10  # 10 decimal places of precision

from retireplan.policy import rmd_factor
from retireplan.social_security import ss_for_year
from retireplan.spending import spend_target
from retireplan.taxes import compute_tax_magi
from retireplan.timeline import make_years
from retireplan.precision import round_dollar, round_percent, round_year


def _infl_factor(rate: float, idx: int) -> Decimal:
    return (Decimal(1) + Decimal(str(rate))) ** idx


def _withdraw_local(
    b: Decimal, r: Decimal, i: Decimal, need: Decimal, order: Tuple[str, str, str]
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    """Withdraw in the given order; returns draws, end balances, and remaining unmet need."""
    remaining = max(Decimal(0), need)
    draws = {"Brokerage": Decimal(0), "Roth": Decimal(0), "IRA": Decimal(0)}
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
        if remaining <= Decimal("1e-9"):
            break
    return draws["Brokerage"], draws["Roth"], draws["IRA"], b, r, i, remaining


def _parse_draw_order(draw_order: str) -> Tuple[str, str, str]:
    """Parse the draw order string into a tuple of account types."""
    parts = [part.strip() for part in draw_order.split(",")]
    return tuple(parts)


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

    # Running end balances (converted to Decimal for precision)
    brokerage_end = Decimal(str(cfg.balances_brokerage))
    roth_end = Decimal(str(cfg.balances_roth))
    ira_end = Decimal(str(cfg.balances_ira))

    # Parse the draw order
    order = _parse_draw_order(cfg.draw_order)

    rows: list[dict] = []

    for idx, yc in enumerate(years):
        infl = _infl_factor(cfg.inflation, idx)
        std_ded = Decimal(str(cfg.standard_deduction_base)) * infl

        # Determine filing status based on living status
        filing_status = "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"

        # Pre-Medicare MAGI target inflates; otherwise zero
        target_magi = (
            Decimal(str(cfg.magi_target_base)) * infl
            if (yc.person1_alive and yc.age_person1 < cfg.aca_end_age)
            else Decimal(0)
        )

        # Annual budget (includes taxes and events), inflation + survivor adjust
        total_spend = Decimal(
            str(
                spend_target(
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
            )
        )

        # Social Security with survivor step-up
        ss_person1 = Decimal(
            str(
                ss_for_year(
                    yc.age_person1,
                    cfg.ss_person1_start_age,
                    cfg.ss_person1_annual_at_start,
                    idx,
                    cfg.inflation,
                )
            )
        )
        ss_person2 = Decimal(
            str(
                ss_for_year(
                    yc.age_person2,
                    cfg.ss_person2_start_age,
                    cfg.ss_person2_annual_at_start,
                    idx,
                    cfg.inflation,
                )
            )
        )
        if yc.person1_alive and yc.person2_alive:
            ss_income = ss_person1 + ss_person2
        elif yc.person1_alive and not yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
        elif (not yc.person1_alive) and yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
        else:
            ss_income = Decimal(0)

        # Events (inside the budget; they reduce discretionary)
        events_cash = Decimal(0)
        for e in ev_by_year.get(yc.year, []):
            events_cash += Decimal(str(e.get("amount", 0)))

        # RMD if owner alive and ≥ start age
        rmd = Decimal(0)
        if (
            yc.person1_alive
            and yc.age_person1 >= cfg.rmd_start_age
            and ira_end > Decimal(0)
        ):
            rmd = ira_end / Decimal(str(rmd_factor(yc.age_person1)))

        # Cash needed to meet the budget (taxes are inside the budget)
        need_for_budget = max(Decimal(0), total_spend - ss_income - rmd)

        # Withdraw to meet budget; IRA reduced by RMD before draws
        draw_broke, draw_roth, draw_ira, b1, r1, i1, unmet = _withdraw_local(
            brokerage_end, roth_end, ira_end - rmd, need_for_budget, order
        )

        # Provided cash and shortfall against budget
        provided_cash = ss_income + rmd + draw_broke + draw_roth + draw_ira
        shortfall = max(Decimal(0), total_spend - provided_cash)

        # Taxes/MAGI for composition; conversions next
        def tax_and_magi(conv: Decimal) -> tuple[Decimal, Decimal]:
            tax, _ss_tax, _taxable, magi = compute_tax_magi(
                ira_ordinary=float(rmd + draw_ira + conv),
                roth_conversion=float(conv),
                ss_total=float(ss_income),
                std_deduction=float(std_ded),
                filing=filing_status,
            )
            return Decimal(str(tax)), Decimal(str(magi))

        # Fill conversions up to MAGI target (pre-Medicare), limited by post-draw IRA capacity
        conv = Decimal(0)
        for _ in range(8):  # Limit iterations to prevent infinite loop
            tax0, magi0 = tax_and_magi(conv)

            if (
                target_magi <= Decimal(0)
                or not yc.person1_alive
                or yc.age_person1 >= cfg.aca_end_age
            ):
                break

            gap = target_magi - magi0
            if gap <= Decimal("1.0"):
                break

            cap = max(Decimal(0), i1)
            step = min(gap, cap - conv)
            if step <= Decimal("1.0"):
                break

            conv += step

        # Apply conversion (IRA -> Roth)
        roth_conv = min(conv, max(Decimal(0), i1))
        i1 -= roth_conv
        r1 += roth_conv

        # Recalculate tax with final conversion amount
        tax, magi = tax_and_magi(roth_conv)

        # Sweep ONLY RMD surplus (no SS sweep)
        need_after_ss = max(Decimal(0), total_spend - ss_income)
        rmd_surplus = max(Decimal(0), rmd - need_after_ss)
        b1 += rmd_surplus

        # Year-end growth
        broke_bal = b1 * (Decimal(1) + Decimal(str(cfg.brokerage_growth)))
        roth_bal = r1 * (Decimal(1) + Decimal(str(cfg.roth_growth)))
        ira_bal = i1 * (Decimal(1) + Decimal(str(cfg.ira_growth)))

        # Commit running balances
        brokerage_end, roth_end, ira_end = broke_bal, roth_bal, ira_bal

        # Discretionary inside the gross budget
        base_spend = max(Decimal(0), total_spend - tax - events_cash)

        # Apply rounding to all monetary values
        row_data = {
            # Timeline
            "Year": round_year(yc.year),
            "Person1_Age": round_year(yc.age_person1),
            "Person2_Age": round_year(yc.age_person2),
            "Lifestyle": yc.phase,
            "Filing": filing_status,
            # Budgeting
            "Total_Spend": round_dollar(total_spend),
            "Taxes_Due": round_dollar(tax),
            "Cash_Events": round_dollar(events_cash),
            "Base_Spend": round_dollar(base_spend),
            # Flows
            "Social_Security": round_dollar(ss_income),
            "IRA_Draw": round_dollar(draw_ira),  # excludes RMD
            "Brokerage_Draw": round_dollar(draw_broke),
            "Roth_Draw": round_dollar(draw_roth),
            "Roth_Conversion": round_dollar(roth_conv),
            "RMD": round_dollar(rmd),
            "MAGI": round_dollar(magi),
            "Std_Deduction": round_dollar(std_ded),
            # Balances
            "IRA_Balance": round_dollar(ira_bal),
            "Brokerage_Balance": round_dollar(broke_bal),
            "Roth_Balance": round_dollar(roth_bal),
            "Total_Assets": round_dollar(broke_bal + roth_bal + ira_bal),
            # Shortfall
            "Shortfall": round_dollar(shortfall),
        }

        rows.append(row_data)

    return rows
