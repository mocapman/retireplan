# RetirePlan — Dependency Audit

**Date:** 2026-05-01  
**Scope:** All production Python files. Test files excluded.  
**Type:** Read-only analysis — no code changes made.

---

## Files Analyzed (30)

```
retireplan/__init__.py
retireplan/inputs.py
retireplan/schema.py
retireplan/gui.py
retireplan/engine/__init__.py
retireplan/engine/accounts.py
retireplan/engine/core.py
retireplan/engine/policy.py
retireplan/engine/precision.py
retireplan/engine/rmd.py
retireplan/engine/social_security.py
retireplan/engine/spending.py
retireplan/engine/taxes.py
retireplan/engine/timeline.py
retireplan/engine/utils.py
retireplan/engine/year.py
retireplan/gui/__init__.py
retireplan/gui/__main__.py
retireplan/gui/config_manager.py
retireplan/gui/file_operations.py
retireplan/gui/input_panel.py
retireplan/gui/main_window.py
retireplan/gui/results_display.py
tools/audit.py
tools/diagnostics.py
tools/doctor.py
tools/projections.py
tools/refactor_to_canon.py
tools/scenarios.py
```

---

## File-by-File Analysis

---

### `retireplan/__init__.py`
- **Imports:** nothing (empty file)
- **Exports:** nothing
- **Called by:** (package marker only)
- **Calls:** nothing

---

### `retireplan/inputs.py`
- **Imports:** `dataclasses.dataclass`, `typing.Optional/Literal`, `yaml`
- **Exports:** `Inputs` (dataclass), `Filing` (type alias), `DrawOrder` (type alias), `load_yaml()`, `validate()`
- **Called by:** `gui/main_window.py`, `tools/audit.py`, `tools/diagnostics.py`, `tools/scenarios.py`, all test files
- **Calls:** `yaml.safe_load()`, `validate()` (internal)

---

### `retireplan/schema.py`
- **Imports:** `typing.List/Dict/Any`
- **Exports:** `COLUMNS` (constant), `keys()`, `labels()`, `visible_keys()`, `columns()`
- **Called by:** `tools/projections.py`, `tools/scenarios.py`, `gui/file_operations.py`
- **Calls:** nothing

---

### `retireplan/gui.py`
- **Imports:** `retireplan.gui.main_window.main`
- **Exports:** `main` (re-export)
- **Called by:** nothing (entry point only — `__main__` block at bottom)
- **Calls:** `main_window.main()`
- **Note:** Backward-compatibility wrapper. Not imported by any other project file.

---

### `retireplan/engine/__init__.py`
- **Imports:** nothing (empty file)
- **Exports:** nothing
- **Called by:** nothing
- **Calls:** nothing

---

### `retireplan/engine/accounts.py`
- **Imports:** `dataclasses.dataclass`, `decimal.Decimal`, `typing.Tuple`
- **Exports:** `Accounts` (class), `withdraw_with_order()`, `parse_draw_order()`
- **Called by:** `engine/core.py` — imports `withdraw_with_order`, `parse_draw_order` only
- **Calls:** nothing external

---

### `retireplan/engine/core.py`
- **Imports:** `typing`, `decimal`, `engine/policy.rmd_factor`, `engine/social_security.ss_for_year`, `engine/spending.spend_target` + `infl_factor_decimal`, `engine/taxes.compute_tax_magi`, `engine/timeline.make_years`, `engine/precision.round_dollar` + `round_percent` + `round_year`, `engine/accounts.withdraw_with_order` + `parse_draw_order`
- **Exports:** `run_plan()`
- **Called by:** `gui/main_window.py`, `tools/audit.py`, `tools/diagnostics.py`, `tools/scenarios.py`, all test files that run the engine
- **Calls:** `make_years()`, `spend_target()`, `infl_factor_decimal()`, `ss_for_year()`, `rmd_factor()`, `withdraw_with_order()`, `parse_draw_order()`, `compute_tax_magi()`, `round_dollar()`, `round_year()`

---

### `retireplan/engine/policy.py`
- **Imports:** nothing (stdlib only)
- **Exports:** `FED_BRACKETS` (constant), `SS_THRESHOLDS` (constant), `_UNIFORM_LIFETIME` (private constant), `rmd_factor()`
- **Called by:** `engine/taxes.py` (imports `FED_BRACKETS`, `SS_THRESHOLDS`), `engine/core.py` (imports `rmd_factor`)
- **Calls:** nothing

---

### `retireplan/engine/precision.py`
- **Imports:** `typing`, `decimal.Decimal/ROUND_HALF_UP`, `math`
- **Exports:** `DOLLAR_PRECISION`, `PERCENT_PRECISION`, `YEAR_PRECISION`, `COUNT_PRECISION`, `round_dollar()`, `round_percent()`, `round_year()`, `round_count()`, `ROUNDING_RULES`, `round_value()`, `round_row()`, `round_rows()`
- **Called by:** `engine/core.py` (imports `round_dollar`, `round_percent`, `round_year`), `gui/file_operations.py` (imports `round_row`)
- **Calls:** nothing external

---

### `retireplan/engine/rmd.py`
- **Imports:** nothing (empty file)
- **Exports:** nothing
- **Called by:** nothing
- **Calls:** nothing

---

### `retireplan/engine/social_security.py`
- **Imports:** nothing (stdlib only)
- **Exports:** `ss_for_year()`
- **Called by:** `engine/core.py`
- **Calls:** nothing

---

### `retireplan/engine/spending.py`
- **Imports:** `decimal.Decimal`
- **Exports:** `calculate_base_target_spend()`, `apply_phase_percentage()`, `apply_inflation_adjustment()`, `apply_survivor_adjustment()`, `calculate_inflation_factor()`, `calculate_spending_target()`, `infl_factor()` (legacy float), `infl_factor_decimal()`, `spend_target()`
- **Called by:** `engine/core.py` — imports `spend_target` and `infl_factor_decimal` only
- **Calls:** all internal

---

### `retireplan/engine/taxes.py`
- **Imports:** `typing.Tuple`, `engine/policy.FED_BRACKETS` + `SS_THRESHOLDS`
- **Exports:** `progressive_tax()`, `ss_taxable_amount()`, `compute_tax_magi()`
- **Called by:** `engine/core.py` (imports `compute_tax_magi`)
- **Calls:** `progressive_tax()` (internal), `ss_taxable_amount()` (internal), `FED_BRACKETS`, `SS_THRESHOLDS`

---

### `retireplan/engine/timeline.py`
- **Imports:** `dataclasses.dataclass`
- **Exports:** `YearCtx` (dataclass), `make_years()`
- **Called by:** `engine/core.py`
- **Calls:** nothing external

---

### `retireplan/engine/utils.py`
- **Imports:** `datetime.datetime`, `pathlib.Path`
- **Exports:** `generate_filename()`
- **Called by:** nothing
- **Calls:** nothing external

---

### `retireplan/engine/year.py`
- **Imports:** nothing (empty file)
- **Exports:** nothing
- **Called by:** nothing
- **Calls:** nothing

---

### `retireplan/gui/__init__.py`
- **Imports:** `.main_window.RetirePlanApp`
- **Exports:** `RetirePlanApp`
- **Called by:** `import retireplan.gui` (package import)
- **Calls:** nothing

---

### `retireplan/gui/__main__.py`
- **Imports:** `.main_window.RetirePlanApp`
- **Exports:** nothing (entry point)
- **Called by:** `python -m retireplan.gui`
- **Calls:** `RetirePlanApp()`

---

### `retireplan/gui/config_manager.py`
- **Imports:** `typing.Dict/Any`
- **Exports:** `ConfigManager` (class with `config_to_dict()`, `update_config_from_dict()`)
- **Called by:** `gui/main_window.py`
- **Calls:** nothing external

---

### `retireplan/gui/file_operations.py`
- **Imports:** `csv`, `yaml`, `tkinter.messagebox`, `tkinter.filedialog`, `datetime`, `pathlib.Path`, `retireplan.schema`, `engine/precision.round_row`
- **Exports:** `FileOperations` (class)
- **Called by:** `gui/main_window.py`
- **Calls:** `schema.keys()`, `schema.labels()`, `round_row()`

---

### `retireplan/gui/input_panel.py`
- **Imports:** `tkinter`, `ttkbootstrap`, `tkinter.messagebox`, `typing.Callable/Optional`
- **Exports:** `format_currency()`, `strip_currency()`, `format_percent()`, `strip_percent()`, `percent_to_float()`, `float_to_percent()`, `InputPanel` (class)
- **Called by:** `gui/main_window.py`
- **Calls:** nothing external (tkinter only)

---

### `retireplan/gui/main_window.py`
- **Imports:** `os`, `tkinter`, `ttkbootstrap`, `datetime`, `yaml`, `retireplan.inputs`, `retireplan.engine.core.run_plan`, `.input_panel.InputPanel`, `.results_display.ResultsDisplay`, `.file_operations.FileOperations`, `.config_manager.ConfigManager`
- **Exports:** `RetirePlanApp` (class), `main()`
- **Called by:** `gui/__init__.py`, `gui/__main__.py`, `gui.py`
- **Calls:** `inputs.load_yaml()`, `run_plan()`, `InputPanel()`, `ResultsDisplay()`, `FileOperations()`, `ConfigManager()`

---

### `retireplan/gui/results_display.py`
- **Imports:** `tkinter`, `ttkbootstrap`, `tksheet.Sheet`, `typing.List`, `tools.projections.to_2d_for_table`
- **Exports:** `ResultsDisplay` (class), `format_currency()` (module-level helper)
- **Called by:** `gui/main_window.py`
- **Calls:** `to_2d_for_table()`

---

### `tools/audit.py`
- **Imports:** `dataclasses.dataclass`, `typing`, `retireplan.inputs`, `engine/core.run_plan`
- **Exports:** `AuditSummary` (dataclass), `audit_rows_against_cfg()`, `main()`
- **Called by:** nothing (standalone script)
- **Calls:** `inputs.load_yaml()`, `run_plan()`

---

### `tools/diagnostics.py`
- **Imports:** `typing`, `retireplan.inputs`, `engine/core.run_plan`
- **Exports:** `main()`, `_rows_early_years()` (private)
- **Called by:** nothing (standalone script)
- **Calls:** `inputs.load_yaml()`, `run_plan()`

---

### `tools/doctor.py`
- **Imports:** `platform`, `sys`, `importlib.metadata`, `pathlib.Path`
- **Exports:** `main()`
- **Called by:** nothing (standalone script)
- **Calls:** references `retireplan.theme` and `PySimpleGUI` — both absent

---

### `tools/projections.py`
- **Imports:** `typing`, `pandas`, `retireplan.schema`
- **Exports:** `to_dataframe()`, `to_2d_for_table()`
- **Called by:** `gui/results_display.py` (imports `to_2d_for_table` only)
- **Calls:** `schema.keys()`, `schema.labels()`, `schema.visible_keys()`

---

### `tools/refactor_to_canon.py`
- **Imports:** `sys`, `re`, `pathlib.Path`
- **Exports:** `main()`, `iter_files()`, `apply_replacements()`
- **Called by:** nothing (one-shot migration script, presumably already run)
- **Calls:** filesystem read/write

---

### `tools/scenarios.py`
- **Imports:** `pathlib.Path`, `typing`, `csv`, `retireplan.inputs`, `retireplan.schema`, `engine/core.run_plan`
- **Exports:** `main()`, `_print_cut()` (private), `_write_csv()` (private)
- **Called by:** nothing (standalone script)
- **Calls:** `inputs.load_yaml()`, `run_plan()`, `schema.keys()`, `schema.labels()`

---

## Complete Call Chain

```
USER INPUT (YAML file)
  └── inputs.load_yaml()
        ├── yaml.safe_load()
        └── validate()

GUI PATH:
  gui/__main__.py  or  gui.py  or  gui/__init__.py
    └── main_window.RetirePlanApp.__init__()
          ├── inputs.load_yaml()
          ├── FileOperations(app)
          ├── ConfigManager()
          └── build_ui()
                ├── InputPanel()
                └── ResultsDisplay()

  User edits → InputPanel.apply_changes()
    └── main_window.run_plan()
          ├── input_panel.get_config_dict()
          ├── config_manager.update_config_from_dict()
          └── engine/core.run_plan(cfg)
                ├── parse_draw_order()            [accounts.py]
                ├── make_years()                  [timeline.py]
                └── per year:
                      ├── infl_factor_decimal()   [spending.py]
                      │     └── calculate_inflation_factor()
                      ├── spend_target()          [spending.py]
                      │     └── calculate_spending_target()
                      │           ├── calculate_base_target_spend()
                      │           ├── apply_phase_percentage()
                      │           ├── apply_inflation_adjustment()
                      │           └── apply_survivor_adjustment()
                      ├── ss_for_year() x2        [social_security.py]
                      ├── rmd_factor()            [policy.py]
                      │     └── _UNIFORM_LIFETIME table
                      ├── withdraw_with_order()   [accounts.py]
                      ├── compute_tax_magi()      [taxes.py]
                      │     ├── ss_taxable_amount()
                      │     │     └── SS_THRESHOLDS   [policy.py]
                      │     └── progressive_tax()
                      │           └── FED_BRACKETS    [policy.py]
                      └── round_dollar() / round_year()  [precision.py]

  run_plan() → list[dict]
    └── results_display.load_results(rows)
          └── to_2d_for_table(rows)  [tools/projections.py]
                └── schema.keys() / labels() / visible_keys()

CLI TOOL PATH:
  tools/audit.py      → inputs.load_yaml() → run_plan()
  tools/diagnostics.py→ inputs.load_yaml() → run_plan()
  tools/scenarios.py  → inputs.load_yaml() → run_plan()
  tools/doctor.py     → BROKEN (see Undefined section)
```

---

## Flags

### ORPHANED — Exported but never imported or called anywhere

| Symbol | File | Detail |
|---|---|---|
| `generate_filename()` | `engine/utils.py` | Defined and exported. Zero callers anywhere in the project. |
| `Accounts` class | `engine/accounts.py` | Defined and exported. Never instantiated or imported. A TODO comment in the file acknowledges this. Only `withdraw_with_order()` and `parse_draw_order()` from this file are used. |
| `calculate_base_target_spend()` | `engine/spending.py` | Called only internally by `calculate_spending_target()`. Never imported outside the file. |
| `apply_phase_percentage()` | `engine/spending.py` | Same — internal only. |
| `apply_inflation_adjustment()` | `engine/spending.py` | Same — internal only. |
| `apply_survivor_adjustment()` | `engine/spending.py` | Same — internal only. |
| `calculate_inflation_factor()` | `engine/spending.py` | Same — internal only. |
| `calculate_spending_target()` | `engine/spending.py` | Same — internal only. Only `spend_target()` and `infl_factor_decimal()` are imported by `core.py`. |
| `infl_factor()` | `engine/spending.py` | Legacy float version. Never imported anywhere. Marked deprecated in docstring. |
| `round_count()` | `engine/precision.py` | Defined and exported. Never imported anywhere. |
| `round_value()` | `engine/precision.py` | Defined and exported. Never imported anywhere. |
| `round_rows()` | `engine/precision.py` | Defined and exported. Never imported anywhere. |
| `ROUNDING_RULES` | `engine/precision.py` | Defined and exported. Never imported anywhere. |
| `DOLLAR_PRECISION`, `PERCENT_PRECISION`, `YEAR_PRECISION`, `COUNT_PRECISION` | `engine/precision.py` | Four constants defined and exported. Never imported anywhere. |
| `round_percent()` | `engine/precision.py` | Imported by `engine/core.py` in the import statement but never actually called in `core.py`. |
| `to_dataframe()` | `tools/projections.py` | Defined and exported. Never imported anywhere. Only `to_2d_for_table()` is used. |

---

### UNDEFINED — Called or imported but not found in the codebase

| Symbol | Referenced in | Detail |
|---|---|---|
| `retireplan.theme` | `tools/doctor.py` | File does not exist. `doctor.py` will raise `ImportError` at runtime when it reaches this import. |
| `retireplan.theme` | `tests/test_env.py` | Same missing file. Handled gracefully with `try/except` + `pytest.skip`. |
| `PySimpleGUI` | `tools/doctor.py` | Not installed. `doctor.py` itself reports it as `NOT INSTALLED`. |
| Legacy file paths in `tools/doctor.py` `FILES` list | `tools/doctor.py` | Nine hardcoded paths reflect the pre-refactor flat layout and will all show `MISSING` when `doctor.py` runs: `retireplan/policy.py`, `retireplan/core.py`, `retireplan/accounts.py`, `retireplan/taxes.py`, `retireplan/social_security.py`, `retireplan/spending.py`, `retireplan/projections.py`, `retireplan/io_csv.py`, `retireplan/theme.py` |

---

### DEAD — Files that exist but are never referenced

| File | Reason |
|---|---|
| `retireplan/engine/rmd.py` | Empty file (1 line). Never imported anywhere. |
| `retireplan/engine/year.py` | Empty file (1 line). Never imported anywhere. |
| `retireplan/engine/utils.py` | Has content but `generate_filename()` is never called. Zero imports. |
| `tools/doctor.py` | Standalone script with stale content. Checks for packages and file paths that no longer reflect the current project structure. Will produce entirely wrong output if run. |
| `tools/refactor_to_canon.py` | One-shot migration script. Presumably already run. Keeping it creates confusion about whether it is safe to run again. |

---

### CIRCULAR IMPORTS

None. The dependency graph is strictly acyclic:

```
gui → engine/core → {policy, social_security, spending,
                      taxes, timeline, precision, accounts}
engine/taxes → engine/policy
```

All edges point inward toward leaf modules. No cycles.

---

### CROSS-LAYER ANOMALY

`gui/results_display.py` imports from the `tools/` directory:

```python
from tools.projections import to_2d_for_table
```

`tools/` has no `__init__.py` and is not a package. This import works only when the project root is on `sys.path` (which it is at runtime via the launch scripts). It is a structural violation: the GUI layer has a hard compile-time dependency on a script directory.

---

## Files to Delete

The following files can be deleted without breaking any other code. Each has been confirmed to have zero callers and zero dependents.

| File | Reason to Delete |
|---|---|
| `retireplan/engine/rmd.py` | Empty. Never imported. Placeholder that was never filled in. |
| `retireplan/engine/year.py` | Empty. Never imported. No purpose. |
| `retireplan/engine/utils.py` | Only export (`generate_filename`) is called nowhere. Entire file is dead code. |
| `tools/doctor.py` | Stale. References packages not installed, a module that does not exist (`theme`), and nine file paths that moved during the engine refactor. Produces incorrect output if run. |
| `tools/refactor_to_canon.py` | One-shot migration script. Presumably already run. Running it again would be destructive. No ongoing value. |
