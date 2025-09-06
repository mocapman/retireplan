# taxes.py
from __future__ import annotations
from typing import Tuple
from decimal import Decimal

from retireplan.policy import FED_BRACKETS, SS_THRESHOLDS


def progressive_tax(taxable_income: float, filing: str) -> float:
    """Compute regular federal tax on taxable income using simple progressive brackets."""
    if taxable_income <= 0:
        return 0.0
    tax = 0.0
    prev = 0.0
    for upper, rate in FED_BRACKETS[filing]:
        span = min(taxable_income, upper) - prev
        if span > 0:
            tax += span * rate
            prev = upper
        if taxable_income <= upper:
            break
    return max(0.0, tax)


def ss_taxable_amount(ss_total: float, other_ordinary: float, filing: str) -> float:
    """
    Taxable Social Security using the 50%/85% rules.
    other_ordinary = ordinary income excluding SS (e.g., IRA draws, conversions).
    """
    if ss_total <= 0:
        return 0.0
    base, addl = SS_THRESHOLDS[filing]
    provisional = other_ordinary + 0.5 * ss_total

    if provisional <= base:
        return 0.0

    # Portion up to 'addl' threshold: up to 50% of SS
    part1 = min(provisional - base, addl - base)
    taxable1 = 0.5 * min(ss_total, part1 * 2.0) if part1 > 0 else 0.0

    # Over 'addl': 85% of the excess, limited so total taxable ≤ 85% of SS
    excess = max(0.0, provisional - addl)
    taxable2 = 0.85 * excess

    taxable = taxable1 + taxable2
    return min(0.85 * ss_total, max(0.0, taxable))


def compute_tax_magi(
    ira_ordinary: float,
    roth_conversion: float,
    ss_total: float,
    std_deduction: float,
    filing: str,
) -> Tuple[float, float, float, float]:
    """
    Returns: (federal_tax, ss_taxable, taxable_income, magi)
    Notes:
      - Brokerage draws assumed basis-funded here (no realized gains modeled in v1).
      - MAGI (ACA) ≈ AGI for our inputs = ordinary + ss_taxable (no muni interest modeled).
    """
    ordinary = max(0.0, ira_ordinary + roth_conversion)
    ss_tax = ss_taxable_amount(ss_total, ordinary, filing)
    taxable_income = max(0.0, ordinary + ss_tax - max(0.0, std_deduction))
    tax = progressive_tax(taxable_income, filing)
    magi = ordinary + ss_tax
    return tax, ss_tax, taxable_income, magi
