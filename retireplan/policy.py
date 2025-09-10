#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/policy.py

Tax policy constants and Required Minimum Distribution (RMD) tables.

This module contains federal tax brackets, Social Security taxation thresholds,
and IRS Uniform Lifetime Tables for RMD calculations. These values represent
current tax policy and should be updated as tax laws change.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations

# Federal tax brackets for 2024 tax year (taxable income thresholds and rates)
# Format: (upper_limit, tax_rate) - rates apply to income within each bracket
FED_BRACKETS = {
    "Single": [
        (11600, 0.10),    # 10% on income up to $11,600
        (47150, 0.12),    # 12% on income from $11,601 to $47,150
        (100525, 0.22),   # 22% on income from $47,151 to $100,525
        (191950, 0.24),   # 24% on income from $100,526 to $191,950
        (243725, 0.32),   # 32% on income from $191,951 to $243,725
        (609350, 0.35),   # 35% on income from $243,726 to $609,350
        (float("inf"), 0.37),  # 37% on income over $609,350
    ],
    "MFJ": [  # Married Filing Jointly
        (23200, 0.10),    # 10% on income up to $23,200
        (94300, 0.12),    # 12% on income from $23,201 to $94,300
        (201050, 0.22),   # 22% on income from $94,301 to $201,050
        (383900, 0.24),   # 24% on income from $201,051 to $383,900
        (487450, 0.32),   # 32% on income from $383,901 to $487,450
        (731200, 0.35),   # 35% on income from $487,451 to $731,200
        (float("inf"), 0.37),  # 37% on income over $731,200
    ],
}

# Social Security provisional income thresholds for determining taxable amount
# Format: (first_threshold, second_threshold) for 0% -> 50% -> 85% taxation
# Provisional income = other ordinary income + 50% of SS benefits
SS_THRESHOLDS = {
    "Single": (25000.0, 34000.0),  # 0% below $25k, up to 50% between $25k-$34k, up to 85% above $34k
    "MFJ": (32000.0, 44000.0),    # 0% below $32k, up to 50% between $32k-$44k, up to 85% above $44k
}

# IRS Uniform Lifetime Table (2022+) for Required Minimum Distribution calculations
# Used when IRA owner is alive and spouse is within 10 years of age (most common case)
# Format: {age: distribution_factor} where RMD = account_balance / factor
# Lower factors mean higher required distribution percentages
_UNIFORM_LIFETIME = {
    73: 26.5,
    74: 25.5,
    75: 24.6,
    76: 23.7,
    77: 22.9,
    78: 22.0,
    79: 21.1,
    80: 20.2,
    81: 19.4,
    82: 18.5,
    83: 17.7,
    84: 16.8,
    85: 16.0,
    86: 15.2,
    87: 14.4,
    88: 13.7,
    89: 12.9,
    90: 12.2,
    91: 11.5,
    92: 10.8,
    93: 10.1,
    94: 9.5,
    95: 8.9,
    96: 8.4,
    97: 7.8,
    98: 7.3,
    99: 6.8,
    100: 6.4,
    101: 6.0,
    102: 5.6,
    103: 5.2,
    104: 4.9,
    105: 4.6,
    106: 4.3,
    107: 4.1,
    108: 3.9,
    109: 3.7,
    110: 3.5,
    111: 3.4,
    112: 3.3,
    113: 3.1,
    114: 3.0,
    115: 2.9,
}


def rmd_factor(age: int) -> float:
    """
    Get Required Minimum Distribution factor from IRS Uniform Lifetime Table.
    
    Args:
        age: Age of the IRA owner
        
    Returns:
        Distribution factor used to calculate RMD (IRA_balance / factor)
        Returns infinity for ages below 73 (no RMD required)
        
    Business Rules:
        - RMD required starting at age 73 (as of 2023 tax law changes)
        - Uses IRS Uniform Lifetime Table (assumes spouse within 10 years)
        - Factor decreases with age (higher required distribution percentage)
        - For ages not in table, uses nearest lower age factor
        - Ages below 73 return infinity (no RMD required)
        
    Example:
        Age 73: factor 26.5 -> RMD = balance / 26.5 ≈ 3.77% of balance
        Age 80: factor 20.2 -> RMD = balance / 20.2 ≈ 4.95% of balance
        Age 72: factor infinity -> RMD = 0 (no requirement)
    """
    # No RMD required before age 73
    if age < 73:
        return float("inf")
        
    # Find the appropriate factor for this age
    # Use nearest factor at or below the person's age
    for a in sorted(_UNIFORM_LIFETIME.keys(), reverse=True):
        if age >= a:
            return _UNIFORM_LIFETIME[a]
            
    # Fallback to age 73 factor if somehow no match found
    return _UNIFORM_LIFETIME[73]
