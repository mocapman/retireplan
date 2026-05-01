# PROJECT_AUDIT.md
## RetirePlan Python — Full Codebase Audit
**Date:** 2026-04-30  
**Auditor:** Claude (automated review)  
**Scope:** All Python source, tests, config, and VBA reference

---

## 1. What the App Currently Does

RetirePlan is a year-by-year retirement projection tool with a tkinter/ttkbootstrap GUI. Given a set of starting balances, demographic info, and spending goals, it projects every year from `start_year` until both persons have died (based on configured final ages).

Each projected year produces:
- Inflation-adjusted lifestyle spending target (by GoGo / SlowGo / NoGo phase)
- Social Security income with COLA
- Required Minimum Distribution (IRS Uniform Lifetime Table)
- Iterative Roth conversion to hit a MAGI target (for ACA subsidy preservation)
- Account draws from Brokerage, Roth, and IRA in user-specified order
- Federal income tax via progressive brackets
- SS taxable amount via the provisional income method
- Year-end account balances after growth
- Shortfall flagging when income can't cover spending

The GUI is a single-window split-pane app: a tabbed input panel on the left, a scrollable result table on the right. Inputs are loaded from and saved to YAML files.

---

## 2. Files and Their Purpose

### Root
| File | Purpose |
|------|---------|
| `README.md` | One-line placeholder |
| `.gitattributes` | Empty |

### `retireplan/` (package root)
| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies (pandas, numpy, ttkbootstrap, matplotlib, openpyxl, pyyaml, tksheet) |
| `.gitignore` | Excludes `.venv/`, `tests/`, `examples/`, `tools/`, `docs/`, `*.csv` |
| `.pre-commit-config.yaml` | Black + Ruff + mypy hooks |
| `SPENDING_MODEL.md` | Documents the target-spend + phase-percentage spending model |
| `retireplan/default_config.yaml` | Default parameters loaded at app startup |
| `config_Brokerage_Roth_IRA_120000.0_*.yaml` | Saved user config (auto-named) |

### `retireplan/retireplan/` (Python package)
| File | Purpose |
|------|---------|
| `__init__.py` | Empty |
| `schema.py` | Canonical column list (`COLUMNS`), key/label/visibility helpers |
| `inputs.py` | `Inputs` dataclass + `load_yaml()` + `validate()` |
| `gui.py` | Thin entry-point shim delegating to `gui/main_window.py` |

### `retireplan/retireplan/engine/`
| File | Purpose |
|------|---------|
| `core.py` | `run_plan()` — the main year-by-year loop, orchestrates all modules |
| `accounts.py` | `withdraw_with_order()` + `parse_draw_order()` (used by engine); also an `Accounts` class (unused in main loop) |
| `taxes.py` | `progressive_tax()`, `ss_taxable_amount()`, `compute_tax_magi()` |
| `spending.py` | `spend_target()` / `calculate_spending_target()` — phase + inflation + survivor |
| `social_security.py` | `ss_for_year()` — COLA compounding from collection start age |
| `timeline.py` | `make_years()` — generates `YearCtx` list with ages, phase, alive flags |
| `policy.py` | 2024 federal tax brackets, SS provisional income thresholds, IRS RMD table, `rmd_factor()` |
| `precision.py` | `round_dollar()`, `round_percent()`, `round_year()`, `ROUNDING_RULES` dict |
| `utils.py` | `generate_filename()` — timestamped CSV/YAML filename builder |
| `rmd.py` | **Empty stub** |
| `year.py` | **Empty stub** |

### `retireplan/retireplan/gui/`
| File | Purpose |
|------|---------|
| `main_window.py` | `RetirePlanApp` — root window, wires together panels, calls `run_plan()` on change |
| `input_panel.py` | Tabbed form (Personal / Accounts / Spending / SS / Rates / Tax&Health / Strategy) |
| `results_display.py` | Scrollable table for projection output |
| `config_manager.py` | Converts `Inputs` ↔ dict for the GUI layer |
| `file_operations.py` | Load / save YAML config, export CSV |
| `__init__.py`, `__main__.py` | Package wiring |

### `retireplan/tests/` (19 files, excluded from git per .gitignore)
Tests cover: smoke, imports, inputs loading, calculation consistency, account growth, MAGI, precision/rounding, draw order, RMD, survivor benefit, non-negativity, invariants. Many use `examples/sample_inputs.yaml` (also excluded from git).

---

## 3. Hardcoded Assumptions

| Assumption | Location | Value |
|-----------|---------|-------|
| Federal tax brackets | `engine/policy.py:19-38` | 2024 MFJ + Single — **not inflation-indexed over multi-decade projections** |
| SS provisional income thresholds | `engine/policy.py:43-46` | $32K / $44K (MFJ), $25K / $34K (Single) — **never adjusted for inflation** |
| IRS Uniform Lifetime RMD table | `engine/policy.py:52-96` | 2022+ table, ages 73–115 |
| Filing status after death | `engine/core.py:192` | MFJ when both alive → Single when one dies. No Head-of-Household. |
| Brokerage draws tax treatment | `engine/taxes.py:143` | Treated as **return of basis** — no capital gains tax modeled |
| MAGI targeting stops at ACA end age | `engine/core.py:196-200` | Conversions drop to zero at `aca_end_age` (default 65). No post-65 strategy. |
| Year 1 SS income | `engine/core.py:122` | Hardcoded to `$0` regardless of config |
| Year 1 taxes | `engine/core.py:123` | Hardcoded to `$0` |
| Year 1 MAGI, RMD, Roth conversion | `engine/core.py:124,173-175` | All hardcoded to `$0` |
| Only person1 drives RMD/ACA timing | `engine/core.py:267-273, 196-200` | Person2 IRA, RMD, and ACA cutoff not modeled |
| Growth applied after draws | `engine/core.py:336-338` | End-of-year; Python applies to post-draw balance |

---

## 4. Assumptions That Come From User Input

All are fields on the `Inputs` dataclass, loadable via YAML or entered in the GUI:

| Input | Key | GUI Tab |
|-------|-----|---------|
| Birth years (both persons) | `birth_year_person1/2` | Personal |
| Final ages (both persons) | `final_age_person1/2` | Personal |
| Filing status | `filing_status` | Personal |
| Account balances (Brokerage, Roth, IRA) | `balances_*` | Accounts |
| Account growth rates | `brokerage_growth`, `roth_growth`, `ira_growth` | Rates |
| Inflation rate | `inflation` | Rates |
| Spending target (today's $) | `target_spend` | Spending |
| Phase percentages (GoGo, SlowGo, NoGo) | `gogo_percent`, `slow_percent`, `nogo_percent` | Spending |
| Phase durations | `gogo_years`, `slow_years` | Spending |
| Survivor spending % | `survivor_percent` | Spending |
| Year 1 actuals (spend, draws, cash events) | `year1_spend`, `year1_*_draw`, `year1_cash_events` | Spending |
| SS start ages and benefit amounts | `ss_person1/2_start_age`, `ss_person1/2_annual_at_start` | Social Security |
| RMD start age | `rmd_start_age` | Tax & Health |
| ACA end age | `aca_end_age` | Tax & Health |
| MAGI target base | `magi_target_base` | Tax & Health |
| Standard deduction base | `standard_deduction_base` | Tax & Health |
| Draw order | `draw_order` | Strategy |
| ACA subsidy annual | `aca_subsidy_annual` | (YAML only, GUI has no field) |

---

## 5. Calculations That Are Implemented

1. **Timeline generation** (`timeline.py`) — year-by-year ages, GoGo/Slow/NoGo phases, and alive flags
2. **Inflation-adjusted spending target** (`spending.py`) — `base × phase% × (1+r)^n`
3. **Survivor spending reduction** (`spending.py`) — multiplies by `survivor_percent / 100` when one person is gone
4. **Social Security COLA** (`social_security.py`) — compounds from the year collection starts (`age_now − start_age` years)
5. **Survivor SS benefit** (`core.py:249-256`) — when one person dies, survivor gets the higher of the two benefits
6. **Required Minimum Distribution** (`core.py:266-272`, `policy.py`) — IRS Uniform Lifetime Table factor, triggered at `rmd_start_age`
7. **Account withdrawals in configured order** (`accounts.py:withdraw_with_order`) — respects `draw_order` setting
8. **Iterative Roth conversion** (`core.py:301-321`) — up to 8 iterations to hit inflation-adjusted MAGI target
9. **SS taxable amount** (`taxes.py:56-108`) — proper provisional income method with 50%/85% thresholds
10. **Progressive federal income tax** (`taxes.py:21-53`) — correct bracket math for MFJ and Single
11. **Standard deduction** (`core.py:188`) — inflated annually from `standard_deduction_base`
12. **MAGI calculation** (`taxes.py:167`) — `ordinary income + taxable SS`
13. **Surplus RMD handling** (`core.py:331-333`) — excess RMD beyond spending need is deposited into Brokerage
14. **Account growth** (`core.py:336-338`) — applied end-of-year after draws
15. **Shortfall detection** (`core.py:285`) — flags years where income can't cover Target_Spend

---

## 6. Calculations That Are Missing or Incomplete

| Gap | Impact | Notes |
|-----|--------|-------|
| **IRMAA** (Medicare Part B/D surcharges) | Medium-high | VBA had a full `CalculateIRMAA()` with 2-year lookback. Python has no equivalent. Affects total spend by $1,500–$7,700/year per couple at higher MAGI. |
| **ACA premium subsidies** | Medium | `aca_subsidy_annual` field exists in `Inputs` but is loaded, validated, and then **never used** in `core.py` or any engine function. |
| **Post-65 / post-ACA Roth conversion strategy** | High | VBA had three conversion phases (Pre65, Post65, RMD-phase). Python stops all conversions at `aca_end_age`. Large IRA balances left unconverted leading to larger future RMDs. |
| **IRA early withdrawal penalty avoidance** | Medium | VBA checked `age1 >= 59` and blocked IRA draws before penalty-free age. Python applies the draw order without any age gate. |
| **Capital gains tax on brokerage** | Medium | Brokerage draws assumed to be return of basis. Long-term capital gains on growth are never taxed. Understates taxes for high-brokerage scenarios. |
| **Tax bracket inflation indexing** | Medium | Brackets are 2024 values and never adjusted. Over 20–30 year projections, bracket creep is ignored, overstating future taxes in nominal dollars. |
| **SS provisional income thresholds not indexed** | Low-medium | `$32,000`/`$44,000` MFJ thresholds never inflated. Over time, more SS income appears taxable than actually would be. |
| **Standard deduction not adjusted for Single vs MFJ** | **High** | When one spouse dies, filing changes to Single but `standard_deduction_base` stays the same. MFJ deduction is ~$29,200–$32,300; Single is ~$14,600–$16,550. Taxes are substantially understated in survivor years. |
| **Person2 IRA / RMD** | Medium | Only person1's age drives RMD calculations. A scenario where person2 has a large IRA is not modeled. |
| **State income tax** | Low | Not present, consistent with VBA. Fine as long as this is documented scope. |

---

## 7. Risky, Unclear, or Potentially Wrong Functions

### 7.1 — Roth Conversion Double-Count Bug (**HIGH PRIORITY**)
**Location:** `engine/core.py:292-298`

```python
def tax_and_magi(conv: Decimal) -> tuple[Decimal, Decimal]:
    tax, _ss_tax, _taxable, magi = compute_tax_magi(
        ira_ordinary=float(rmd + draw_ira + conv),   # <-- conv included here
        roth_conversion=float(conv),                  # <-- and again here
        ...
    )
```

In `compute_tax_magi` (taxes.py:154):
```python
ordinary = max(0.0, ira_ordinary + roth_conversion)
# = (rmd + draw_ira + conv) + conv = rmd + draw_ira + 2*conv
```

**The conversion is counted twice.** The function's docstring explicitly states `ira_ordinary` is "Traditional IRA distributions including RMDs" — meaning it should not include conversions. The correct call is `ira_ordinary=float(rmd + draw_ira)`.

**Effect:** The iterative loop compensates by converging to `conv ≈ (target_magi − ss_tax) / 2` instead of the correct `conv ≈ target_magi − ss_tax`. Result: Roth conversions are approximately half the intended amount each year. The reported MAGI appears correct (the loop converges to the target), but the IRA is being drained too slowly and the Roth is being filled too slowly. The test `test_magi_calculation` would catch this if it runs against a year with non-zero conversions.

---

### 7.2 — Standard Deduction Not Split by Filing Status (**HIGH PRIORITY**)
**Location:** `engine/core.py:188`

```python
std_ded = Decimal(str(cfg.standard_deduction_base)) * infl
```

This applies the same deduction regardless of `filing_status`. When one spouse dies (filing switches to "Single"), the deduction should roughly halve (from ~$29,200 to ~$14,600). Using the MFJ base for single years understates taxes by ~$2,000–$4,000/year during the survivor phase.

---

### 7.3 — Year 1 Always Sets SS, Tax, MAGI, RMD to Zero
**Location:** `engine/core.py:122-124`

```python
ss_income = Decimal(0)   # Not in config, or set if you wish
tax = Decimal(0)         # Not in config, or set if you wish
roth_conv = Decimal(0)   # Not in config, or set if you wish
```

If person1 is already collecting SS in year 1 (start_age ≤ person1's age in start_year), the actual SS income is silently zeroed. No tax is computed on any income for year 1. The comment "or set if you wish" suggests this is known but unfinished. RMD is also not calculated for year 1, even if the person is already past RMD age.

---

### 7.4 — `parse_draw_order` Has No Validation
**Location:** `engine/accounts.py:200-217`

```python
def parse_draw_order(draw_order: str) -> Tuple[str, str, str]:
    parts = [part.strip() for part in draw_order.split(",")]
    return tuple(parts)
```

The return type hint says `Tuple[str, str, str]` but the actual return is an unvalidated tuple of any length. A malformed string (e.g., "Brokerage, Roth") would return a 2-tuple. When iterated in `withdraw_with_order`, the third account would never be drawn from, silently. The `TODO` comment notes this but it is not yet fixed.

---

### 7.5 — `Accounts` Class Is Unused in the Main Engine
**Location:** `engine/accounts.py:22-122`

The `Accounts` dataclass with `withdraw_sequence()` and `apply_growth()` uses `float` arithmetic. The engine uses the separate `withdraw_with_order()` function (Decimal). The class is never instantiated by `core.py`. It represents dead code that could mislead future developers.

---

### 7.6 — SS COLA Uses Age Difference, VBA Uses Plan Year Index
**Location:** `engine/social_security.py:59`

```python
years_since_start = max(0, age_now - start_age)
```

Python COLA compounds from the year collection begins. VBA computes `SSIncome = SSName1Annual * (1 + inflationRate) ^ yearIndex` from plan year 0, regardless of when collection starts. If SS starts in year 5 of the plan, Python gives 0 COLA in year 5 and grows from there; VBA would give 5 years of COLA in year 5. The Python approach is more logically correct (COLA since first payment) but the two systems will diverge in any scenario where SS starts after the plan start year.

---

### 7.7 — Growth Order Differs from VBA
**Location:** `engine/core.py:336-338` vs `modProjections.bas:21`

Python applies growth **after draws**:
```python
broke_bal = b1 * (1 + cfg.brokerage_growth)   # b1 is post-draw balance
```

VBA applies growth **before draws** (step 0 of the loop):
```python
Call ApplyAccountGrowth(yearIndex, ...)  ' then draws happen later
```

This is a different assumption about when in the year the investment returns are realized. There is no universally correct choice, but the two systems will produce diverging balance curves. This choice is not documented in any comment or spec.

---

### 7.8 — Three Test Files Are Permanently Broken
**Location:** `tests/test_magi_and_medicare.py`, `tests/test_rmd.py`, `tests/test_invariants.py`

`test_magi_and_medicare.py` and `test_rmd.py` reference `row["Your_Age"]` and `cfg.birth_year_you`. These fields do not exist. The actual column is `Person1_Age` and the config field is `birth_year_person1`. Every assertion in these files will raise `KeyError` / `AttributeError`.

`test_invariants.py` imports `from tools.audit import audit_rows_against_cfg`. The `tools/` directory is in `.gitignore` and not part of the committed package. This import will fail with `ModuleNotFoundError` in any clean install.

---

### 7.9 — `sample_inputs.yaml` Has Structural Mismatch with Loader
**Location:** `examples/sample_inputs.yaml:1`, `inputs.py:76`

`sample_inputs.yaml` has `start_year: 2025` at the top level. The loader reads it as:
```python
start_year=s["start_year"],  # s = raw["spending"]
```
The `spending` section in `sample_inputs.yaml` has no `start_year` key. This causes a `KeyError` when any test calls `inputs.load_yaml("examples/sample_inputs.yaml")`. The `default_config.yaml` correctly places `start_year` under `spending`.

---

## 8. How Python Code Compares to the VBA Logic

| Dimension | VBA (reference) | Python (current) |
|-----------|----------------|-----------------|
| **SS taxation** | Hard-codes 85% of SS as taxable (known simplification, noted in ideas.txt) | Proper provisional income method — **more correct** |
| **Roth conversion strategy** | Three phases: Pre-65 (`Pre65ConversionLimit`), Post-65 (`Post65ConversionTarget`), RMD phase (`RMDStartConversionMin`) | Single phase: MAGI target while below ACA end age; zero after. **Missing post-65 phase.** |
| **IRMAA** | `CalculateIRMAA()` — 4-tier table, 2-year MAGI lookback, filing-status aware | **Not implemented** |
| **IRA penalty avoidance** | Blocks IRA draws if `age1 < 59` (`DrawWithIRALimit(iraMaxDraw=0)`) | **Not implemented** — draw order applies at any age |
| **Growth timing** | Growth first, then draws each year | Draws first, then growth each year |
| **Year 1 partial year** | Calculates `(12 - Month(StartDate) + 1) / 12` fraction | User provides year 1 actuals; no partial year math |
| **Draw order** | Default: IRA → Brokerage → Roth | Configurable; default config is Brokerage → Roth → IRA (opposite) |
| **Tax bracket math** | Correct progressive brackets (MFJ only) | Correct progressive brackets (MFJ + Single) — **better** |
| **Standard deduction** | Single `StandardDeduction` variable, not differentiated by status | Same single base — **same gap** |
| **RMD start age** | Hardcoded to 75 in `ValidateAndLoadInputs` | Configurable input, validated 70–80 — **better** |
| **ACA subsidy** | Has `NR_ACASubsidy` array in outputs | Field exists in `Inputs` but **never used in engine** |
| **Survivor SS** | Not explicitly shown in the read code | Correctly takes the higher benefit — **better** |
| **Modularization** | Global variables, shared mutable state, no tests | Clean modules, Decimal precision, 19 test files — **much better** |
| **Config** | Excel named ranges, sheet cells | YAML files, dataclass validation — **better** |

### Summary
The Python code is architecturally far superior. It has correct SS taxation, clean module separation, Decimal precision, and a test framework. The primary regressions vs VBA are: missing IRMAA, missing post-65 conversion strategy, missing IRA penalty gate, and the double-count bug that causes conversions to be roughly half the intended amount.

The `ideas.txt` file in the VBA repo is a detailed self-critique of the VBA model's own flaws (noted by the VBA author). The Python rewrite already addresses several of those critiques (proper SS taxation, structured phase logic, no global state). The Python code should be treated as the target architecture, not the VBA.

---

## 9. Recommended Next Small Task

**Fix the three broken test files before touching any engine logic.**

The test suite is the primary quality gate for subsequent fixes. Right now, 3 of 19 test files will always fail, masking any real regressions. These are mechanical renames — no algorithmic judgment required.

**Step 1:** In `test_magi_and_medicare.py` and `test_rmd.py`:
- Replace every `row["Your_Age"]` → `row["Person1_Age"]`
- Replace every `cfg.birth_year_you` → `cfg.birth_year_person1`
- Replace `row["Your_Age"]` comparisons for person2 with `row["Person2_Age"]` where applicable

**Step 2:** In `test_invariants.py`:
- Either move the `audit.py` tool into the tracked package (e.g., `retireplan/audit.py`) or replace it with an inline invariant check

**Step 3:** Fix `examples/sample_inputs.yaml` to add `start_year: 2025` under the `spending:` key (or update the loader to also accept `start_year` at the top level)

Once the test suite is clean and all 19 tests pass, the next task with the highest financial impact is:

> **Fix the Roth conversion double-count** in `engine/core.py:292`:  
> Change `ira_ordinary=float(rmd + draw_ira + conv)` to `ira_ordinary=float(rmd + draw_ira)`.

This single-character-group change will double the Roth conversion amounts in pre-ACA years, increasing IRA depletion, reducing future RMD exposure, and aligning MAGI calculations with what `test_magi_calculation` actually tests for.
