from __future__ import annotations

from typing import Iterable, Tuple

from retireplan.policy import rmd_factor
from retireplan.social_security import ss_for_year
from retireplan.spending import spend_target
from retireplan.taxes import compute_tax_magi
from retireplan.timeline import make_years


def _infl_factor(rate: float, idx: int) -> float:
    return (1.0 + rate) ** idx


def _withdraw_local(b: float, r: float, i: float, need: float, order: Tuple[str, str, str]):
    """Pure, local withdraw in given order; returns draws and remaining balances."""
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
    # Events by year (amount >0 = extra spend; <0 = inflow). Tax treatment later.
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
            cfg.magi_target_base * infl if (yc.you_alive and yc.age_you < cfg.aca_end_age) else 0.0
        )
        filing_this_year = (
            "MFJ" if (cfg.filing_status == "MFJ" and yc.living == "Joint") else "Single"
        )

        # Spend target (inflation + survivor adjustment)
        spend = spend_target(
            phase=yc.phase,
            year_index=idx,
            infl=cfg.inflation,
            gogo=cfg.gogo_annual,
            slow=cfg.slow_annual,
            nogo=cfg.nogo_annual,
            survivor_pct=cfg.survivor_percent,
            living=yc.living,
        )

        # Social Security (only if alive)
        ss_you = (
            ss_for_year(
                yc.age_you, cfg.ss_you_start_age, cfg.ss_you_annual_at_start, idx, cfg.inflation
            )
            if yc.you_alive
            else 0.0
        )
        ss_sp = (
            ss_for_year(
                yc.age_spouse,
                cfg.ss_spouse_start_age,
                cfg.ss_spouse_annual_at_start,
                idx,
                cfg.inflation,
            )
            if (cfg.birth_year_spouse and yc.spouse_alive)
            else 0.0
        )
        ss_inc = ss_you + ss_sp

        # Events (cash only in v2)
        ev_amt = 0.0
        for e in ev_by_year.get(yc.year, []):
            ev_amt += float(e.get("amount", 0.0))

        # RMD if owner alive and at/over start age, based on IRA start-of-year
        rmd = 0.0
        if yc.you_alive and yc.age_you >= cfg.rmd_start_age and i_end > 0.0:
            rmd = i_end / rmd_factor(yc.age_you)

        # Solver for conversions to hit MAGI target (until ACA age). Conversions cannot include RMD.
        conv = 0.0

        def simulate(c: float):
            # Start-of-year balances
            b0, r0, i0 = b_end, r_end, i_end

            # RMD reduces IRA balance; it also covers part of cash need up to its amount.
            need_pre_tax = max(0.0, (spend + ev_amt) - ss_inc - rmd)

            # Pass 1: without taxes
            d_b1, d_r1, d_i1, b1, r1, i1, _ = _withdraw_local(b0, r0, i0 - rmd, need_pre_tax, order)
            # Taxes/MAGI from ordinary income = RMD + IRA-draw + conversion
            tax1, _ss_tax1, _taxable1, magi1 = compute_tax_magi(
                ira_ordinary=(rmd + d_i1),
                roth_conversion=c,
                ss_total=ss_inc,
                std_deduction=std_ded,
                filing=filing_this_year,
            )

            # Pass 2: include taxes in cash need
            need_with_tax = max(0.0, (spend + ev_amt + tax1) - ss_inc - rmd)
            d_b2, d_r2, d_i2, b2, r2, i2, _ = _withdraw_local(
                b0, r0, i0 - rmd, need_with_tax, order
            )
            tax2, _ss_tax2, _taxable2, magi2 = compute_tax_magi(
                ira_ordinary=(rmd + d_i2),
                roth_conversion=c,
                ss_total=ss_inc,
                std_deduction=std_ded,
                filing=filing_this_year,
            )

            # RMD surplus if RMD alone exceeds total need
            total_need = max(0.0, (spend + ev_amt + tax2) - ss_inc)
            rmd_surplus = max(0.0, rmd - total_need)

            # Apply conversion (IRA -> Roth). RMD itself cannot be converted.
            c_cap = max(0.0, i2)  # remaining IRA after cash draws
            c_eff = min(c, c_cap)
            i2 -= c_eff
            r2 += c_eff

            # Sweep any RMD surplus to Brokerage (cannot be converted by law)
            b2 += rmd_surplus

            # Year-end growth
            b_out = b2 * (1.0 + cfg.brokerage_growth)
            r_out = r2 * (1.0 + cfg.roth_growth)
            i_out = i2 * (1.0 + cfg.ira_growth)

            # Shortfall calculation
            provided = ss_inc + rmd + d_b2 + d_r2 + d_i2
            shortfall = max(0.0, (spend + ev_amt + tax2) - provided)

            return {
                "d_b": d_b2,
                "d_r": d_r2,
                "d_i": d_i2,
                "tax": tax2,
                "magi": magi2,
                "shortfall": shortfall,
                "b_out": b_out,
                "r_out": r_out,
                "i_out": i_out,
                "c_eff": c_eff,
                "rmd_surplus": rmd_surplus,
                "i_cap_after_draws": c_cap,
            }

        # Fill conversions up to MAGI target with a few fixed-point steps
        for _ in range(8):
            res = simulate(conv)
            if target_magi <= 0.0 or not yc.you_alive or yc.age_you >= cfg.aca_end_age:
                break
            gap = target_magi - res["magi"]
            if gap <= 1.0 or res["i_cap_after_draws"] <= 1.0:
                break
            conv += min(gap, res["i_cap_after_draws"])

        # Final run with settled conversion
        res = simulate(conv)

        # Commit end-of-year balances for next loop
        b_end, r_end, i_end = res["b_out"], res["r_out"], res["i_out"]

        rows.append(
            {
                "Year": yc.year,
                "Age_You": yc.age_you,
                "Age_Spouse": yc.age_spouse,
                "Phase": yc.phase,
                "Living": yc.living,
                "Spend_Target": round(spend),
                "Taxes": round(res["tax"]),
                "Events_Cash": round(ev_amt),
                "Total_Spend": round(spend + ev_amt + res["tax"]),
                "SS_Income": round(ss_inc),
                "Draw_Brokerage": round(res["d_b"]),
                "Draw_Roth": round(res["d_r"]),
                "Draw_IRA": round(res["d_i"]),  # excludes RMD
                "Roth_Conversion": round(res["c_eff"]),
                "RMD": round(rmd),
                "MAGI": round(res["magi"]),
                "Std_Deduction": round(std_ded),
                "End_Bal_Brokerage": round(b_end),
                "End_Bal_Roth": round(r_end),
                "End_Bal_IRA": round(i_end),
                "Total_Assets": round(b_end + r_end + i_end),
                "Shortfall": round(res["shortfall"]),
            }
        )

    return rows
