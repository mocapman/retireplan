#!/usr/bin/env python3
"""
Filename: spending.py
Path: retireplan/engine/spending.py

Retirement spending calculations with phase-based adjustments.

This module implements the Target Spend model described in SPENDING_MODEL.md. It calculates
annual spending targets based on lifecycle phases (GoGo/Slow/NoGo), applies compound 
inflation adjustments over time, and handles survivor benefit reductions when one person 
passes away. All internal calculations use Decimal precision with rounding only at output.

Key Functions and Output Mapping:
- calculate_base_target_spend() → Base target spend calculation
- apply_phase_percentage() → Phase-adjusted spending (GoGo/Slow/NoGo percentages)  
- apply_inflation_adjustment() → Inflation-adjusted spending amounts
- apply_survivor_adjustment() → Survivor-adjusted spending when one person dies
- calculate_spending_target() → Final Total_Spend column value

Business Logic:
- Target Spend: Base annual spending in today's dollars
- Phase Percentages: GoGo (100%), SlowGo (80%), NoGo (70%) of target by default
- Inflation: Compound annual inflation from start year
- Survivor: Reduced spending (70% by default) when one person passes away

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-12-19
"""
from __future__ import annotations
from decimal import Decimal


def calculate_base_target_spend(target_spend: float) -> Decimal:
    """
    Calculate base annual spending target in start year dollars.
    
    This is the foundation amount before any phase, inflation, or survivor adjustments.
    Represents the baseline annual spending goal in today's purchasing power.
    
    Args:
        target_spend: Base annual spending target in start year dollars
        
    Returns:
        Decimal: Base target spend amount with full precision
        
    Output Column Mapping:
        Used internally for Total_Spend calculation basis
        
    Business Rules:
        - This is the "Target Spend" from SPENDING_MODEL.md
        - All other spending calculations derive from this base amount
        - Converted to Decimal immediately to maintain precision through all calculations
    """
    return Decimal(str(target_spend))


def apply_phase_percentage(
    base_target: Decimal, 
    phase: str,
    gogo_percent: float,
    slow_percent: float, 
    nogo_percent: float
) -> Decimal:
    """
    Apply lifecycle phase percentage to base target spend.
    
    Adjusts spending based on activity level expected in each retirement phase.
    GoGo years typically have higher expenses (travel, activities), Slow years 
    have moderate reduction, and NoGo years have significant reduction but may
    include higher care costs.
    
    Args:
        base_target: Base annual target spend amount  
        phase: Lifecycle phase - "GoGo", "Slow", or "NoGo"
        gogo_percent: Percentage of base spending during GoGo phase (typically 100%)
        slow_percent: Percentage of base spending during Slow phase (typically 80%)
        nogo_percent: Percentage of base spending during NoGo phase (typically 70%)
        
    Returns:
        Decimal: Phase-adjusted spending amount
        
    Output Column Mapping:
        Contributes to Total_Spend calculation
        
    Business Rules:
        - GoGo: Active lifestyle with travel and activities (100% of target)
        - Slow: Reduced activity but independent living (80% of target)  
        - NoGo: Minimal activity, potential care needs (70% of target)
        - Percentages from SPENDING_MODEL.md configuration
    """
    if phase == "GoGo":
        phase_pct = Decimal(str(gogo_percent))
    elif phase == "Slow": 
        phase_pct = Decimal(str(slow_percent))
    else:  # NoGo
        phase_pct = Decimal(str(nogo_percent))
    
    return base_target * (phase_pct / Decimal('100'))


def apply_inflation_adjustment(amount: Decimal, inflation_rate: float, years_since_start: int) -> Decimal:
    """
    Apply compound inflation adjustment to spending amount.
    
    Adjusts spending amount for cumulative inflation since the start year to maintain
    purchasing power equivalency. Uses compound growth formula.
    
    Args:
        amount: Spending amount to adjust for inflation
        inflation_rate: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        years_since_start: Number of years since start (0 = no adjustment)
        
    Returns:
        Decimal: Inflation-adjusted amount maintaining purchasing power
        
    Output Column Mapping:
        Contributes to Total_Spend calculation
        
    Business Rules:
        - Uses compound inflation: amount * (1 + rate) ^ years
        - Year 0 has no inflation adjustment (factor = 1.0)
        - Maintains constant purchasing power relative to start year
        - Inflation rate typically 2-4% annually based on economic assumptions
    """
    if years_since_start == 0:
        return amount
    
    inflation_factor = (Decimal('1') + Decimal(str(inflation_rate))) ** years_since_start
    return amount * inflation_factor


def apply_survivor_adjustment(
    amount: Decimal,
    survivor_pct: float,
    person1_alive: bool,
    person2_alive: bool
) -> Decimal:
    """
    Apply survivor benefit adjustment when one person passes away.
    
    Adjusts spending downward when household transitions from two people to one,
    reflecting reduced expenses for housing, food, transportation, etc. Some fixed
    costs remain, so reduction is partial rather than 50%.
    
    Args:
        amount: Spending amount before survivor adjustment
        survivor_pct: Percentage of spending when only one person alive (typically 70%)
        person1_alive: Whether primary person is alive
        person2_alive: Whether secondary person is alive
        
    Returns:
        Decimal: Survivor-adjusted spending amount
        
    Output Column Mapping:
        Contributes to Total_Spend calculation
        
    Business Rules:
        - Both alive: no adjustment (100% of amount)
        - One alive: apply survivor percentage (typically 70%)
        - Neither alive: zero spending (estate planning scenario)
        - Survivor percentage reflects that some costs (housing, utilities) don't scale linearly
    """
    if person1_alive and person2_alive:
        # Both alive - no adjustment
        return amount
    elif person1_alive or person2_alive:
        # One alive - apply survivor percentage reduction
        survivor_factor = Decimal(str(survivor_pct)) / Decimal('100')
        return amount * survivor_factor
    else:
        # Neither alive - no spending needed
        return Decimal('0')


def calculate_inflation_factor(inflation_rate: float, years_since_start: int) -> Decimal:
    """
    Calculate compound inflation factor with Decimal precision.
    
    Computes the multiplier needed to adjust start-year amounts for cumulative inflation.
    This is the primary inflation calculation function using Decimal for precision.
    
    Args:
        inflation_rate: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        years_since_start: Number of years since start (0 = no adjustment)
        
    Returns:
        Decimal: Compound inflation factor to multiply base amounts
        
    Output Column Mapping:
        Used internally for inflation adjustments in Total_Spend
        
    Business Rules:
        - Formula: (1 + rate) ^ years  
        - Year 0 returns factor of 1.0 (no adjustment)
        - Provides high precision for multi-year compounding calculations
        - Replaces legacy float-based inflation calculations
        
    Example:
        calculate_inflation_factor(0.03, 5) returns 1.159274074 for 3% over 5 years
    """
    if years_since_start == 0:
        return Decimal('1')
    return (Decimal('1') + Decimal(str(inflation_rate))) ** years_since_start


def calculate_spending_target(
    phase: str,
    year_index: int,
    infl: float,
    target_spend: float,
    gogo_percent: float,
    slow_percent: float,
    nogo_percent: float,
    survivor_pct: float,
    person1_alive: bool,
    person2_alive: bool,
) -> Decimal:
    """
    Calculate complete inflation-adjusted spending target for a given year and situation.
    
    Orchestrates the full spending calculation by applying phase adjustments, inflation
    adjustments, and survivor benefit reductions to determine the appropriate spending
    target for the year. This is the main public interface for spending calculations.
    
    Args:
        phase: Lifecycle phase - "GoGo", "Slow", or "NoGo"
        year_index: Years since start of plan (0 = start year)  
        infl: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        target_spend: Base annual spending target in start year dollars
        gogo_percent: Percentage of base spending during GoGo phase
        slow_percent: Percentage of base spending during Slow phase
        nogo_percent: Percentage of base spending during NoGo phase  
        survivor_pct: Percentage of spending when only one person alive
        person1_alive: Whether primary person is alive
        person2_alive: Whether secondary person is alive
        
    Returns:
        Decimal: Final spending target for the year with all adjustments applied
        
    Output Column Mapping:
        Maps directly to Total_Spend column in retirement projection output
        
    Business Rules:
        1. Start with base Target Spend from configuration
        2. Apply phase percentage (GoGo/Slow/NoGo lifestyle adjustment)  
        3. Apply compound inflation adjustment from start year
        4. Apply survivor adjustment if applicable
        5. Result represents required spending to maintain lifestyle in current dollars
        
    Calculation Flow:
        Base Target → Phase % → Inflation → Survivor % → Final Total_Spend
    """
    # Step 1: Calculate base target spend
    base_target = calculate_base_target_spend(target_spend)
    
    # Step 2: Apply phase percentage adjustment
    phase_adjusted = apply_phase_percentage(
        base_target, phase, gogo_percent, slow_percent, nogo_percent
    )
    
    # Step 3: Apply inflation adjustment  
    inflation_adjusted = apply_inflation_adjustment(
        phase_adjusted, infl, year_index
    )
    
    # Step 4: Apply survivor adjustment
    final_amount = apply_survivor_adjustment(
        inflation_adjusted, survivor_pct, person1_alive, person2_alive
    )
    
    return final_amount


# Legacy function maintained for backward compatibility  
def infl_factor(infl: float, years_since_start: int) -> float:
    """
    Calculate compound inflation factor (legacy function).
    
    Args:
        infl: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        years_since_start: Number of years since start (0 = no adjustment)
        
    Returns:
        Compound inflation factor to multiply base amount
        
    Note:
        This function is deprecated. Use calculate_inflation_factor() for new code
        as it provides Decimal precision. Maintained for backward compatibility.
    """
    return (1.0 + infl) ** years_since_start


def infl_factor_decimal(rate: float, idx: int) -> Decimal:
    """
    Calculate inflation adjustment factor returning Decimal for precision (legacy name).
    
    Args:
        rate: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        idx: Number of years since start (0 = no inflation adjustment)
        
    Returns:
        Decimal factor to multiply base amount for inflation adjustment
        
    Note:
        This function is deprecated. Use calculate_inflation_factor() for new code
        which has a clearer name and consistent parameter naming. Maintained for
        backward compatibility.
    """
    return calculate_inflation_factor(rate, idx)


def spend_target(
    phase: str,
    year_index: int,
    infl: float,
    target_spend: float,
    gogo_percent: float,
    slow_percent: float,
    nogo_percent: float,
    survivor_pct: float,
    person1_alive: bool,
    person2_alive: bool,
) -> Decimal:
    """
    Calculate inflation-adjusted spending target (legacy function name).
    
    Args:
        phase: Lifecycle phase - "GoGo", "Slow", or "NoGo"  
        year_index: Years since start of plan (0 = start year)
        infl: Annual inflation rate as decimal
        target_spend: Base annual spending target in start year dollars
        gogo_percent: Percentage of base spending during GoGo phase
        slow_percent: Percentage of base spending during Slow phase  
        nogo_percent: Percentage of base spending during NoGo phase
        survivor_pct: Percentage of spending when only one person alive
        person1_alive: Whether primary person is alive
        person2_alive: Whether secondary person is alive
        
    Returns:
        Decimal amount representing target spending for the year
        
    Note:
        This function is maintained for backward compatibility. The logic has been
        refactored into modular functions but the interface remains unchanged.
        Uses calculate_spending_target() internally.
    """
    return calculate_spending_target(
        phase=phase,
        year_index=year_index,
        infl=infl, 
        target_spend=target_spend,
        gogo_percent=gogo_percent,
        slow_percent=slow_percent,
        nogo_percent=nogo_percent,
        survivor_pct=survivor_pct,
        person1_alive=person1_alive,
        person2_alive=person2_alive,
    )
