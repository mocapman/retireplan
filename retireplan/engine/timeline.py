from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YearCtx:
    year: int
    age_person1: int
    age_person2: int
    phase: str  # "GoGo" | "Slow" | "NoGo"
    person1_alive: bool
    person2_alive: bool


def make_years(
    start_year: int,
    birth_person1: int,
    birth_person2: int | None,
    final_age_person1: int,
    final_age_person2: int | None,
    gogo_years: int,
    slow_years: int,
) -> list[YearCtx]:
    # Final calendar years each person is alive
    last_p1 = birth_person1 + final_age_person1
    last_p2 = (
        (birth_person2 + final_age_person2)
        if (birth_person2 and final_age_person2)
        else start_year
    )
    last_year = max(last_p1, last_p2)

    out: list[YearCtx] = []
    for y in range(start_year, last_year + 1):
        ap1 = y - birth_person1
        ap2 = (y - birth_person2) if birth_person2 else 0

        idx = y - start_year
        if idx < gogo_years:
            phase = "GoGo"
        elif idx < gogo_years + slow_years:
            phase = "Slow"
        else:
            phase = "NoGo"

        person1_alive = ap1 <= final_age_person1
        person2_alive = (
            (ap2 <= final_age_person2)
            if (birth_person2 and final_age_person2)
            else False
        )

        out.append(YearCtx(y, ap1, ap2, phase, person1_alive, person2_alive))
    return out
