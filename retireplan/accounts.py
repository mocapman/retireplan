from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Accounts:
    brokerage: float
    roth: float
    ira: float
    gr_brokerage: float
    gr_roth: float
    gr_ira: float

    def withdraw_sequence(self, need: float) -> tuple[float, float, float]:
        """Return draws (brk, roth, ira) to meet 'need' in order Brokerage→Roth→IRA."""
        b = min(self.brokerage, max(0.0, need))
        r_need = max(0.0, need - b)
        r = min(self.roth, r_need)
        i = max(0.0, r_need - r)
        # apply to balances
        self.brokerage -= b
        self.roth -= r
        self.ira -= i
        return b, r, i

    def apply_growth(self) -> None:
        self.brokerage *= 1.0 + self.gr_brokerage
        self.roth *= 1.0 + self.gr_roth
        self.ira *= 1.0 + self.gr_ira
