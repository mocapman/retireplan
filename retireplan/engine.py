from __future__ import annotations

from typing import Iterable

from retireplan.accounts import Accounts
from retireplan.social_security import ss_for_year
from retireplan.spending import spend_target
from retireplan.taxes import compute_tax_magi
from retireplan.timeline import make_years


def run_plan(cfg, events: Iterable[dict] | None = None) -> list[dict]:
    # Events by year (amount >0 = extra spend; <0 = inflow). Tax treatment deferred for v1.
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

    accts = Accounts(
        brokerage=cfg.balances_brokerage,
        roth=cfg.balances_roth,
        ira=cfg.balances_ira,
        gr_brokerage=cfg.brokerage_growth,
        gr_roth=cfg.roth_growth,
        gr_ira=cfg.ira_growth,
    )

    order = (
        ("IRA", "Brokerage", "Roth")
        if cfg.draw_order == "IRA, Brokerage, Roth"
        else ("Brokerage", "Roth", "IRA")
    )

    rows: list[dict] = []
    for idx, yc in enumerate(years):
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

        # Social Security gated by alive flags
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

        # Events (cash impact only in v1)
        ev_amt = 0.0
        for e in ev_by_year.get(yc.year, []):
            ev_amt += float(e.get("amount", 0.0))

        # Two-pass loop to include taxes in cash need
        roth_conv = 0.0  # v1 keeps conversions at 0; will add policy later
        std_ded = cfg.standard_deduction_base
        filing_this_year = (
            "MFJ" if (cfg.filing_status == "MFJ" and yc.living == "Joint") else "Single"
        )

        # Pass 1: no taxes
        need1 = max(0.0, spend + ev_amt - ss_inc)
        d_b1, d_r1, d_i1 = accts.withdraw_sequence(need1, order)
        tax1, ss_tax1, taxable_income1, magi1 = compute_tax_magi(
            d_i1, roth_conv, ss_inc, std_ded, filing_this_year
        )

        # Pass 2: include taxes in need
        need2 = max(0.0, spend + ev_amt + tax1 - ss_inc)
        # Rewind the Pass 1 draws from balances before re-drawing
        accts.brokerage += d_b1
        accts.roth += d_r1
        accts.ira += d_i1
        d_b2, d_r2, d_i2 = accts.withdraw_sequence(need2, order)
        tax2, ss_tax2, taxable_income2, magi2 = compute_tax_magi(
            d_i2, roth_conv, ss_inc, std_ded, filing_this_year
        )

        # Shortfall if accounts cannot cover remaining need
        provided2 = ss_inc + d_b2 + d_r2 + d_i2
        shortfall = max(0.0, (spend + ev_amt + tax2) - provided2)

        # Year-end growth
        accts.apply_growth()

        rows.append(
            {
                "Year": yc.year,
                "Age_You": yc.age_you,
                "Age_Spouse": yc.age_spouse,
                "Phase": yc.phase,
                "Living": yc.living,
                "Spend_Target": round(spend),
                "Taxes": round(tax2),
                "Events_Cash": round(ev_amt),
                "Total_Spend": round(spend + ev_amt + tax2),
                "SS_Income": round(ss_inc),
                "Draw_Brokerage": round(d_b2),
                "Draw_Roth": round(d_r2),
                "Draw_IRA": round(d_i2),
                "Roth_Conversion": round(roth_conv),
                "RMD": 0,
                "MAGI": round(magi2),
                "Std_Deduction": round(std_ded),
                "End_Bal_Brokerage": round(accts.brokerage),
                "End_Bal_Roth": round(accts.roth),
                "End_Bal_IRA": round(accts.ira),
                "Total_Assets": round(accts.brokerage + accts.roth + accts.ira),
                "Shortfall": round(shortfall),
            }
        )

    return rows
