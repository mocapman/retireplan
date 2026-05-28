# RetirePlan Project Dependency Audit

Date: 2026-05-27

Scope: current repository state, focused on the retirement planner package,
GUI display path, tests, and active documentation. This is a factual usage map,
not a refactor plan.

Authority note: `docs/PROJECT_CONTRACT.md` controls project philosophy and
scope. `docs/SPENDING_MODEL.md` is active model documentation where it matches
current code. Files under `docs/source_material/` are reference material only.

## 1. Seed / Config Inputs

Important current input names are the names used by `retireplan/inputs.py` and
`retireplan/default_config.yaml`. Some source material and the project contract
use newer/proposed names such as `target_spend_base`, `inflation_rate`, or
`standard_deduction_annual_base`; those are not the current code-facing names in
this checkout.

| Name | Source file | Unit | Timing | Purpose | First code consumer | Downstream outputs |
|---|---|---|---|---|---|---|
| `balances.brokerage` -> `balances_brokerage` | `retireplan/default_config.yaml`, `retireplan/inputs.py` | dollars | start of projection | Starting taxable brokerage balance | `run_plan()` initializes `brokerage_end` | `Brokerage_Draw`, `Brokerage_Balance`, `Total_Assets`, `Shortfall` |
| `balances.roth` -> `balances_roth` | same | dollars | start of projection | Starting Roth balance | `run_plan()` initializes `roth_end` | `Roth_Draw`, `Roth_Balance`, `Total_Assets` |
| `balances.ira` -> `balances_ira` | same | dollars | start of projection | Starting Traditional IRA balance | `run_plan()` initializes `ira_end` | `IRA_Draw`, `Roth_Conversion`, `RMD`, `IRA_Balance`, `MAGI`, `Taxes_Due` |
| `spending.start_year` -> `start_year` | `default_config.yaml`, `inputs.py` | calendar year | projection start | First projected year | `make_years()` via `run_plan()` | `Year`, ages, phase sequencing |
| `spending.year1_spend` -> `year1_spend` | same | dollars | first projection row only | Manual Year 1 lifestyle spend seed | Year 1 branch in `run_plan()` | Year 1 `Target_Spend`, `Total_Spend` |
| `spending.year1_brokerage_draw` | same | dollars | first projection row only | Manual Year 1 brokerage draw | Year 1 branch in `run_plan()` | Year 1 `Brokerage_Draw`, `Brokerage_Balance` |
| `spending.year1_ira_draw` | same | dollars | first projection row only | Manual Year 1 IRA draw | Year 1 branch in `run_plan()` | Year 1 `IRA_Draw`, `IRA_Balance` |
| `spending.year1_roth_draw` | same | dollars | first projection row only | Manual Year 1 Roth draw | Year 1 branch in `run_plan()` | Year 1 `Roth_Draw`, `Roth_Balance` |
| `spending.year1_roth_conversion` | same | dollars | first projection row only | Manual Year 1 IRA-to-Roth conversion | Year 1 branch in `run_plan()` | Year 1 `Roth_Conversion`, `MAGI`, `IRA_Balance`, `Roth_Balance` |
| `spending.year1_magi_income` | same | dollars | first projection row only | Manual Year 1 MAGI income seed | Year 1 branch in `run_plan()` | Year 1 `MAGI`, `MAGI_Remaining`, `MAGI_Status` |
| `spending.year1_magi_losses` | same | dollars | first projection row only | Manual Year 1 MAGI loss offset | Year 1 branch in `run_plan()` | Year 1 `MAGI`, `MAGI_Remaining`, `MAGI_Status` |
| `spending.target_spend` | same | dollars | annual baseline in start-year dollars | Base annual lifestyle spending target | `spend_target()` via `run_plan()` | Year 2+ `Target_Spend`, `Total_Spend`, draw need, `Shortfall` |
| `spending.gogo_percent` | same | whole percent | annual phase rule | GoGo spending percentage of target | `apply_phase_percentage()` via `spend_target()` | `Target_Spend`, `Total_Spend`, draws |
| `spending.slow_percent` | same | whole percent | annual phase rule | Slow phase spending percentage of target | same | same |
| `spending.nogo_percent` | same | whole percent | annual phase rule | NoGo spending percentage of target | same | same |
| `spending.gogo_years` | same | years | phase sequencing | Number of GoGo years | `make_years()` | `Lifestyle`, `Target_Spend` |
| `spending.slow_years` | same | years | phase sequencing | Number of Slow years after GoGo | `make_years()` | `Lifestyle`, `Target_Spend` |
| `spending.survivor_percent` | same | whole percent | annual survivor rule | Spending percentage when one person survives | `apply_survivor_adjustment()` via `spend_target()` | `Target_Spend`, `Total_Spend`, draws |
| `rates.inflation` | same | decimal annual rate | projection-wide assumption | Inflation/COLA factor | `infl_factor_decimal()`, `spend_target()`, `ss_for_year()` | `Target_Spend`, `Std_Deduction`, `Social_Security`, `Target_MAGI` internal calculation |
| `rates.brokerage_growth` | same | decimal annual rate | annual end-of-year growth | Brokerage balance growth | Year 1 and Year 2+ balance update in `run_plan()` | `Brokerage_Balance`, `Total_Assets` |
| `rates.roth_growth` | same | decimal annual rate | annual end-of-year growth | Roth balance growth | same | `Roth_Balance`, `Total_Assets` |
| `rates.ira_growth` | same | decimal annual rate | annual end-of-year growth | IRA balance growth | same | `IRA_Balance`, `Total_Assets`, future `RMD` |
| `social_security.person1_start_age` -> `ss_person1_start_age` | same | age | annual eligibility rule | Person 1 Social Security start age | `ss_for_year()` | `Social_Security`, `MAGI`, `Taxes_Due` |
| `social_security.person1_annual_at_start` -> `ss_person1_annual_at_start` | same | annual dollars | first payable year amount | Person 1 annual benefit at claiming age | `ss_for_year()` | same |
| `social_security.person2_start_age` -> `ss_person2_start_age` | same | age | annual eligibility rule | Person 2 Social Security start age | `ss_for_year()` | same |
| `social_security.person2_annual_at_start` -> `ss_person2_annual_at_start` | same | annual dollars | first payable year amount | Person 2 annual benefit at claiming age | `ss_for_year()` | same |
| `tax_health.magi_floor_base` | same | dollars | base-year annual lower guardrail | MAGI floor used for status display | Year 1 and Year 2+ `MAGI_Floor` calculation | `MAGI_Floor`, `MAGI_Status` |
| `tax_health.magi_target_base` | same | dollars | base-year annual target | Preferred MAGI target used by Year 1 display and Year 2+ conversion loop | Year 1 branch and Year 2+ `target_magi` calculation | Year 1 `Target_MAGI`, Year 2+ `Roth_Conversion`, `MAGI`, `Taxes_Due` |
| `tax_health.magi_ceiling_base` | same | dollars | base-year annual upper guardrail | Hard MAGI guardrail for status and Roth conversion cap | Year 1 and Year 2+ `MAGI_Ceiling` calculation | `MAGI_Ceiling`, `MAGI_Remaining_To_Ceiling`, `MAGI_Status`, `Roth_Conversion` |
| `tax_health.standard_deduction_base` | same | dollars | base-year annual deduction | Federal standard deduction baseline | Year 2+ `std_ded` calculation | `Std_Deduction`, `Taxes_Due`; not MAGI |
| `tax_health.rmd_start_age` | same | age | annual policy threshold | Age where RMD calculation begins | RMD branch in `run_plan()` | `RMD`, `IRA_Balance`, `Brokerage_Balance`, `MAGI`, `Taxes_Due` |
| `tax_health.aca_end_age` | same | age | annual policy threshold | Stops MAGI-target conversions when person1 reaches guardrail end age | Year 2+ `target_magi` and conversion-loop guard | `Roth_Conversion`, `MAGI`; indirectly taxes and balances |
| `draw_order` | `default_config.yaml`, `inputs.py` | ordered account names | projection-wide strategy | Withdrawal priority among Brokerage, Roth, IRA | `parse_draw_order()` in `run_plan()` | `Brokerage_Draw`, `Roth_Draw`, `IRA_Draw`, balances, `Shortfall` |

## 2. Core Annual Calculation Flow

The current engine entry point is `retireplan.engine.core.run_plan(cfg, events=None)`.

1. Event setup
   - Optional `events` are reserved for a future model and are ignored by the
     current engine.

2. Timeline/year setup
   - `make_years()` receives `start_year`, birth years, final ages, `gogo_years`,
     and `slow_years`.
   - It returns immutable `YearCtx` rows with calendar year, ages, `Lifestyle`
     phase, and alive flags.
   - Phase is based on years since start, not age.

3. Starting balances and draw order
   - `balances_brokerage`, `balances_roth`, and `balances_ira` are converted to
     `Decimal` running balances.
   - `draw_order` is parsed and validated by `parse_draw_order()`.

4. Year 1 branch
   - Uses manual seed values: `year1_spend`, `year1_roth_conversion`,
     `year1_magi_income`, `year1_magi_losses`, and manual account draws.
   - Known one-time Year 1 spending is included directly in `year1_spend`.
   - Sets Social Security, taxes, RMD, standard deduction, and shortfall to zero.
   - Computes Year 1 MAGI as:
     `year1_magi_income - year1_magi_losses + year1_roth_conversion`.
   - Applies conversion, draws, and end-of-year growth to balances.

5. Year 2+ inflation and deduction setup
   - `infl_factor_decimal(cfg.inflation, idx)` computes an inflation factor.
   - Filing status is recalculated from alive flags: both alive -> `MFJ`, else
     `Single`.
   - `standard_deduction_base` is halved for `Single` and multiplied by the
     inflation factor.

6. Year 2+ MAGI guardrail setup
   - `target_magi = magi_target_base * inflation_factor` only while person1 is
     alive and below `aca_end_age`.
   - `magi_floor_base` and `magi_ceiling_base` inflate on the same schedule.
   - Roth conversion sizing uses the lower of Target MAGI and MAGI Ceiling.
   - If person1 is at/above `aca_end_age`, target MAGI is zero and conversion
     targeting stops.

7. Spending calculation
   - `spend_target()` calls `calculate_spending_target()`.
   - Flow: base `target_spend` -> phase percent -> inflation -> survivor percent.
   - Result is stored as `target_spend_lifestyle`.

8. Social Security calculation
   - `ss_for_year()` is called for each person.
   - Benefits begin at each configured start age.
   - COLA compounds from the first payable year using `cfg.inflation`.
   - If both are alive, benefits are summed. If one survives, the survivor gets
     the higher of the two calculated benefits.

9. RMD logic
    - RMD applies when person1 is alive, person1 age is at/above `rmd_start_age`,
      and IRA balance is positive.
    - Amount is `ira_end / rmd_factor(person1_age)`.
    - RMD is excluded from the balance passed to normal draw-order withdrawals.

10. Draw strategy
    - Need before ordinary draws is:
      `target_spend_lifestyle - Social_Security - RMD`, floored at zero.
    - `withdraw_with_order()` draws from Brokerage, Roth, and IRA in configured
      order.
    - `Shortfall` is the remaining gap between lifestyle target and cash
      provided by Social Security, RMD, and account draws.

11. Roth conversion logic
    - An inner `tax_and_magi(conv)` calls `compute_tax_magi()`.
    - `ira_ordinary` is `RMD + IRA_Draw`.
    - `roth_conversion` is passed separately.
    - The loop tries up to eight iterations to fill remaining MAGI room without
      exceeding available IRA balance.
    - Final conversion reduces IRA balance and increases Roth balance.

12. MAGI, taxable income, and tax calculation
    - `compute_tax_magi()` calculates:
      - ordinary income = IRA ordinary distributions + Roth conversions
      - taxable Social Security via provisional income thresholds
      - taxable income = ordinary + taxable Social Security - standard deduction
      - federal tax via `progressive_tax()`
      - MAGI = ordinary + taxable Social Security
    - `taxable_income` and taxable Social Security are returned internally but
      not placed in output rows.

13. MAGI guardrail logic
    - The planner exposes MAGI floor, target, ceiling, remaining-to-target,
      remaining-to-ceiling, and status.
    - The planner does not calculate ACA subsidy dollars.

14. Account balance updates
    - Surplus RMD beyond spending need after Social Security is deposited into
      brokerage.
    - Growth is applied after draws, RMD handling, and conversion.
    - End balances become next year starting balances.

15. Output row creation
    - Rows are dictionaries keyed to `retireplan/schema.py`.
    - Monetary values are rounded by `round_dollar()`.
    - Ages/years are rounded by `round_year()`.

## 3. Output / Schema Fields

Schema is defined in `retireplan/schema.py`. GUI table conversion uses
`retireplan/projections.py`. Diagnostics use `tools/diagnostics_report.py`.
Tests assert schema coverage and selected field behavior.

| Output field | Defined | Populated | Current status | GUI/export/test expectation |
|---|---|---|---|---|
| `Year` | `schema.py` | `run_plan()` both branches | real | visible in GUI; tested |
| `Person1_Age` | `schema.py` | `run_plan()` from `YearCtx` | real | visible; tested |
| `Person2_Age` | `schema.py` | `run_plan()` from `YearCtx` | real; zero for single-person contexts from timeline | visible; tested |
| `Filing` | `schema.py` | `run_plan()` from alive flags | real for projection row, not directly from `filing_status` after timeline starts | visible; diagnostics |
| `Lifestyle` | `schema.py` | `run_plan()` from `YearCtx.phase` | real | visible; tested |
| Base Spend | not in schema | not populated | absent | old docs mention it, current code does not |
| `Target_Spend` | `schema.py` | Year 1 from `year1_spend`; Year 2+ from spending model | real but Year 1 has manual semantics | visible; tested; diagnostics |
| `Total_Spend` | `schema.py` | Year 1 equals `year1_spend`; Year 2+ target spend + tax | real but Year 1 does not include tax in same way | visible; tested |
| `Taxes_Due` | `schema.py` | Year 1 zero; Year 2+ federal tax plus simplified estimated state tax | partial | visible; tested; no detailed state brackets |
| `Social_Security` | `schema.py` | Year 1 zero; Year 2+ `ss_for_year()` survivor logic | partial for Year 1 | visible; tested |
| `IRA_Draw` | `schema.py` | Year 1 manual; Year 2+ draw-order result | real | visible; tested |
| `Brokerage_Draw` | `schema.py` | Year 1 manual; Year 2+ draw-order result | real | visible; tested |
| `Roth_Draw` | `schema.py` | Year 1 manual; Year 2+ draw-order result | real | visible; tested |
| `Roth_Conversion` | `schema.py` | Year 1 manual; Year 2+ MAGI-target loop | real but strategy is narrow | visible; tested |
| `RMD` | `schema.py` | Year 1 zero; Year 2+ living-person age/balance rule | partial for Year 1 | visible; tested |
| `MAGI` | `schema.py` | Year 1 manual formula; Year 2+ tax helper | real but simplified | hidden by default; diagnostics/tested |
| `Taxable_Income` | `schema.py` | Year 1 zero; Year 2+ tax helper result | diagnostic | hidden/exported/tested |
| `MAGI_Floor` | `schema.py` | Year 1 from `magi_floor_base`; Year 2+ active inflation-adjusted floor while MAGI targeting applies | real while targeting is active | hidden; tested |
| `Target_MAGI` | `schema.py` | Year 1 from `magi_target_base`; Year 2+ active inflation-adjusted target while MAGI targeting applies | real while targeting is active | hidden; tested |
| `MAGI_Ceiling` | `schema.py` | Year 1 from `magi_ceiling_base`; Year 2+ active inflation-adjusted ceiling while MAGI targeting applies | real while targeting is active | hidden; tested |
| `MAGI_Remaining` | `schema.py` | target - projected MAGI while targeting is active | real while targeting is active | hidden; tested |
| `MAGI_Remaining_To_Ceiling` | `schema.py` | ceiling - projected MAGI while targeting is active | real while targeting is active | hidden; tested |
| `MAGI_Status` | `schema.py` | classifies MAGI against floor/ceiling while targeting is active | real while targeting is active | hidden; tested |
| `Std_Deduction` | `schema.py` | Year 1 zero; Year 2+ calculated deduction | partial for Year 1 | hidden; diagnostics |
| `IRA_Balance` | `schema.py` | `run_plan()` end-of-year balance | real | visible; tested |
| `Brokerage_Balance` | `schema.py` | `run_plan()` end-of-year balance | real | visible; tested |
| `Roth_Balance` | `schema.py` | `run_plan()` end-of-year balance | real | visible; tested |
| `Total_Assets` | `schema.py` | sum of three end balances | real | visible; tested |
| `Shortfall` | `schema.py` | Year 1 zero; Year 2+ unmet lifestyle target | partial for Year 1 | hidden; tested |

## 4. Tax / MAGI Audit Notes

### Taxes Due

Current inputs to Year 2+ `Taxes_Due`:

- IRA ordinary income: RMD + IRA draw.
- Roth conversion.
- Social Security total, of which some is taxable through provisional income.
- Standard deduction.
- Filing status from alive flags.
- Federal brackets from `retireplan/engine/policy.py`.

Not currently included:

- Oregon tax.
- taxable brokerage gains, dividends, or interest.
- federal tax credits.
- ACA subsidy repayment or premium tax credit reconciliation.
- current-year taxes in Year 1.
- separate tax output components.

### Taxable Income

Current calculation exists inside `compute_tax_magi()`:

`max(0, ordinary + taxable_social_security - standard_deduction)`.

It is returned by the helper as the third tuple value, but the engine assigns it
to `_taxable` and does not expose it in rows, schema, diagnostics, GUI, or tests.

### MAGI

Year 1 MAGI:

`year1_magi_income - year1_magi_losses + year1_roth_conversion`.

Year 2+ MAGI:

`IRA ordinary income + Roth conversion + taxable Social Security`.

Current MAGI does not include:

- taxable brokerage capital gains.
- dividends.
- interest.
- wages or other ordinary income after Year 1.
- municipal bond interest or other MAGI adjustments.
- ACA-specific reconciliation details.

### MAGI Guardrails

Current behavior:

- `magi_floor_base`, `magi_target_base`, and `magi_ceiling_base` are the active
  MAGI planning values.
- `MAGI_Remaining = Target_MAGI - MAGI`.
- `MAGI_Remaining_To_Ceiling = MAGI_Ceiling - MAGI`.
- `MAGI_Status` is `Warning` below the floor, `Good` within floor/ceiling, and
  `FAIL` above the ceiling.
- The planner does not calculate or output ACA subsidy dollars.

Diagnostic components needed later for audit/export, not implemented here:

- taxable IRA distributions separate from Roth conversions.
- taxable Social Security.
- taxable income.
- federal tax and Oregon tax split.
- brokerage capital gains, dividends, and interest.
- ACA subsidy formula/table, premium, calculated subsidy, and subsidy status.
- RMD surplus handling amount.
- account starting balance, draw, conversion, growth, and ending balance per
  account.

## 5. Known Gaps Or Suspicious Areas

These are verified observations from current usage. No fixes are made in this
audit document.

- Project contract uses terms such as `target_spend_base`, `inflation_rate`,
  `standard_deduction_annual_base`, and Oregon tax. Current code uses
  `target_spend`, `inflation`, `standard_deduction_base`, and federal tax only.
- `docs/SPENDING_MODEL.md` is directionally consistent with current spending
  code, but its YAML example uses `target_spend`, which matches this checkout,
  while newer source material mentions `target_spend_base`.
- Year 1 bypasses many normal calculations: Social Security, tax, RMD, standard
  deduction, and shortfall are forced to zero.
- Year 1 `Target_Spend` and `Total_Spend` both equal `year1_spend`; Year 2+
  `Total_Spend` includes taxes.
- `Target_MAGI`, `MAGI_Remaining`, and `MAGI_Status` are populated for Year 2+
  while MAGI targeting is active.
- `Taxable_Income` and major tax/MAGI components are exported as hidden audit
  fields.
- `Taxes_Due` currently means federal income tax plus simplified estimated state
  tax.
- Brokerage draws use the simple brokerage tax-character model; brokerage cash
  creates no MAGI, and holdings sales create estimated gains.
- RMD timing selects the living person's age: person1 if alive, otherwise
  person2 if alive.
- `retireplan/engine/accounts.py` contains an `Accounts` dataclass that is not
  used by `run_plan()`; the active engine path uses `withdraw_with_order()`.
- `tools/diagnostics_report.py` is used by tests but `tools/` remains ignored by
  `.gitignore`; if future commits rely on it, ensure it remains tracked or move
  diagnostics into the package.

## 6. Documentation And File Authority

Current active documentation:

- `docs/PROJECT_CONTRACT.md`: controlling scope and design contract.
- `docs/SPENDING_MODEL.md`: active spending-model documentation.
- `docs/PROJECT_DEPENDENCY_AUDIT.md`: current dependency and output audit.
- `docs/source_material/`: historical/reference material only.
- `docs/archive/`: ignored local archive, not intended for commits.

