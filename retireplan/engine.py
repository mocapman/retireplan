#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/engine.py

Core retirement planning calculation engine.

This module contains the main `run_plan()` function that orchestrates the year-by-year
retirement planning calculations. It handles timeline generation, spending calculations,
tax computations, account withdrawals, and RMD requirements.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations

from typing import Iterable, Tuple
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 10  # 10 decimal places of precision

from retireplan.policy import rmd_factor
from retireplan.social_security import ss_for_year
from retireplan.spending import spend_target, infl_factor_decimal
from retireplan.taxes import compute_tax_magi
from retireplan.timeline import make_years
from retireplan.precision import round_dollar, round_percent, round_year
from retireplan.accounts import withdraw_with_order, parse_draw_order


# Remove duplicate inflation function - use infl_factor_decimal from spending.py
# TODO: Further consolidate inflation utilities once Decimal adoption is complete
#
# MODULARIZATION DECISION: Consolidated inflation calculations in spending.py
# RATIONALE: The spending.py module already had an identical inflation function.
#            Having two functions doing the same calculation creates maintenance issues.
# FUTURE: Consider standardizing on either float or Decimal throughout the codebase
#         to allow complete consolidation of these functions.


# Remove duplicate functions - now using centralized versions from accounts.py
# TODO: Further consolidate account management once refactoring is complete
#
# MODULARIZATION DECISION: Moved withdrawal and draw order logic to accounts.py
# RATIONALE: The accounts.py module is the natural place for account-related operations.
#            The engine was duplicating withdrawal logic that already existed there.
# FUTURE: Consider using the Accounts class directly instead of separate functions
#         once Decimal precision is standardized throughout the codebase.


def run_plan(cfg, events: Iterable[dict] | None = None) -> list[dict]:
    """
    Execute year-by-year retirement planning calculations.
    
    This is the main engine function that orchestrates all retirement planning
    calculations for each year from start to end of plan. It handles spending
    targets, tax calculations, account withdrawals, RMD requirements, Roth
    conversions, and survivor benefit adjustments.
    
    Args:
        cfg: Configuration object containing all plan parameters including:
            - Account balances and growth rates
            - Spending targets and lifestyle phases
            - Tax and Social Security parameters
            - Timeline parameters (birth years, final ages)
        events: Optional list of cash events by year with structure:
            [{"year": int, "amount": float}, ...] where positive amounts
            are extra spending, negative amounts are cash inflows
            
    Returns:
        List of dictionaries, one per year, containing:
            - Year and age information
            - Spending and tax calculations  
            - Account balances and draws
            - RMD and Roth conversion amounts
            - Social Security benefits
            - Filing status and lifecycle phase
            
    Business Rules:
        - Year 1 uses user-provided values for most calculations
        - Subsequent years use calculated values based on configuration
        - Survivor benefits: When one person dies, take higher SS benefit
        - RMD starts at configured age using IRS Uniform Lifetime Table
        - Roth conversions target MAGI limits for ACA premium subsidies
        - Account withdrawals follow configured draw order
        - Surplus RMD (beyond spending need) goes to brokerage account
    """
    # Events by year (amount >0 = extra spend; <0 = inflow). Cash-only.
    ev_by_year: dict[int, list[dict]] = {}
    for e in events or []:
        ev_by_year.setdefault(int(e["year"]), []).append(e)

    # Generate complete timeline with ages, phases, and survival status
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

    # Parse the draw order for account withdrawal sequencing
    order = parse_draw_order(cfg.draw_order)

    rows: list[dict] = []

    for idx, yc in enumerate(years):
        # BUSINESS RULE: Year 1 special handling
        # Year 1 uses user-provided values instead of calculated values
        # This allows users to set known actuals for the current year
        if idx == 0:
            # Use user-provided values for Year 1
            total_spend = Decimal(str(cfg.year1_spend))
            ss_income = Decimal(0)  # Not in config, or set if you wish
            tax = Decimal(0)  # Not in config, or set if you wish
            roth_conv = Decimal(0)  # Not in config, or set if you wish

            # Apply user-specified draws for Year 1
            draw_ira = Decimal(str(cfg.year1_ira_draw))
            draw_broke = Decimal(str(cfg.year1_brokerage_draw))
            draw_roth = Decimal(str(cfg.year1_roth_draw))

            # Apply cash events (as one value)
            events_cash = Decimal(str(cfg.year1_cash_events))

            # Apply Roth conversion (IRA -> Roth transfer)
            ira_end -= roth_conv
            roth_end += roth_conv

            # Apply draws to accounts
            ira_end -= draw_ira
            brokerage_end -= draw_broke
            roth_end -= draw_roth

            # Apply growth at end of year
            brokerage_end *= Decimal(1) + Decimal(str(cfg.brokerage_growth))
            roth_end *= Decimal(1) + Decimal(str(cfg.roth_growth))
            ira_end *= Decimal(1) + Decimal(str(cfg.ira_growth))

            # Calculate target spend (spending after taxes and events)
            target_spend = max(Decimal(0), total_spend - tax - events_cash)

            # Create Year 1 row
            row_data = {
                "Year": round_year(yc.year),
                "Person1_Age": round_year(yc.age_person1),
                "Person2_Age": round_year(yc.age_person2),
                "Lifestyle": yc.phase,
                "Filing": (
                    "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"
                ),
                "Total_Spend": round_dollar(total_spend),
                "Taxes_Due": round_dollar(tax),
                "Cash_Events": round_dollar(events_cash),
                "Target_Spend": round_dollar(target_spend),
                "Social_Security": round_dollar(ss_income),
                "IRA_Draw": round_dollar(draw_ira),
                "Brokerage_Draw": round_dollar(draw_broke),
                "Roth_Draw": round_dollar(draw_roth),
                "Roth_Conversion": round_dollar(roth_conv),
                "RMD": round_dollar(0),
                "MAGI": round_dollar(0),  # Not calculated for Year 1
                "Std_Deduction": round_dollar(0),  # Not calculated for Year 1
                "IRA_Balance": round_dollar(ira_end),
                "Brokerage_Balance": round_dollar(brokerage_end),
                "Roth_Balance": round_dollar(roth_end),
                "Total_Assets": round_dollar(brokerage_end + roth_end + ira_end),
                "Shortfall": round_dollar(0),  # No shortfall calculation for Year 1
            }

            rows.append(row_data)
            continue

        # Normal processing for subsequent years (calculated values)
        infl = infl_factor_decimal(cfg.inflation, idx)
        std_ded = Decimal(str(cfg.standard_deduction_base)) * infl

        # BUSINESS RULE: Filing status determination
        # Both alive = Married Filing Jointly, otherwise Single
        filing_status = "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"

        # BUSINESS RULE: MAGI targeting for ACA premium subsidies  
        # Only target MAGI while person1 is under ACA end age (usually 65)
        target_magi = (
            Decimal(str(cfg.magi_target_base)) * infl
            if (yc.person1_alive and yc.age_person1 < cfg.aca_end_age)
            else Decimal(0)
        )

        # Calculate inflation-adjusted spending target based on lifecycle phase
        total_spend = Decimal(
            str(
                spend_target(
                    phase=yc.phase,
                    year_index=idx,
                    infl=cfg.inflation,
                    target_spend=cfg.target_spend,
                    gogo_percent=cfg.gogo_percent,
                    slow_percent=cfg.slow_percent,
                    nogo_percent=cfg.nogo_percent,
                    survivor_pct=cfg.survivor_percent,
                    person1_alive=yc.person1_alive,
                    person2_alive=yc.person2_alive,
                )
            )
        )

        # Calculate Social Security benefits with COLA adjustments
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
        
        # BUSINESS RULE: Survivor Social Security benefits
        # When both alive: sum of both benefits
        # When one alive: higher of the two benefits (survivor gets better benefit)
        # When neither alive: no benefits
        if yc.person1_alive and yc.person2_alive:
            ss_income = ss_person1 + ss_person2
        elif yc.person1_alive and not yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
        elif (not yc.person1_alive) and yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
        else:
            ss_income = Decimal(0)

        # Sum all cash events for this year
        events_cash = Decimal(0)
        for e in ev_by_year.get(yc.year, []):
            events_cash += Decimal(str(e.get("amount", 0)))

        # BUSINESS RULE: Required Minimum Distribution (RMD) calculation
        # RMD required when person1 is alive and at/above RMD start age (usually 73)
        # Uses IRS Uniform Lifetime Table factors
        rmd = Decimal(0)
        if (
            yc.person1_alive
            and yc.age_person1 >= cfg.rmd_start_age
            and ira_end > Decimal(0)
        ):
            rmd = ira_end / Decimal(str(rmd_factor(yc.age_person1)))

        # Calculate how much we need from accounts after SS and RMD
        need_for_budget = max(Decimal(0), total_spend - ss_income - rmd)

        # Withdraw from accounts in specified order to meet budget need
        # Note: RMD amount is excluded from IRA balance for withdrawal calculation
        draw_broke, draw_roth, draw_ira, b1, r1, i1, unmet = withdraw_with_order(
            brokerage_end, roth_end, ira_end - rmd, need_for_budget, order
        )

        # Calculate total cash provided and any shortfall
        provided_cash = ss_income + rmd + draw_broke + draw_roth + draw_ira
        shortfall = max(Decimal(0), total_spend - provided_cash)

        # BUSINESS RULE: Roth conversion targeting for MAGI limits
        # Iteratively adjust Roth conversion to hit MAGI target for ACA subsidies
        # Only applies when person1 is alive and under ACA end age
        def tax_and_magi(conv: Decimal) -> tuple[Decimal, Decimal]:
            """Calculate tax and MAGI for given Roth conversion amount."""
            tax, _ss_tax, _taxable, magi = compute_tax_magi(
                ira_ordinary=float(rmd + draw_ira + conv),
                roth_conversion=float(conv),
                ss_total=float(ss_income),
                std_deduction=float(std_ded),
                filing=filing_status,
            )
            return Decimal(str(tax)), Decimal(str(magi))

        conv = Decimal(0)
        # Iterative approach to hit MAGI target (limit iterations to prevent infinite loop)
        for _ in range(8):
            tax0, magi0 = tax_and_magi(conv)
            if (
                target_magi <= Decimal(0)
                or not yc.person1_alive
                or yc.age_person1 >= cfg.aca_end_age
            ):
                break
            gap = target_magi - magi0
            if gap <= Decimal("1.0"):  # Close enough to target
                break
            cap = max(Decimal(0), i1)  # Available IRA balance for conversion
            step = min(gap, cap - conv)  # Don't exceed available balance
            if step <= Decimal("1.0"):  # Minimal remaining step
                break
            conv += step

        # Apply final Roth conversion (limited by available IRA balance)
        roth_conv = min(conv, max(Decimal(0), i1))
        i1 -= roth_conv
        r1 += roth_conv

        # Calculate final tax and MAGI with chosen conversion amount
        tax, magi = tax_and_magi(roth_conv)

        # BUSINESS RULE: Surplus RMD handling
        # If RMD exceeds spending need (after SS), put surplus in brokerage
        # This ensures required distributions are taken but excess goes to taxable account
        need_after_ss = max(Decimal(0), total_spend - ss_income)
        rmd_surplus = max(Decimal(0), rmd - need_after_ss)
        b1 += rmd_surplus

        # Apply end-of-year growth to all accounts
        broke_bal = b1 * (Decimal(1) + Decimal(str(cfg.brokerage_growth)))
        roth_bal = r1 * (Decimal(1) + Decimal(str(cfg.roth_growth)))
        ira_bal = i1 * (Decimal(1) + Decimal(str(cfg.ira_growth)))

        # Update running balances for next year
        brokerage_end, roth_end, ira_end = broke_bal, roth_bal, ira_bal

        # Calculate target spend (spending after taxes and events)
        target_spend = max(Decimal(0), total_spend - tax - events_cash)

        row_data = {
            "Year": round_year(yc.year),
            "Person1_Age": round_year(yc.age_person1),
            "Person2_Age": round_year(yc.age_person2),
            "Lifestyle": yc.phase,
            "Filing": filing_status,
            "Total_Spend": round_dollar(total_spend),
            "Taxes_Due": round_dollar(tax),
            "Cash_Events": round_dollar(events_cash),
            "Target_Spend": round_dollar(target_spend),
            "Social_Security": round_dollar(ss_income),
            "IRA_Draw": round_dollar(draw_ira),
            "Brokerage_Draw": round_dollar(draw_broke),
            "Roth_Draw": round_dollar(draw_roth),
            "Roth_Conversion": round_dollar(roth_conv),
            "RMD": round_dollar(rmd),
            "MAGI": round_dollar(magi),
            "Std_Deduction": round_dollar(std_ded),
            "IRA_Balance": round_dollar(ira_bal),
            "Brokerage_Balance": round_dollar(broke_bal),
            "Roth_Balance": round_dollar(roth_bal),
            "Total_Assets": round_dollar(broke_bal + roth_bal + ira_bal),
            "Shortfall": round_dollar(shortfall),
        }

        rows.append(row_data)

    return rows
