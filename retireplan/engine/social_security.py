#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/social_security.py

Social Security benefit calculations.

This module calculates annual Social Security benefits based on starting age,
initial benefit amount, and cost-of-living adjustments (COLA) over time.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations


def ss_for_year(
    age_now: int,
    start_age: int | None,
    annual_at_start: float | None,
    year_index: int,
    cola: float,
) -> float:
    """
    Calculate Social Security benefit for a given year with COLA adjustments.
    
    Args:
        age_now: Current age of the person
        start_age: Age when Social Security benefits begin (None if not applicable)
        annual_at_start: Annual benefit amount in the first year of collection
        year_index: Years since start of retirement plan (used for COLA compounding)
        cola: Annual cost-of-living adjustment rate as decimal (e.g., 0.025 for 2.5%)
        
    Returns:
        Annual Social Security benefit amount for this year (0 if not eligible)
        
    Business Rules:
        - Benefits only start when person reaches start_age
        - COLA adjustments compound annually from first payable year
        - If start_age or annual_at_start is None, no benefits are paid
        - Benefits grow with COLA from the year they first become payable
        
    Example:
        Person turns 62 in year 3 with $30,000 annual benefit and 2.5% COLA:
        - Years 0-2: $0 (too young)
        - Year 3: $30,000 * (1.025)^0 = $30,000
        - Year 4: $30,000 * (1.025)^1 = $30,750
        - Year 5: $30,000 * (1.025)^2 = $31,519
    """
    # Return zero if SS parameters not configured
    if start_age is None or annual_at_start is None:
        return 0.0
        
    # Return zero if person hasn't reached benefit start age yet
    if age_now < start_age:
        return 0.0
        
    # Calculate years since benefits became payable (COLA compounds from start)
    years_since_start = max(0, age_now - start_age)
    
    # Apply compound COLA adjustment from first payable year
    return annual_at_start * ((1.0 + cola) ** years_since_start)
