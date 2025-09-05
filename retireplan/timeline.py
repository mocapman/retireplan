from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YearCtx:
    year: int
    age_you: int
    age_spouse: int
    phase: str  # "GoGo" | "Slow" | "NoGo"
    living: str  # "Joint" | "Survivor" | "None"


def make_years(
    start_year: int,
    birth_you: int,
    birth_spouse: int | None,
    final_you: int,
    final_spouse: int | None,
    gogo_years: int,
    slow_years: int,
) -> list[YearCtx]:
    cur_age_you = start_year - birth_you
    cur_age_sp = start_year - birth_spouse if birth_spouse else None
    horizon_you = start_year + (final_you - cur_age_you)
    horizon_sp = (
        start_year + (final_spouse - cur_age_sp)
        if final_spouse and cur_age_sp is not None
        else start_year
    )
    last_year = max(horizon_you, horizon_sp)

    out: list[YearCtx] = []
    for y in range(start_year, last_year + 1):
        ay = y - birth_you
        as_ = (y - birth_spouse) if birth_spouse else 0
        # phases counted from start_year
        idx = y - start_year
        if idx < gogo_years:
            phase = "GoGo"
        elif idx < gogo_years + slow_years:
            phase = "Slow"
        else:
            phase = "NoGo"
        # living status
        you_alive = ay <= final_you
        sp_alive = (as_ <= final_spouse) if final_spouse and birth_spouse else False
        living = (
            "Joint"
            if (you_alive and sp_alive)
            else ("Survivor" if (you_alive or sp_alive) else "None")
        )
        out.append(YearCtx(y, ay, as_, phase, living))
    return out
