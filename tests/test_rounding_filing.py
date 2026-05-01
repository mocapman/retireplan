from retireplan import inputs
from retireplan.engine.core import run_plan


def test_filing_status_consistency():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for row in rows:
        p1_alive = row["Person1_Age"] <= cfg.final_age_person1
        p2_alive = row["Person2_Age"] <= cfg.final_age_person2
        expected = "MFJ" if (p1_alive and p2_alive) else "Single"
        assert row["Filing"] == expected, (
            f"Year {row['Year']}: expected {expected}, got {row['Filing']}"
        )


def test_account_balances_sum_to_total():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for row in rows:
        total = row["IRA_Balance"] + row["Brokerage_Balance"] + row["Roth_Balance"]
        assert abs(total - row["Total_Assets"]) <= 1, (
            f"Year {row['Year']}: Total_Assets {row['Total_Assets']} != sum {total}"
        )


def test_standard_deduction_inflation():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for row in rows[1:]:  # year 1 has Std_Deduction=0 hardcoded
        years_since_start = row["Year"] - cfg.start_year
        base = cfg.standard_deduction_base / 2 if row["Filing"] == "Single" else cfg.standard_deduction_base
        expected = round(base * (1 + cfg.inflation) ** years_since_start)
        assert abs(row["Std_Deduction"] - expected) < 100, (
            f"Year {row['Year']}: Std_Deduction {row['Std_Deduction']} vs expected {expected}"
        )


def test_magi_nonnegative():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for row in rows[1:]:  # skip year 1
        assert row["MAGI"] >= 0, f"Year {row['Year']}: MAGI should be non-negative"


def test_rmd_starts_at_rmd_start_age():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for row in rows[1:]:  # skip year 1 (hardcoded to 0 regardless)
        if row["Person1_Age"] < cfg.rmd_start_age:
            assert row["RMD"] == 0, (
                f"Year {row['Year']}: RMD should be 0 before age {cfg.rmd_start_age}"
            )
