# PROJECT_AUDIT_2.md
## RetirePlan Python — Targeted Follow-Up Audit
**Date:** 2026-04-30
**Auditor:** Claude (automated review)
**Scope:** Four targeted questions following the first audit and a reported cleanup session

---

## Q1. What Did the Cleanup Session Commit — Is It Clean or Did It Introduce Problems?

**Nothing was committed to git.** The repository still has exactly one commit (`416171e Initial commit`), which only added `README.md` and `.gitattributes`. The `tests/` and `examples/` directories are excluded from git per `.gitignore`, so no test changes can be committed.

The cleanup session made four clean on-disk fixes and left one set of problems in the engine:

### Clean fixes (tests, examples — not in git)
| File | What Changed | Assessment |
|------|-------------|------------|
| `tests/test_magi_and_medicare.py` | `Your_Age` → `Person1_Age`; `birth_year_you` → `birth_year_person1` | Clean rename |
| `tests/test_rmd.py` | `birth_year_you` → `birth_year_person1` | Clean rename |
| `tests/test_invariants.py` | Removed `from tools.audit import audit_rows_against_cfg`; inlined the function | Clean fix |
| `examples/sample_inputs.yaml` | Added `start_year: 2025` under `spending:` section | Clean fix |

### Problems introduced in `engine/core.py`
The session deleted some duplicate functions (good), but left behind comment debris that violates CLAUDE.md:

**Lines 32–49** — Two large comment blocks explain what was removed and why, using the exact structure CLAUDE.md prohibits:
```python
# Remove duplicate inflation function - use infl_factor_decimal from spending.py
# TODO: Further consolidate inflation utilities once Decimal adoption is complete
#
# MODULARIZATION DECISION: ...
# RATIONALE: ...
# FUTURE: ...
```
Both blocks contain `TODO` markers (explicitly banned by CLAUDE.md), and both describe removed code rather than present code (what the code does). These should be deleted entirely.

**Line 3** — The module docstring contains a stale Linux path (`/home/runner/work/retireplan/retireplan/retireplan/core.py`). This is a Windows project; the path is a leftover from an automated runner environment and is misleading.

---

## Q2. Which Original Audit Issues Are Now Resolved?

Four of the issues from Section 7.8 and Section 9 are resolved:

| Original Issue | Status |
|---------------|--------|
| `test_magi_and_medicare.py` — `row["Your_Age"]` KeyError | **RESOLVED** |
| `test_rmd.py` — `cfg.birth_year_you` AttributeError | **RESOLVED** |
| `test_invariants.py` — `from tools.audit import ...` ModuleNotFoundError | **RESOLVED** |
| `examples/sample_inputs.yaml` — `start_year` in wrong section, KeyError on load | **RESOLVED** |

No engine bugs were fixed. The four resolutions bring three previously dead test files back to life and fix the YAML loader crash that blocked all tests using `sample_inputs.yaml`.

---

## Q3. Remaining Issues — Priority Order

### P1 — Roth Conversion Double-Count Bug (HIGH, financial math error)
**Location:** `engine/core.py:293`

```python
ira_ordinary=float(rmd + draw_ira + conv),   # conv included here
roth_conversion=float(conv),                   # and again here
```

`compute_tax_magi` adds `ira_ordinary + roth_conversion` internally, so `conv` is counted twice in the MAGI calculation. The iterative solver compensates by converging to `conv ≈ (target_magi − ss_tax) / 2` instead of the correct value. **Roth conversions run at roughly half the intended rate every pre-ACA year.** IRA drains too slowly; future RMDs will be larger than planned.

Fix: change `ira_ordinary=float(rmd + draw_ira + conv)` to `ira_ordinary=float(rmd + draw_ira)`. One value, one line. No other changes needed.

Note: `test_magi_conversion.py` and `test_magi_and_medicare.py` both check only that MAGI is near the inflated target — which appears correct even with the bug (the solver converges). Neither test currently catches that conversion amounts are half of what they should be.

---

### P2 — Standard Deduction Not Adjusted for Filing Status (HIGH, financial math error)
**Location:** `engine/core.py:188`

```python
std_ded = Decimal(str(cfg.standard_deduction_base)) * infl
```

`filing_status` is correctly set to `"Single"` when one spouse dies (line 192), but `std_ded` is never adjusted for it. The user-configured `standard_deduction_base` is the MFJ value (~$31,500 in sample config). For Single years it should be approximately half (~$15,750). Every survivor year understates federal tax by roughly $2,000–$4,000. `test_rounding_filing.py:27` (`test_standard_deduction_inflation`) confirms inflation scaling but does not test the MFJ/Single split.

---

### P3 — TODO Comments Left in Engine Code (MEDIUM, process violation)
**Location:** `engine/core.py:32–49`

Two multi-line comment blocks with `TODO` markers explain deleted code. CLAUDE.md explicitly prohibits TODO comments. These should be deleted; the fact that code was moved to `accounts.py` and `spending.py` is self-evident from the imports and does not need an explanation in `core.py`.

Also: `engine/accounts.py:213` — `parse_draw_order` docstring contains `TODO: Add validation ...`. Same violation.

---

### P4 — `parse_draw_order` Has No Validation (MEDIUM, silent failure risk)
**Location:** `engine/accounts.py:200–217`

The function returns an unvalidated tuple of any length. A draw order string with fewer or more than three accounts silently produces a wrong-length tuple. `withdraw_with_order` iterates it without length checking. The third account would simply never be drawn, with no error. The TODO acknowledges this but does not fix it.

---

### P5 — ACA Subsidy Field Loaded and Validated but Never Used (MEDIUM, missing calculation)
**Location:** `inputs.py:62`, `engine/core.py` — absent

`aca_subsidy_annual` is a valid `Inputs` field, is loaded from YAML, has a GUI reference in `config_manager.py`, and appears in the sample config. It is never referenced in `core.py` or any engine module. The output table has no `ACA_Subsidy` column. For a household near the $85k MAGI cliff, this can represent $10,000–$20,000/year of benefit that is modeled as zero.

---

### P6 — `results_display.py` Imports from `tools/` (MEDIUM, clean-install breakage)
**Location:** `retireplan/gui/results_display.py:9`

```python
from tools.projections import to_2d_for_table
```

`tools/` is excluded from git per `.gitignore`. The GUI will raise `ModuleNotFoundError` on any clean install where `tools/` is absent. The function is used to convert engine output to a 2D list for the table widget — it is not optional. This was pre-existing and not introduced by the cleanup session, but was not caught by the first audit (which focused on test files). The fix is to move `to_2d_for_table` into the tracked package (e.g., `retireplan/gui/` or `retireplan/engine/`).

---

### P7 — Empty Stub Files (LOW, dead/misleading code)
**Location:** `engine/rmd.py`, `engine/year.py`

Both files are 1-line stubs (empty except for a newline). They are importable but do nothing. They were presumably placeholders for planned modules whose logic ended up in `core.py` and `policy.py`. They create the false impression that RMD and year logic live there.

---

### P8 — `Accounts` Class Is Dead Code (LOW, maintenance confusion)
**Location:** `engine/accounts.py:22–122`

The `Accounts` dataclass with `withdraw_sequence()` and `apply_growth()` uses `float` arithmetic and is never instantiated by `core.py`. The engine uses `withdraw_with_order()` (Decimal). The class is unreachable production code that could mislead someone reading `accounts.py`.

---

### P9 — Stale Runner Path in `core.py` Docstring (LOW, misleading comment)
**Location:** `engine/core.py:3`

The module docstring contains `/home/runner/work/retireplan/retireplan/retireplan/core.py` — a Linux CI path, not the Windows project path. The docstring appears to have been generated or modified by an automated tool.

---

### Not-Yet-Implemented Features (Out of Scope for Bug Fixes)
These were noted in the first audit as known gaps, not bugs. Still absent:
- IRMAA (Medicare Part B/D surcharges)
- Post-65 Roth conversion strategy
- IRA early withdrawal penalty gate (age < 59½)
- Capital gains tax on brokerage draws
- Tax bracket inflation indexing
- Person2 IRA / RMD modeling

---

## Q4. Single Highest-Value Next Task

**Fix the Roth conversion double-count bug in `engine/core.py:293`.**

Change:
```python
ira_ordinary=float(rmd + draw_ira + conv),
```
To:
```python
ira_ordinary=float(rmd + draw_ira),
```

This is a one-value change in one line with no ripple effects. It corrects the most consequential financial math error in the engine: Roth conversions running at half the intended rate in every pre-ACA year. Over a 10–15 year window before Medicare, the cumulative under-conversion is hundreds of thousands of dollars. The IRA balance at RMD age will be materially higher than the model reports, leading to underestimated future RMDs and taxes.

After this fix, add a test that asserts the conversion amount (not just the MAGI) is approximately equal to `target_magi − ss_taxable − rmd − draw_ira` to prevent regression.
