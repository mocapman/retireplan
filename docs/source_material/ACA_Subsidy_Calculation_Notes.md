# ACA Subsidy Calculation — Research Notes
## For RetirePlan Python Project

---

## The Situation

Oregon resident, MFJ, Benton County (zip 97330), Kaiser Gold 0 plan.
ACA subsidies are a core financial variable — worth up to $23,448/year.
MAGI must stay within a precise window to preserve them.

---

## The Four Zones

| MAGI | Subsidy | Notes |
|------|---------|-------|
| Below $43,000 | $0 | **Medicaid trap** — assets disqualify, effectively pay full price |
| $43,000–$84,999 | Sliding scale | **Operating window** — maximize conversions here |
| $85,000+ | $0 | **Hard cliff** — full premium $2,555/month ($30,660/year) |

Both edges are bad. The goal is to stay inside the window, not just below the top.

---

## Raw HealthSherpa Data (Kaiser Gold 0, 2026)

Full premium (unsubsidized): **$2,555/month**
Subsidy = $2,555 - Premium at any MAGI point.

| MAGI | Monthly Subsidy |
|------|----------------|
| $43,000 | $1,954 |
| $45,000 | $1,929 |
| $47,000 | $1,904 |
| $49,000 | $1,877 |
| $51,000 | $1,850 |
| $53,000 | $1,821 |
| $55,000 | $1,793 |
| $57,000 | $1,765 |
| $59,000 | $1,736 |
| $61,000 | $1,706 |
| $63,000 | $1,675 |
| $65,000 | $1,655 |
| $67,000 | $1,638 |
| $69,000 | $1,622 |
| $71,000 | $1,605 |
| $73,000 | $1,589 |
| $75,000 | $1,572 |
| $77,000 | $1,555 |
| $79,000 | $1,539 |
| $81,000 | $1,522 |
| $83,000 | $1,506 |
| $84,000 | $1,497 |
| $85,000 | $0 (hard cliff) |

---

## Shape of the Curve

The subsidy does NOT follow a simple linear formula.
Drop per $2,000 MAGI reveals two distinct segments:

- **$43k–$63k:** drops ~$25–$31/per $2k (faster decline)
- **$63k–$84k:** drops ~$16–$17 per $2k (slower decline)

This means converting above $63k costs LESS in lost subsidy per dollar
than converting just above $43k. Strategically important for the optimizer.

---

## The Formula

A **degree-4 polynomial curve fit** was chosen because:
- Simple linear formula had max $468/year error — unacceptable for decisions
- Two-segment linear had max $91/year error — acceptable but inelegant
- Degree-4 polynomial has max $86/year, avg $26/year error — best accuracy with clean math
- Degree 3 bought nothing over degree 2; degree 4 was meaningfully better

### User-Facing Inputs (3 values only)

```
aca_magi_floor:            43000   # MAGI where full subsidy begins
aca_magi_ceiling:          84000   # MAGI where subsidy reaches zero (cliff fires at 85000)
aca_subsidy_monthly_full:  1954    # Monthly subsidy at floor MAGI
```

### Internal Calculation (derived, never exposed to user)

```python
def calc_aca_subsidy_annual(magi, aca_magi_floor, aca_magi_ceiling, aca_subsidy_monthly_full):
    """
    Calculate annual ACA subsidy using degree-4 polynomial curve fit
    derived from HealthSherpa data for Kaiser Gold 0, Oregon zip 97330, MFJ.

    Returns 0 if MAGI is below floor (Medicaid trap) or at/above 85000 (hard cliff).
    """
    if magi < aca_magi_floor:
        return 0  # Medicaid trap
    if magi >= 85000:
        return 0  # Hard cliff

    # Normalize MAGI to 0-1 range between floor and ceiling
    x = (magi - aca_magi_floor) / (aca_magi_ceiling - aca_magi_floor)

    # Degree-4 polynomial coefficients derived from 2026 HealthSherpa data
    # These are recalculated if user updates the three input values
    # Coefficients: a4, a3, a2, a1, a0
    # subsidy_monthly = a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0
    # Coefficients from numpy.polyfit on 2026 data:
    #   -869.0x^4 + 1822.8x^3 - 1024.1x^2 - 385.9x + 1951.8
    
    subsidy_monthly = (
        -869.0047 * x**4
        + 1822.8167 * x**3
        - 1024.1311 * x**2
        - 385.9558 * x
        + 1951.7758
    )
    return max(0, subsidy_monthly * 12)
```

---

## Accuracy Summary

| Formula | Max Annual Error | Avg Annual Error |
|---------|-----------------|-----------------|
| Single linear | $1,450 | $717 |
| Single slope (0.012) | $468 | $209 |
| Two-segment linear | $91 | $34 |
| Degree-2 polynomial | $151 | $58 |
| **Degree-4 polynomial** | **$86** | **$26** |

---

## Maintenance

**Normal year (ACA rules unchanged):**
- Verify max subsidy at $43k on HealthSherpa
- Update `aca_subsidy_monthly_full` if it changed
- Curve reshapes automatically

**Rule change year (new cliffs or new slope):**
- Run ~10 HealthSherpa queries across the MAGI range
- Update `aca_magi_floor`, `aca_magi_ceiling`, `aca_subsidy_monthly_full`
- Re-derive polynomial coefficients from new data points
- Update coefficients in `policy.py`

**Plan change year (switch from Kaiser Gold 0):**
- Same process as rule change year with new plan data

---

## Strategic Implications

- **Below $43k:** Never go here — loses all subsidy, Medicaid ineligible due to assets
- **$43k–$63k:** Conversion costs ~$0.168/dollar in lost subsidy (steeper slope)
- **$63k–$84k:** Conversion costs ~$0.099/dollar in lost subsidy (flatter slope)
- **At $85k:** Costs ~$31k/year in lost subsidy — hard stop, never cross

The conversion optimizer (Phase 3) must show cost-per-conversion-dollar
across the full MAGI window using this curve.

---

## Implementation Notes

- Function belongs in `engine/policy.py` alongside tax brackets and RMD table
- Three user inputs belong in `inputs.py` and exposed in GUI Tax & Health tab
- Replaces the existing `aca_subsidy_annual` static field which is currently
  loaded but never used in the engine
- Must be called after MAGI is calculated each year in `engine/core.py`
- Output column `ACA_Subsidy` should be added to results table
