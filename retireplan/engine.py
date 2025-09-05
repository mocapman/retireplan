from __future__ import annotations

from typing import Iterable

from retireplan.accounts import Accounts
from retireplan.social_security import ss_for_year
from retireplan.spending import spend_target
from retireplan.timeline import make_years


def run_plan(cfg, events: Iterable[dict] | None = None) -> list[dict]:
    # Events by year (amount >0 = extra spend; <0 = inflow). Tax treatment deferred for v0.
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

        # Events (cash impact only in v0)
        ev_amt = 0.0
        for e in ev_by_year.get(yc.year, []):
            ev_amt += float(e.get("amount", 0.0))

        # Taxes placeholder (v0)
        taxes = 0.0

        # Net cash need after SS, events, and taxes
        need = max(0.0, spend + taxes + ev_amt - ss_inc)

        # Draws in selected order
        d_b, d_r, d_i = accts.withdraw_sequence(need, order)

        # Shortfall if accounts cannot cover remaining need
        provided = ss_inc + d_b + d_r + d_i
        shortfall = max(0.0, (spend + taxes + ev_amt) - provided)

        # Placeholders to be implemented in v1
        roth_conv = 0.0
        rmd = 0.0
        magi = 0.0
        std_ded = cfg.standard_deduction_base

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
                "Taxes": round(taxes),
                "Events_Cash": round(ev_amt),
                "Total_Spend": round(spend + taxes + ev_amt),
                "SS_Income": round(ss_inc),
                "Draw_Brokerage": round(d_b),
                "Draw_Roth": round(d_r),
                "Draw_IRA": round(d_i),
                "Roth_Conversion": round(roth_conv),
                "RMD": round(rmd),
                "MAGI": round(magi),
                "Std_Deduction": round(std_ded),
                "End_Bal_Brokerage": round(accts.brokerage),
                "End_Bal_Roth": round(accts.roth),
                "End_Bal_IRA": round(accts.ira),
                "Total_Assets": round(accts.brokerage + accts.roth + accts.ira),
                "Shortfall": round(shortfall),
            }
        )

    return rows
