from __future__ import annotations


def infl_factor(infl: float, years_since_start: int) -> float:
    return (1.0 + infl) ** years_since_start


def spend_target(
    phase: str,
    year_index: int,
    infl: float,
    gogo: float,
    slow: float,
    nogo: float,
    survivor_pct: float,
    person1_alive: bool,
    person2_alive: bool,
) -> float:
    base = gogo if phase == "GoGo" else slow if phase == "Slow" else nogo
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

    return amt
