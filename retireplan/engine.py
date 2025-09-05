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
):
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
    # Events by year (amount >0 = extra spend category; <0 = inflow). Cash-only.
    ev_by_year: dict[int, list[dict]] = {}
    for e in events or []:
        ev_by_year.setdefault(int(e["year"]), []).append(e)

    years = make_years(
        cfg.start_year,
        cfg.birth_year_you,
        cfg.birth_year_spouse,
        cfg.final_age_you,
        cfg.final_age_spouse,
        cfg.gogo_years,
        cfg.slow_years,
    )

    # Running end balances
    b_end = float(cfg.balances_brokerage)
    r_end = float(cfg.balances_roth)
    i_end = float(cfg.balances_ira)

    order = (
        ("IRA", "Brokerage", "Roth")
        if cfg.draw_order == "IRA, Brokerage, Roth"
        else ("Brokerage", "Roth", "IRA")
    )
    rows: list[dict] = []

    for idx, yc in enumerate(years):
        infl = _infl_factor(cfg.inflation, idx)
        std_ded = cfg.standard_deduction_base * infl
        target_magi = (
            cfg.magi_target_base * infl
            if (yc.you_alive and yc.age_you < cfg.aca_end_age)
            else 0.0
        )
        filing_this_year = (
            "MFJ" if (cfg.filing_status == "MFJ" and yc.living == "Joint") else "Single"
        )

        # Annual budget (includes taxes and events), inflation + survivor adjust
        budget = spend_target(
            phase=yc.phase,
            year_index=idx,
            infl=cfg.inflation,
            gogo=cfg.gogo_annual,
            slow=cfg.slow_annual,
            nogo=cfg.nogo_annual,
            survivor_pct=cfg.survivor_percent,
            living=yc.living,
        )

        # Social Security with survivor step-up
        you_sched = ss_for_year(
            yc.age_you,
            cfg.ss_you_start_age,
            cfg.ss_you_annual_at_start,
            idx,
            cfg.inflation,
        )
        sp_sched = ss_for_year(
            yc.age_spouse,
            cfg.ss_spouse_start_age,
            cfg.ss_spouse_annual_at_start,
            idx,
            cfg.inflation,
        )
        if yc.you_alive and yc.spouse_alive:
            ss_inc = you_sched + sp_sched
        elif yc.you_alive and not yc.spouse_alive:
            ss_inc = max(you_sched, sp_sched)
        elif (not yc.you_alive) and yc.spouse_alive:
            ss_inc = max(you_sched, sp_sched)
        else:
            ss_inc = 0.0

        # Events (inside the budget; they reduce discretionary)
        ev_amt = sum(float(e.get("amount", 0.0)) for e in ev_by_year.get(yc.year, []))

        # RMD if owner alive and ≥ start age
        rmd = 0.0
        if yc.you_alive and yc.age_you >= cfg.rmd_start_age and i_end > 0.0:
            rmd = i_end / rmd_factor(yc.age_you)

        # Cash needed to meet the budget (taxes are inside the budget)
        need_for_budget = max(0.0, budget - ss_inc - rmd)

        # Withdraw to meet budget; IRA reduced by RMD before draws
        d_b, d_r, d_i, b1, r1, i1, unmet = _withdraw_local(
            b_end, r_end, i_end - rmd, need_for_budget, order
        )

        # Provided cash and shortfall against budget
        provided_cash = ss_inc + rmd + d_b + d_r + d_i
        shortfall = max(0.0, budget - provided_cash)

        # Taxes/MAGI for composition; conversions next
        def tax_and_magi(conv: float):
            tax, _ss_tax, _taxable, magi = compute_tax_magi(
                ira_ordinary=(rmd + d_i),
                roth_conversion=conv,
                ss_total=ss_inc,
                std_deduction=std_ded,
                filing=filing_this_year,
            )
            return tax, magi

        # Fill conversions up to MAGI target (pre-Medicare), limited by post-draw IRA capacity
        conv = 0.0
        for _ in range(8):
            tax0, magi0 = tax_and_magi(conv)
            if target_magi <= 0.0 or not yc.you_alive or yc.age_you >= cfg.aca_end_age:
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
        conv_eff = min(conv, max(0.0, i1))
        i1 -= conv_eff
        r1 += conv_eff

        # Sweep ONLY RMD surplus (no SS sweep)
        need_after_ss = max(0.0, budget - ss_inc)
        rmd_surplus = max(0.0, rmd - need_after_ss)
        b1 += rmd_surplus

        # Year-end growth
        b_out = b1 * (1.0 + cfg.brokerage_growth)
        r_out = r1 * (1.0 + cfg.roth_growth)
        i_out = i1 * (1.0 + cfg.ira_growth)

        # Commit
        b_end, r_end, i_end = b_out, r_out, i_out

        rows.append(
            {
                "Year": yc.year,
                "Age_You": yc.age_you,
                "Age_Spouse": yc.age_spouse,
                "Phase": yc.phase,
                "Living": yc.living,
                # Budgeting
                "Spend_Target": round(
                    budget
                ),  # total annual budget incl. taxes and events
                "Taxes": round(tax),
                "Events_Cash": round(ev_amt),
                "Total_Spend": round(budget),  # equals budget by definition
                # Flows
                "SS_Income": round(ss_inc),
                "Draw_Brokerage": round(d_b),
                "Draw_Roth": round(d_r),
                "Draw_IRA": round(d_i),  # excludes RMD
                "Roth_Conversion": round(conv_eff),
                "RMD": round(rmd),
                "MAGI": round(magi),
                "Std_Deduction": round(std_ded),
                # Balances
                "End_Bal_Brokerage": round(b_out),
                "End_Bal_Roth": round(r_out),
                "End_Bal_IRA": round(i_out),
                "Total_Assets": round(b_out + r_out + i_out),
                # Shortfall
                "Shortfall": round(shortfall),
            }
        )

    return rows
