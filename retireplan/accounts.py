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
