#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/spending.py

Spending target calculations and inflation adjustments.

This module calculates spending targets based on lifecycle phases (GoGo/Slow/NoGo),
applies inflation adjustments over time, and handles survivor benefit reductions
when one person passes away.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations
from decimal import Decimal


def infl_factor(infl: float, years_since_start: int) -> float:
    """
    Calculate compound inflation factor.
    
    Args:
        infl: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        years_since_start: Number of years since start (0 = no adjustment)
        
    Returns:
        Compound inflation factor to multiply base amount
        
    Example:
        infl_factor(0.03, 5) returns (1.03)^5 = 1.159274...
    """
    return (1.0 + infl) ** years_since_start


def infl_factor_decimal(rate: float, idx: int) -> Decimal:
    """
    Calculate inflation adjustment factor returning Decimal for precision.
    
    Same calculation as infl_factor() but returns Decimal type for
    high-precision financial calculations.
    
    Args:
        rate: Annual inflation rate as decimal (e.g., 0.03 for 3%)
        idx: Number of years since start (0 = no inflation adjustment)
        
    Returns:
        Decimal factor to multiply base amount for inflation adjustment
        
    Example:
        infl_factor_decimal(0.03, 5) returns Decimal('1.159274074')
        
    TODO: Consider consolidating with infl_factor() once Decimal adoption
    is complete throughout the codebase.
    """
    return (Decimal(1) + Decimal(str(rate))) ** idx


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
    Calculate inflation-adjusted spending target for a given year and situation.
    
    Applies lifecycle phase adjustments, inflation adjustments, and survivor
    benefit reductions to determine the appropriate spending target.
    
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
        
    Business Rules:
        - Phase determines percentage of base spending to use
        - Inflation compounds annually from start year
        - When both alive: use full phase-adjusted amount
        - When one alive: apply survivor percentage reduction  
        - When neither alive: spending is zero
        - Survivor reduction reflects reduced household expenses
    """
    # BUSINESS RULE: Lifecycle phase spending adjustments
    # GoGo: Active lifestyle with higher spending (travel, activities)
    # Slow: Reduced activity but still independent living
    # NoGo: Minimal activity, potentially higher care costs
    if phase == "GoGo":
        base = target_spend * (gogo_percent / 100.0)
    elif phase == "Slow":
        base = target_spend * (slow_percent / 100.0)
    else:  # NoGo
        base = target_spend * (nogo_percent / 100.0)
    
    # Apply compound inflation adjustment
    amt = base * infl_factor(infl, year_index)

    # BUSINESS RULE: Survivor benefit adjustments
    # When one person dies, expenses typically reduce (housing, food, etc.)
    # but some fixed costs remain, so reduction is partial
    if person1_alive and person2_alive:
        # Both alive - use full calculated amount
        pass
    elif person1_alive or person2_alive:
        # One alive - apply survivor percentage reduction
        amt *= survivor_pct / 100.0
    else:
        # Neither alive - no spending needed
        amt = 0.0

    return Decimal(str(amt))
