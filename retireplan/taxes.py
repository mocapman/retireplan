#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/taxes.py

Federal tax calculations for retirement planning.

This module provides comprehensive tax calculations including progressive federal
income tax, Social Security taxation using provisional income rules, and MAGI
(Modified Adjusted Gross Income) calculations for ACA premium subsidies.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations
from typing import Tuple
from decimal import Decimal

from retireplan.policy import FED_BRACKETS, SS_THRESHOLDS


def progressive_tax(taxable_income: float, filing: str) -> float:
    """
    Compute federal income tax using progressive tax brackets.
    
    Args:
        taxable_income: Income subject to federal income tax
        filing: Filing status - "Single" or "MFJ" (Married Filing Jointly)
        
    Returns:
        Federal income tax owed
        
    Business Rules:
        - Uses current federal tax brackets from policy.py
        - Progressive system: higher rates apply only to income above thresholds
        - Different brackets for Single vs. Married Filing Jointly
        - Tax cannot be negative
    """
    if taxable_income <= 0:
        return 0.0
    
    tax = 0.0
    prev = 0.0
    
    # Apply progressive brackets: each bracket rate applies only to income in that range
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
    Calculate taxable portion of Social Security benefits using federal rules.
    
    Uses the "provisional income" method with 50%/85% taxation thresholds.
    This is a complex calculation that determines how much of SS benefits
    become subject to federal income tax.
    
    Args:
        ss_total: Total annual Social Security benefits received
        other_ordinary: Other ordinary income (IRA draws, conversions, wages, etc.)
        filing: Filing status - "Single" or "MFJ"
        
    Returns:
        Amount of Social Security benefits subject to federal income tax
        
    Business Rules:
        - Provisional income = other_ordinary + 50% of SS benefits
        - Below first threshold: 0% of SS is taxable
        - Between thresholds: up to 50% of SS is taxable  
        - Above second threshold: up to 85% of SS is taxable
        - Taxable amount cannot exceed 85% of total SS benefits
        
    Thresholds (2024):
        Single: $25,000 (0% -> 50%), $34,000 (50% -> 85%)
        MFJ: $32,000 (0% -> 50%), $44,000 (50% -> 85%)
    """
    if ss_total <= 0:
        return 0.0
        
    # Get thresholds for filing status
    base, addl = SS_THRESHOLDS[filing]
    
    # Calculate provisional income (key concept in SS taxation)
    provisional = other_ordinary + 0.5 * ss_total

    # Below first threshold: no SS is taxable
    if provisional <= base:
        return 0.0

    # Between first and second threshold: up to 50% of SS taxable
    # Amount in this range determines how much of the 50% applies
    part1 = min(provisional - base, addl - base)
    taxable1 = 0.5 * min(ss_total, part1 * 2.0) if part1 > 0 else 0.0

    # Above second threshold: 85% rate applies to excess
    # This is additional tax on top of the 50% portion
    excess = max(0.0, provisional - addl)
    taxable2 = 0.85 * excess

    # Total taxable amount, capped at 85% of total SS benefits
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
    Calculate comprehensive tax and MAGI for retirement planning.
    
    This is the main tax calculation function that computes federal income tax,
    taxable Social Security amount, and Modified Adjusted Gross Income (MAGI)
    used for ACA premium subsidy calculations.
    
    Args:
        ira_ordinary: Traditional IRA distributions including RMDs
        roth_conversion: Roth conversion amount (IRA -> Roth transfer)  
        ss_total: Total Social Security benefits received
        std_deduction: Standard deduction amount (inflation-adjusted)
        filing: Filing status - "Single" or "MFJ"
        
    Returns:
        Tuple containing:
        - federal_tax: Federal income tax owed
        - ss_taxable: Taxable portion of Social Security benefits
        - taxable_income: Income subject to federal tax (after standard deduction)
        - magi: Modified Adjusted Gross Income for ACA calculations
        
    Business Rules:
        - IRA distributions and Roth conversions are fully taxable as ordinary income
        - Brokerage draws assumed to be return of basis (not modeled as taxable)
        - Social Security taxation uses complex provisional income rules
        - MAGI approximates AGI for our simplified model (excludes municipal interest)
        - Standard deduction reduces taxable income but not MAGI
        
    Tax Calculation Flow:
        1. Calculate total ordinary income (IRA + conversions)
        2. Determine taxable SS amount using provisional income method
        3. Apply standard deduction to get taxable income
        4. Calculate federal tax using progressive brackets
        5. MAGI = ordinary income + taxable SS (simplified)
    """
    # Total ordinary income subject to federal tax
    ordinary = max(0.0, ira_ordinary + roth_conversion)
    
    # Calculate taxable portion of Social Security benefits
    ss_tax = ss_taxable_amount(ss_total, ordinary, filing)
    
    # Taxable income after standard deduction
    taxable_income = max(0.0, ordinary + ss_tax - max(0.0, std_deduction))
    
    # Federal income tax using progressive brackets
    tax = progressive_tax(taxable_income, filing)
    
    # MAGI for ACA premium subsidy calculations
    # Simplified: AGI approximation (excludes municipal bond interest, etc.)
    magi = ordinary + ss_tax
    
    return tax, ss_tax, taxable_income, magi
