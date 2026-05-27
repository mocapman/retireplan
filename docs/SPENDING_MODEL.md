# Retirement Spending Model

## Overview

The retirement planner uses a target-based spending model with phase-specific percentages to calculate spending for different retirement phases.

## New Model (Current)

- **Target Spend**: Annual spending target in today's dollars
- **Phase Percentages**: Percentage of target spend for each phase
  - GoGo Phase: Default 100% (active, travel-heavy years)
  - SlowGo Phase: Default 80% (reduced activity)  
  - NoGo Phase: Default 70% (minimal activity)

## Calculation

For each year, the planned spending for the phase is calculated as:

```
Phase Spend = Target Spend × (Phase % / 100)
```

The amount is then adjusted for:
- Inflation since start year
- Survivor adjustment (if one person passes away)

## Example

With Target Spend = $120,000:
- GoGo spending: $120,000 × 100% = $120,000/year
- SlowGo spending: $120,000 × 80% = $96,000/year  
- NoGo spending: $120,000 × 70% = $84,000/year

## Migration from Legacy Model

The previous model used separate dollar amounts for each phase:
- `gogo_annual`, `slow_annual`, `nogo_annual`

These have been replaced with the target + percentage approach for better flexibility and clarity.

## Configuration

In YAML configuration files:

```yaml
spending:
  target_spend: 120000      # Annual target in today's dollars
  gogo_percent: 100.0       # GoGo phase percentage  
  slow_percent: 80.0        # SlowGo phase percentage
  nogo_percent: 70.0        # NoGo phase percentage
  gogo_years: 10           # Years in GoGo phase
  slow_years: 6            # Years in SlowGo phase
  survivor_percent: 70     # Spending when one person passes
```