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

    def _draw_from(self, name: str, amount: float) -> float:
        if amount <= 0:
            return 0.0
        if name == "Brokerage":
            take = min(self.brokerage, amount)
            self.brokerage -= take
            return take
        if name == "Roth":
            take = min(self.roth, amount)
            self.roth -= take
            return take
        if name == "IRA":
            take = min(self.ira, amount)
            self.ira -= take
            return take
        return 0.0

    def withdraw_sequence(
        self, need: float, order: tuple[str, str, str]
    ) -> tuple[float, float, float]:
        remaining = max(0.0, need)
        draws = {"Brokerage": 0.0, "Roth": 0.0, "IRA": 0.0}
        for leg in order:
            take = self._draw_from(leg, remaining)
            draws[leg] += take
            remaining -= take
            if remaining <= 1e-9:
                break
        return draws["Brokerage"], draws["Roth"], draws["IRA"]

    def apply_growth(self) -> None:
        self.brokerage *= 1.0 + self.gr_brokerage
        self.roth *= 1.0 + self.gr_roth
        self.ira *= 1.0 + self.gr_ira
