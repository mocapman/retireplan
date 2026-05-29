#!/usr/bin/env python3
"""
Core retirement planning calculation engine.

This module contains the main `run_plan()` function that orchestrates the year-by-year
retirement planning calculations. It handles timeline generation, spending calculations,
tax computations, account withdrawals, and RMD requirements.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations

from typing import Iterable
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 10  # 10 decimal places of precision

from retireplan.engine.policy import rmd_factor
from retireplan.engine.social_security import ss_for_year
from retireplan.engine.spending import spend_target, infl_factor_decimal
from retireplan.engine.taxes import compute_tax_magi
from retireplan.engine.timeline import make_years
from retireplan.engine.precision import round_dollar, round_percent, round_year
from retireplan.engine.accounts import (
    calculate_brokerage_sale_tax_character,
    withdraw_with_order,
    parse_draw_order,
)


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
        events: Reserved for a future model. Ignored for now.

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
        - Roth conversions target configured MAGI guardrails
        - Account withdrawals follow configured draw order
        - Surplus RMD (beyond spending need) goes to brokerage account
    """
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
    brokerage_cash_end = Decimal(str(cfg.brokerage_cash))
    brokerage_cost_basis_end = Decimal(str(cfg.brokerage_cost_basis))
    brokerage_unrealized_gain_end = Decimal(str(cfg.brokerage_unrealized_gain))

    # Parse the draw order for account withdrawal sequencing
    order = parse_draw_order(cfg.draw_order)

    rows: list[dict] = []

    for idx, yc in enumerate(years):
        ira_balance_start_of_year = ira_end
        living_person = _living_person(yc)
        survivor_year = _is_survivor_year(yc)
        # BUSINESS RULE: Year 1 special handling
        # Year 1 uses user-provided values instead of calculated values
        # This allows users to set known actuals for the current year
        if idx == 0:
            # Use user-provided values for Year 1
            year1_lifestyle_spend = Decimal(str(cfg.year1_spend))
            ss_income = Decimal(0)  # Not in config, or set if you wish
            tax = Decimal(0)  # Not in config, or set if you wish
            roth_conv = Decimal(str(cfg.year1_roth_conversion))
            magi = (
                Decimal(str(cfg.year1_magi_income))
                - Decimal(str(cfg.year1_magi_losses))
                + roth_conv
            )
            target_magi = Decimal(str(cfg.magi_target_base))
            magi_floor = Decimal(str(cfg.magi_floor_base))
            magi_ceiling = _active_magi_ceiling(yc, cfg, Decimal(1))
            magi_remaining = target_magi - magi
            magi_remaining_to_ceiling = magi_ceiling - magi
            magi_status = _magi_status(
                magi,
                magi_floor,
                magi_ceiling,
            )

            # Apply user-specified draws for Year 1
            draw_ira = Decimal(str(cfg.year1_ira_draw))
            draw_broke = Decimal(str(cfg.year1_brokerage_draw))
            draw_roth = Decimal(str(cfg.year1_roth_draw))

            # Apply Roth conversion (IRA -> Roth transfer)
            ira_end -= roth_conv
            roth_end += roth_conv

            # Apply draws to accounts
            ira_end -= draw_ira
            brokerage_end -= draw_broke
            roth_end -= draw_roth
            brokerage_sale = calculate_brokerage_sale_tax_character(
                draw_broke,
                brokerage_cash_end,
                brokerage_cost_basis_end,
                brokerage_unrealized_gain_end,
            )
            brokerage_cash_end -= brokerage_sale.cash_used
            brokerage_cost_basis_end -= brokerage_sale.basis_used
            brokerage_unrealized_gain_end -= brokerage_sale.capital_gain

            # Apply growth at end of year
            brokerage_pre_growth = brokerage_end
            brokerage_end *= Decimal(1) + Decimal(str(cfg.brokerage_growth))
            roth_end *= Decimal(1) + Decimal(str(cfg.roth_growth))
            ira_end *= Decimal(1) + Decimal(str(cfg.ira_growth))
            brokerage_unrealized_gain_end += brokerage_end - brokerage_pre_growth

            # Calculate final spending values for output
            # Target_Spend: Actual lifestyle spending for Year 1
            target_spend = year1_lifestyle_spend  
            # Total_Spend: For Year 1, show the gross lifestyle spending (same as target)
            total_spend = year1_lifestyle_spend

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
                "Target_Spend": round_dollar(target_spend),
                "Social_Security": round_dollar(ss_income),
                "IRA_Draw": round_dollar(draw_ira),
                "Brokerage_Draw": round_dollar(draw_broke),
                "Roth_Draw": round_dollar(draw_roth),
                "Roth_Conversion": round_dollar(roth_conv),
                "RMD": round_dollar(0),
                "Federal_Tax": round_dollar(0),
                "Filing_Status_Used": (
                    "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"
                ),
                "Federal_Standard_Deduction_Used": round_dollar(0),
                "Federal_Tax_Bracket_Set_Used": (
                    "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"
                ),
                "Federal_Taxable_Income_Before_Deduction": round_dollar(
                    roth_conv + brokerage_sale.capital_gain
                ),
                "Federal_Taxable_Income_After_Deduction": round_dollar(0),
                "Estimated_State_Taxable_Income": round_dollar(0),
                "Estimated_State_Tax": round_dollar(0),
                "Brokerage_Cash_Used": round_dollar(brokerage_sale.cash_used),
                "Brokerage_Holdings_Sold": round_dollar(
                    brokerage_sale.holdings_sold
                ),
                "Brokerage_Basis_Used": round_dollar(brokerage_sale.basis_used),
                "Brokerage_Gain_Ratio": round_percent(brokerage_sale.gain_ratio),
                "Brokerage_Capital_Gains": round_dollar(
                    brokerage_sale.capital_gain
                ),
                "MAGI": round_dollar(magi),
                "MAGI_Floor": round_dollar(magi_floor),
                "Target_MAGI": round_dollar(target_magi),
                "MAGI_Ceiling": round_dollar(magi_ceiling),
                "MAGI_Remaining": round_dollar(magi_remaining),
                "MAGI_Remaining_To_Ceiling": round_dollar(
                    magi_remaining_to_ceiling
                ),
                "MAGI_Status": magi_status,
                "Survivor_Year": survivor_year,
                "Living_Person": living_person,
                "Widow_Tax_Mode": "Single survivor" if survivor_year else "",
                "Survivor_Spending_Used": round_dollar(
                    total_spend if survivor_year else 0
                ),
                "Survivor_Filing_Status_Used": (
                    "Single" if survivor_year else ""
                ),
                "Survivor_Standard_Deduction_Used": round_dollar(0),
                "IRA_Balance_Start_Of_Year": round_dollar(
                    ira_balance_start_of_year
                ),
                "IRA_Taxable_Income": round_dollar(0),
                "IRA_RMD_Taxable_Income": round_dollar(0),
                "IRA_Extra_Draw_Taxable_Income": round_dollar(0),
                "IRA_Balance_End_Of_Year": round_dollar(ira_end),
                "RMD_Gross": round_dollar(0),
                "RMD_Used_For_Spending": round_dollar(0),
                "RMD_Surplus_To_Brokerage": round_dollar(0),
                "Roth_Conversion_Taxable_Income": round_dollar(roth_conv),
                "SS_Person1_Gross": round_dollar(0),
                "SS_Person2_Gross": round_dollar(0),
                "SS_Total_Gross": round_dollar(0),
                "SS_Taxable_Amount": round_dollar(0),
                "SS_Nontaxable_Amount": round_dollar(0),
                "SS_Survivor_Adjustment": round_dollar(0),
                "SS_Filing_Status_Used": (
                    "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"
                ),
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

        # BUSINESS RULE: Filing status determination
        # Both alive = Married Filing Jointly, otherwise Single
        filing_status = "MFJ" if (yc.person1_alive and yc.person2_alive) else "Single"

        base_ded = Decimal(str(cfg.standard_deduction_base))
        if filing_status == "Single":
            base_ded = base_ded / 2
        std_ded = base_ded * infl

        # BUSINESS RULE: Roth conversion MAGI targeting
        # ACA ceiling applies before Medicare age; Medicare ceiling applies after.
        (
            planning_magi_income,
            planning_magi_loss,
            requested_roth_conversion,
        ) = _annual_roth_planning_inputs(yc, cfg)
        planning_magi_net_income = planning_magi_income - planning_magi_loss
        target_magi = Decimal(str(cfg.magi_target_base)) * infl
        magi_floor = Decimal(str(cfg.magi_floor_base)) * infl
        magi_ceiling = _active_magi_ceiling(yc, cfg, infl)
        conversion_target_magi = min(target_magi, magi_ceiling)

        # Calculate inflation-adjusted lifestyle spending target based on lifecycle phase
        # This represents the core lifestyle spending goal (Target_Spend)
        target_spend_lifestyle = Decimal(
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
            ss_person1_gross = ss_person1
            ss_person2_gross = ss_person2
        elif yc.person1_alive and not yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
            ss_person1_gross = ss_income
            ss_person2_gross = Decimal(0)
        elif (not yc.person1_alive) and yc.person2_alive:
            ss_income = max(ss_person1, ss_person2)
            ss_person1_gross = Decimal(0)
            ss_person2_gross = ss_income
        else:
            ss_income = Decimal(0)
            ss_person1_gross = Decimal(0)
            ss_person2_gross = Decimal(0)
        ss_survivor_adjustment = ss_income - ss_person1_gross - ss_person2_gross

        # BUSINESS RULE: Required Minimum Distribution (RMD) calculation
        # RMD required when a living person is at/above RMD start age.
        # Uses IRS Uniform Lifetime Table factors.
        rmd = Decimal(0)
        rmd_age = _rmd_age_for_year(yc)
        if (
            rmd_age is not None
            and rmd_age >= cfg.rmd_start_age
            and ira_end > Decimal(0)
        ):
            rmd = ira_end / Decimal(str(rmd_factor(rmd_age)))

        estimated_tax = Decimal(0)
        tax = Decimal(0)
        federal_tax = Decimal(0)
        taxable_income = Decimal(0)
        estimated_state_taxable_income = Decimal(0)
        estimated_state_tax = Decimal(0)
        ss_taxable = Decimal(0)
        magi = Decimal(0)
        roth_conv = Decimal(0)
        brokerage_capital_gains = Decimal(0)
        brokerage_sale = calculate_brokerage_sale_tax_character(
            Decimal(0),
            brokerage_cash_end,
            brokerage_cost_basis_end,
            brokerage_unrealized_gain_end,
        )
        draw_broke = draw_roth = draw_ira = Decimal(0)
        b1, r1, i1 = brokerage_end, roth_end, ira_end - rmd
        unmet = Decimal(0)
        tax_stable = False

        # BUSINESS RULE: Taxes are part of the annual cash need.
        # Because taxes depend on draws, solve by bounded iteration from the same
        # pre-draw balances each pass and commit only the final pass.
        for _ in range(8):
            annual_need = target_spend_lifestyle + estimated_tax
            need_for_budget = max(Decimal(0), annual_need - ss_income - rmd)

            # Note: RMD amount is excluded from normal draw-order withdrawals.
            (
                iter_draw_broke,
                iter_draw_roth,
                iter_draw_ira,
                iter_b1,
                iter_r1,
                iter_i1,
                iter_unmet,
            ) = withdraw_with_order(
                brokerage_end, roth_end, ira_end - rmd, need_for_budget, order
            )
            iter_brokerage_sale = calculate_brokerage_sale_tax_character(
                iter_draw_broke,
                brokerage_cash_end,
                brokerage_cost_basis_end,
                brokerage_unrealized_gain_end,
            )
            iter_brokerage_capital_gains = iter_brokerage_sale.capital_gain

            def tax_and_magi(
                conv: Decimal,
            ) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
                """Calculate total tax, tax components, and MAGI for a conversion."""
                (
                    federal_tax_value,
                    ss_tax_value,
                    taxable_income_value,
                    magi_value,
                ) = compute_tax_magi(
                    ira_ordinary=float(rmd + iter_draw_ira),
                    roth_conversion=float(conv),
                    ss_total=float(ss_income),
                    std_deduction=float(std_ded),
                    filing=filing_status,
                    brokerage_capital_gains=float(iter_brokerage_capital_gains),
                    other_magi_income=float(planning_magi_net_income),
                )
                federal_tax_decimal = Decimal(str(federal_tax_value))
                ss_tax_decimal = Decimal(str(ss_tax_value))
                taxable_income_decimal = Decimal(str(taxable_income_value))
                state_taxable_income, state_tax = _estimated_state_tax(
                    taxable_income_decimal,
                    Decimal(str(cfg.estimated_state_deduction)),
                    Decimal(str(cfg.estimated_state_tax_rate)),
                )
                total_tax = Decimal(round_dollar(federal_tax_decimal)) + Decimal(
                    round_dollar(state_tax)
                )
                return (
                    total_tax,
                    federal_tax_decimal,
                    ss_tax_decimal,
                    taxable_income_decimal,
                    state_taxable_income,
                    Decimal(str(magi_value)),
                )

            _tax0, _fed0, _ss0, _taxable0, _state_taxable0, magi0 = tax_and_magi(
                Decimal(0)
            )
            conversion_room = max(Decimal(0), conversion_target_magi - magi0)
            conv = min(
                max(Decimal(0), requested_roth_conversion),
                conversion_room,
                max(Decimal(0), iter_i1),
            )

            iter_roth_conv = min(conv, max(Decimal(0), iter_i1))
            (
                iter_tax,
                iter_federal_tax,
                iter_ss_taxable,
                iter_taxable_income,
                iter_estimated_state_taxable_income,
                iter_magi,
            ) = tax_and_magi(iter_roth_conv)
            iter_estimated_state_tax = iter_tax - iter_federal_tax

            draw_broke = iter_draw_broke
            draw_roth = iter_draw_roth
            draw_ira = iter_draw_ira
            b1 = iter_b1
            r1 = iter_r1 + iter_roth_conv
            i1 = iter_i1 - iter_roth_conv
            unmet = iter_unmet
            brokerage_sale = iter_brokerage_sale
            brokerage_capital_gains = iter_brokerage_capital_gains
            roth_conv = iter_roth_conv
            tax = iter_tax
            federal_tax = iter_federal_tax
            ss_taxable = iter_ss_taxable
            taxable_income = iter_taxable_income
            estimated_state_taxable_income = iter_estimated_state_taxable_income
            estimated_state_tax = iter_estimated_state_tax
            magi = iter_magi

            if abs(tax - estimated_tax) <= Decimal("1.0") and tax_stable:
                break
            tax_stable = abs(tax - estimated_tax) <= Decimal("1.0")
            estimated_tax = tax

        # BUSINESS RULE: Surplus RMD handling
        # If RMD exceeds annual cash need (after SS), put surplus in brokerage
        # This ensures required distributions are taken but excess goes to taxable account
        total_spend = target_spend_lifestyle + tax
        need_after_ss = max(Decimal(0), total_spend - ss_income)
        rmd_surplus = max(Decimal(0), rmd - need_after_ss)
        rmd_used_for_spending = rmd - rmd_surplus
        b1 += rmd_surplus
        brokerage_cash_end = (
            brokerage_cash_end - brokerage_sale.cash_used + rmd_surplus
        )
        brokerage_cost_basis_end -= brokerage_sale.basis_used
        brokerage_unrealized_gain_end -= brokerage_sale.capital_gain

        # Apply end-of-year growth to all accounts
        broke_bal = b1 * (Decimal(1) + Decimal(str(cfg.brokerage_growth)))
        roth_bal = r1 * (Decimal(1) + Decimal(str(cfg.roth_growth)))
        ira_bal = i1 * (Decimal(1) + Decimal(str(cfg.ira_growth)))
        brokerage_unrealized_gain_end += broke_bal - b1

        # Update running balances for next year
        brokerage_end, roth_end, ira_end = broke_bal, roth_bal, ira_bal

        # Calculate final spending values for output
        # Target_Spend: Core lifestyle spending goal (inflation-adjusted)
        target_spend = target_spend_lifestyle
        provided_cash = ss_income + rmd + draw_broke + draw_roth + draw_ira
        shortfall = _clean_shortfall(total_spend - provided_cash)
        ira_taxable_income = rmd + draw_ira
        ordinary_income_taxable = max(
            Decimal(0), ira_taxable_income + roth_conv + planning_magi_net_income
        )
        total_taxable_income_before_deduction = (
            ordinary_income_taxable + brokerage_capital_gains + ss_taxable
        )

        row_data = {
            "Year": round_year(yc.year),
            "Person1_Age": round_year(yc.age_person1),
            "Person2_Age": round_year(yc.age_person2),
            "Lifestyle": yc.phase,
            "Filing": filing_status,
            "Total_Spend": round_dollar(total_spend),
            "Taxes_Due": round_dollar(tax),
            "Target_Spend": round_dollar(target_spend),
            "Social_Security": round_dollar(ss_income),
            "IRA_Draw": round_dollar(draw_ira),
            "Brokerage_Draw": round_dollar(draw_broke),
            "Roth_Draw": round_dollar(draw_roth),
            "Roth_Conversion": round_dollar(roth_conv),
            "RMD": round_dollar(rmd),
            "Federal_Tax": round_dollar(federal_tax),
            "Filing_Status_Used": filing_status,
            "Federal_Standard_Deduction_Used": round_dollar(std_ded),
            "Federal_Tax_Bracket_Set_Used": filing_status,
            "Federal_Taxable_Income_Before_Deduction": round_dollar(
                total_taxable_income_before_deduction
            ),
            "Federal_Taxable_Income_After_Deduction": round_dollar(taxable_income),
            "Estimated_State_Taxable_Income": round_dollar(
                estimated_state_taxable_income
            ),
            "Estimated_State_Tax": round_dollar(estimated_state_tax),
            "Brokerage_Cash_Used": round_dollar(brokerage_sale.cash_used),
            "Brokerage_Holdings_Sold": round_dollar(brokerage_sale.holdings_sold),
            "Brokerage_Basis_Used": round_dollar(brokerage_sale.basis_used),
            "Brokerage_Gain_Ratio": round_percent(brokerage_sale.gain_ratio),
            "Brokerage_Capital_Gains": round_dollar(brokerage_capital_gains),
            "MAGI": round_dollar(magi),
            "MAGI_Floor": round_dollar(magi_floor),
            "Target_MAGI": round_dollar(target_magi),
            "MAGI_Ceiling": round_dollar(magi_ceiling),
            "MAGI_Remaining": round_dollar(
                target_magi - magi if target_magi > Decimal(0) else Decimal(0)
            ),
            "MAGI_Remaining_To_Ceiling": round_dollar(
                magi_ceiling - magi if magi_ceiling > Decimal(0) else Decimal(0)
            ),
            "MAGI_Status": _magi_status(magi, magi_floor, magi_ceiling),
            "Survivor_Year": survivor_year,
            "Living_Person": living_person,
            "Widow_Tax_Mode": "Single survivor" if survivor_year else "",
            "Survivor_Spending_Used": round_dollar(
                target_spend_lifestyle if survivor_year else 0
            ),
            "Survivor_Filing_Status_Used": "Single" if survivor_year else "",
            "Survivor_Standard_Deduction_Used": round_dollar(
                std_ded if survivor_year else 0
            ),
            "IRA_Balance_Start_Of_Year": round_dollar(ira_balance_start_of_year),
            "IRA_Taxable_Income": round_dollar(ira_taxable_income),
            "IRA_RMD_Taxable_Income": round_dollar(rmd),
            "IRA_Extra_Draw_Taxable_Income": round_dollar(draw_ira),
            "IRA_Balance_End_Of_Year": round_dollar(ira_bal),
            "RMD_Gross": round_dollar(rmd),
            "RMD_Used_For_Spending": round_dollar(rmd_used_for_spending),
            "RMD_Surplus_To_Brokerage": round_dollar(rmd_surplus),
            "Roth_Conversion_Taxable_Income": round_dollar(roth_conv),
            "SS_Person1_Gross": round_dollar(ss_person1_gross),
            "SS_Person2_Gross": round_dollar(ss_person2_gross),
            "SS_Total_Gross": round_dollar(ss_income),
            "SS_Taxable_Amount": round_dollar(ss_taxable),
            "SS_Nontaxable_Amount": round_dollar(ss_income - ss_taxable),
            "SS_Survivor_Adjustment": round_dollar(ss_survivor_adjustment),
            "SS_Filing_Status_Used": filing_status,
            "IRA_Balance": round_dollar(ira_bal),
            "Brokerage_Balance": round_dollar(broke_bal),
            "Roth_Balance": round_dollar(roth_bal),
            "Total_Assets": round_dollar(broke_bal + roth_bal + ira_bal),
            "Shortfall": round_dollar(shortfall),
        }

        rows.append(row_data)

    return rows


def _magi_status(magi: Decimal, floor: Decimal, ceiling: Decimal) -> str:
    """Classify current-year MAGI against configured MAGI guardrails."""
    if magi > ceiling:
        return "FAIL"
    if magi < floor:
        return "Low"
    if ceiling - magi < Decimal("2000"):
        return "Warning"
    return "Good"


def _active_magi_ceiling(yc, cfg, infl: Decimal) -> Decimal:
    """Select the ACA or Medicare MAGI ceiling for this projection year."""
    base = (
        cfg.magi_ceiling_base
        if yc.age_person1 < cfg.aca_end_age
        else cfg.medicare_magi_ceiling_base
    )
    return Decimal(str(base)) * infl


def _annual_roth_planning_inputs(yc, cfg) -> tuple[Decimal, Decimal, Decimal]:
    """Return annual Roth Planning assumptions for ACA or Medicare years."""
    if yc.age_person1 < cfg.aca_end_age:
        return (
            Decimal(str(cfg.aca_annual_magi_income)),
            Decimal(str(cfg.aca_annual_magi_loss)),
            Decimal(str(cfg.aca_annual_roth_conversion)),
        )
    return (
        Decimal(str(cfg.medicare_annual_magi_income)),
        Decimal(str(cfg.medicare_annual_magi_loss)),
        Decimal(str(cfg.medicare_annual_roth_conversion)),
    )


def _clean_shortfall(shortfall: Decimal) -> Decimal:
    """Treat dollar-rounding residuals as zero while preserving real shortfalls."""
    shortfall = max(Decimal(0), shortfall)
    if shortfall <= Decimal("1.0"):
        return Decimal(0)
    return shortfall


def _estimated_state_tax(
    taxable_income: Decimal,
    estimated_state_deduction: Decimal,
    estimated_state_tax_rate: Decimal,
) -> tuple[Decimal, Decimal]:
    """Apply the simplified state-tax assumption to federal taxable income."""
    state_taxable_income = max(Decimal(0), taxable_income - estimated_state_deduction)
    return state_taxable_income, state_taxable_income * max(
        Decimal(0), estimated_state_tax_rate
    )


def _rmd_age_for_year(yc) -> int | None:
    """Select the RMD age from the living person for this projection year."""
    if yc.person1_alive:
        return yc.age_person1
    if yc.person2_alive:
        return yc.age_person2
    return None


def _is_survivor_year(yc) -> bool:
    """Return True when exactly one person is alive in the projection year."""
    return bool(yc.person1_alive) != bool(yc.person2_alive)


def _living_person(yc) -> str:
    """Return a compact survivor-audit label for who is alive."""
    if yc.person1_alive and yc.person2_alive:
        return "Both"
    if yc.person1_alive:
        return "Person1"
    if yc.person2_alive:
        return "Person2"
    return "None"
