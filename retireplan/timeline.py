from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YearCtx:
    year: int
    age_you: int
    age_spouse: int
    phase: str  # "GoGo" | "Slow" | "NoGo"
    living: str  # "Joint" | "Survivor" | "None"
    you_alive: bool
    spouse_alive: bool


def make_years(
    start_year: int,
    birth_you: int,
    birth_spouse: int | None,
    final_you: int,
    final_spouse: int | None,
    gogo_years: int,
    slow_years: int,
) -> list[YearCtx]:
    # Final calendar years each person is alive
    last_you = birth_you + final_you
    last_sp = (birth_spouse + final_spouse) if (birth_spouse and final_spouse) else start_year
    last_year = max(last_you, last_sp)

    out: list[YearCtx] = []
    for y in range(start_year, last_year + 1):
        ay = y - birth_you
        as_ = (y - birth_spouse) if birth_spouse else 0

        idx = y - start_year
        if idx < gogo_years:
            phase = "GoGo"
        elif idx < gogo_years + slow_years:
            phase = "Slow"
        else:
            phase = "NoGo"

        you_alive = ay <= final_you
        spouse_alive = (as_ <= final_spouse) if (birth_spouse and final_spouse) else False

        if you_alive and spouse_alive:
            living = "Joint"
        elif you_alive or spouse_alive:
            living = "Survivor"
        else:
            living = "None"

        out.append(YearCtx(y, ay, as_, phase, living, you_alive, spouse_alive))
    return out
