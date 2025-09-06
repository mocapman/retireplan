from __future__ import annotations


def ss_for_year(
    age_now: int,
    start_age: int | None,
    annual_at_start: float | None,
    year_index: int,
    cola: float,
) -> float:
    if start_age is None or annual_at_start is None:
        return 0.0
    if age_now < start_age:
        return 0.0
    # benefit grows with COLA from the first payable year
    years_since_start = max(0, age_now - start_age)
    return annual_at_start * ((1.0 + cola) ** years_since_start)
