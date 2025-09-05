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
    living: str,
) -> float:
    base = gogo if phase == "GoGo" else slow if phase == "Slow" else nogo
    amt = base * infl_factor(infl, year_index)
    if living == "Survivor":
        amt *= survivor_pct / 100.0
    if living == "None":
        amt = 0.0
    return amt
