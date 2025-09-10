from __future__ import annotations
from decimal import Decimal


def infl_factor(infl: float, years_since_start: int) -> float:
    return (1.0 + infl) ** years_since_start


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
    # Calculate phase-specific amount from target spend and percentage
    if phase == "GoGo":
        base = target_spend * (gogo_percent / 100.0)
    elif phase == "Slow":
        base = target_spend * (slow_percent / 100.0)
    else:  # NoGo
        base = target_spend * (nogo_percent / 100.0)
    
    amt = base * infl_factor(infl, year_index)

    # Determine if survivor situation
    if person1_alive and person2_alive:
        # Both alive - full amount
        pass
    elif person1_alive or person2_alive:
        # One alive - apply survivor percentage
        amt *= survivor_pct / 100.0
    else:
        # Neither alive - no spending
        amt = 0.0

    return Decimal(str(amt))
