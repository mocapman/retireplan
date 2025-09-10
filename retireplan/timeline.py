#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/timeline.py

Timeline and lifecycle phase management for retirement planning.

This module defines the year-by-year context for retirement planning, including
person ages, lifecycle phases (GoGo/Slow/NoGo), and survival status. It generates
the complete timeline from start year to final year when both persons have passed.

Author: Retirement Planning Team
License: MIT
Last Updated: 2024-01-10
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YearCtx:
    """
    Context information for a single year in the retirement plan timeline.
    
    This immutable dataclass captures all the contextual information needed
    for calculations in a given year, including ages, lifecycle phase,
    and survival status of both persons.
    
    Attributes:
        year: Calendar year (e.g., 2024)
        age_person1: Age of primary person in this year
        age_person2: Age of secondary person in this year (0 if single)
        phase: Lifecycle phase - "GoGo", "Slow", or "NoGo"
        person1_alive: Whether primary person is alive in this year
        person2_alive: Whether secondary person is alive in this year
    """
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
    """
    Generate complete timeline of years with context for retirement planning.
    
    Creates a year-by-year timeline from start year until both persons have
    passed away, with lifecycle phases and survival status calculated for
    each year.
    
    Args:
        start_year: First year of the retirement plan
        birth_person1: Birth year of primary person
        birth_person2: Birth year of secondary person (None for single person)
        final_age_person1: Age when primary person passes away
        final_age_person2: Age when secondary person passes away (None for single)
        gogo_years: Number of years in active "GoGo" phase
        slow_years: Number of years in moderate "Slow" phase
        
    Returns:
        List of YearCtx objects, one for each year in the timeline
        
    Business Rules:
        - Timeline continues until both persons have passed away
        - Lifecycle phases: GoGo -> Slow -> NoGo based on year counts
        - Phase transitions are based on years since start, not ages
        - Single person planning uses person2 parameters as None/0
        
    Phase Transitions:
        - Years 0 to gogo_years-1: "GoGo" phase (active lifestyle)
        - Years gogo_years to gogo_years+slow_years-1: "Slow" phase
        - Years gogo_years+slow_years and beyond: "NoGo" phase (care needs)
    """
    # Calculate final calendar years for each person
    last_p1 = birth_person1 + final_age_person1
    last_p2 = (
        (birth_person2 + final_age_person2)
        if (birth_person2 and final_age_person2)
        else start_year  # Default for single person
    )
    last_year = max(last_p1, last_p2)

    out: list[YearCtx] = []
    for y in range(start_year, last_year + 1):
        # Calculate ages in this calendar year
        ap1 = y - birth_person1
        ap2 = (y - birth_person2) if birth_person2 else 0

        # Determine lifecycle phase based on years since start
        idx = y - start_year
        if idx < gogo_years:
            phase = "GoGo"
        elif idx < gogo_years + slow_years:
            phase = "Slow"
        else:
            phase = "NoGo"

        # Determine survival status for each person
        person1_alive = ap1 <= final_age_person1
        person2_alive = (
            (ap2 <= final_age_person2)
            if (birth_person2 and final_age_person2)
            else False  # Single person scenario
        )

        out.append(YearCtx(y, ap1, ap2, phase, person1_alive, person2_alive))
    return out
