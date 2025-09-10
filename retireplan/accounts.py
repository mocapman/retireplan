#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/accounts.py

Retirement account management and withdrawal logic.

This module manages the three main retirement account types (Brokerage, Roth IRA,
Traditional IRA) including balance tracking, withdrawal sequencing, and growth
applications. It provides a structured approach to account operations.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple


@dataclass
class Accounts:
    """
    Manages retirement account balances and operations.
    
    Tracks three main account types with their balances and growth rates,
    and provides methods for withdrawals and growth application.
    
    Attributes:
        brokerage: Taxable brokerage account balance
        roth: Roth IRA account balance (tax-free growth/withdrawals)
        ira: Traditional IRA account balance (tax-deferred, taxable on withdrawal)
        gr_brokerage: Annual growth rate for brokerage account
        gr_roth: Annual growth rate for Roth IRA
        gr_ira: Annual growth rate for Traditional IRA
    """
    brokerage: float
    roth: float
    ira: float
    gr_brokerage: float
    gr_roth: float
    gr_ira: float

    def _draw_from(self, name: str, amount: float) -> float:
        """
        Withdraw specified amount from a single account type.
        
        Args:
            name: Account name - "Brokerage", "Roth", or "IRA"
            amount: Amount to withdraw
            
        Returns:
            Actual amount withdrawn (limited by account balance)
            
        Side Effects:
            Updates the account balance by subtracting withdrawn amount
        """
        if amount <= 0:
            return 0.0
            
        if name == "Brokerage":
            take = min(self.brokerage, amount)
            self.brokerage -= take
            return take
        elif name == "Roth":
            take = min(self.roth, amount)
            self.roth -= take
            return take
        elif name == "IRA":
            take = min(self.ira, amount)
            self.ira -= take
            return take
        else:
            return 0.0

    def withdraw_sequence(
        self, need: float, order: tuple[str, str, str]
    ) -> tuple[float, float, float]:
        """
        Withdraw funds from accounts in specified sequence to meet a spending need.
        
        Args:
            need: Total amount needed for spending
            order: Tuple specifying withdrawal order (e.g., ("Brokerage", "Roth", "IRA"))
            
        Returns:
            Tuple of (brokerage_draw, roth_draw, ira_draw) amounts
            
        Business Rules:
            - Withdrawals follow specified order strictly
            - Cannot withdraw more than available balance
            - Stops when need is fully met or all accounts exhausted
            - Small amounts (< 1e-9) treated as zero to handle rounding
        """
        remaining = max(0.0, need)
        draws = {"Brokerage": 0.0, "Roth": 0.0, "IRA": 0.0}
        
        for leg in order:
            take = self._draw_from(leg, remaining)
            draws[leg] += take
            remaining -= take
            
            # Stop if need is essentially met (handle rounding errors)
            if remaining <= 1e-9:
                break
                
        return draws["Brokerage"], draws["Roth"], draws["IRA"]

    def apply_growth(self) -> None:
        """
        Apply annual growth to all account balances.
        
        Multiplies each account balance by (1 + growth_rate) to simulate
        investment returns. Growth rates are typically set annually.
        
        Side Effects:
            Updates all account balances with growth applied
        """
        self.brokerage *= 1.0 + self.gr_brokerage
        self.roth *= 1.0 + self.gr_roth
        self.ira *= 1.0 + self.gr_ira


def withdraw_with_order(
    brokerage_balance: Decimal, 
    roth_balance: Decimal, 
    ira_balance: Decimal, 
    need: Decimal, 
    order: Tuple[str, str, str]
) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    """
    Withdraw funds from retirement accounts in specified order to meet spending need.
    
    This function implements the core withdrawal logic used by the retirement
    planning engine. It takes money from accounts in the specified order until
    the need is met or all accounts are exhausted.
    
    Args:
        brokerage_balance: Available brokerage account balance
        roth_balance: Available Roth IRA balance  
        ira_balance: Available Traditional IRA balance
        need: Amount of money needed for spending
        order: Tuple specifying withdrawal order (e.g., ("Brokerage", "Roth", "IRA"))
        
    Returns:
        Tuple containing:
        - Brokerage draw amount
        - Roth draw amount  
        - IRA draw amount
        - Remaining brokerage balance
        - Remaining Roth balance
        - Remaining IRA balance
        - Unmet need (if any)
        
    Business Rules:
        - Withdrawals follow the specified order strictly
        - Cannot withdraw more than account balance
        - Stops when need is met or all accounts exhausted
        - Uses small epsilon (1e-9) to handle rounding errors
        
    Note:
        This function does not modify the input balances - it returns new values.
        This is designed for use in the engine's calculation loop where balances
        are managed separately.
        
    TODO: Consider merging with Accounts.withdraw_sequence() once Decimal
    adoption is complete throughout the codebase.
    """
    remaining = max(Decimal(0), need)
    draws = {"Brokerage": Decimal(0), "Roth": Decimal(0), "IRA": Decimal(0)}
    
    # Track balances (don't modify inputs)
    b, r, i = brokerage_balance, roth_balance, ira_balance
    
    for leg in order:
        # Determine available balance for current account type
        cap = b if leg == "Brokerage" else r if leg == "Roth" else i
        take = min(cap, remaining)
        
        # Update running balance
        if leg == "Brokerage":
            b -= take
        elif leg == "Roth":
            r -= take
        else:  # IRA
            i -= take
            
        # Track withdrawal amount
        draws[leg] += take
        remaining -= take
        
        # Stop if need is met (with small tolerance for rounding)
        if remaining <= Decimal("1e-9"):
            break
            
    return draws["Brokerage"], draws["Roth"], draws["IRA"], b, r, i, remaining


def parse_draw_order(draw_order: str) -> Tuple[str, str, str]:
    """
    Parse the draw order string into a tuple of account types.
    
    Args:
        draw_order: Comma-separated string of account names (e.g., "Brokerage, Roth, IRA")
        
    Returns:
        Tuple of three account type strings in withdrawal order
        
    Example:
        parse_draw_order("Brokerage, IRA, Roth") -> ("Brokerage", "IRA", "Roth")
        
    TODO: Add validation to ensure all three account types are specified
    and are valid account names.
    """
    parts = [part.strip() for part in draw_order.split(",")]
    return tuple(parts)
