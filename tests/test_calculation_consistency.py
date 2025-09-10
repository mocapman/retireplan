import os

from retireplan.inputs import load_yaml
from retireplan.engine.engine import run_plan
from retireplan.engine.taxes import ss_taxable_amount

# Load the sample inputs
yaml_path = os.path.join("examples", "sample_inputs.yaml")


def test_calculation_consistency():
    """Test that all calculations are internally consistent"""
    cfg = load_yaml(yaml_path)
    rows = run_plan(cfg)

    for i, row in enumerate(rows):
        # 1. Check that Total_Assets equals sum of account balances
        total_assets = row["Total_Assets"]
        sum_balances = (
            row["IRA_Balance"] + row["Brokerage_Balance"] + row["Roth_Balance"]
        )
        assert (
            abs(total_assets - sum_balances) <= 1
        ), f"Year {row['Year']}: Total_Assets doesn't match sum of account balances"

        # 2. Check that spending components add up
        total_spend = row["Total_Spend"]
        sum_components = row["Target_Spend"] + row["Taxes_Due"] + row["Cash_Events"]
        assert (
            abs(total_spend - sum_components) <= 1
        ), f"Year {row['Year']}: Total_Spend doesn't match sum of components"

        # 3. Check that income sources are consistent with spending
        total_income = (
            row["Social_Security"]
            + row["IRA_Draw"]
            + row["Brokerage_Draw"]
            + row["Roth_Draw"]
            + row["Roth_Conversion"]
            + row["RMD"]
        )

        # Allow $1 tolerance for rounding differences
        if total_income < total_spend - 1:
            assert (
                row["Shortfall"] > 0
            ), f"Year {row['Year']}: Income {total_income} < Spend {total_spend} but no shortfall"
        elif total_income >= total_spend:
            assert (
                row["Shortfall"] == 0
            ), f"Year {row['Year']}: Income {total_income} >= Spend {total_spend} but shortfall {row['Shortfall']}"


def test_account_growth_consistency():
    """Test that account balances grow at the expected rates"""
    cfg = load_yaml(yaml_path)
    rows = run_plan(cfg)

    for i in range(1, len(rows)):
        prev = rows[i - 1]
        curr = rows[i]

        # Check IRA growth (accounting for draws and conversions)
        expected_ira = (
            prev["IRA_Balance"] - curr["IRA_Draw"] - curr["Roth_Conversion"]
        ) * (1 + cfg.ira_growth)
        assert (
            abs(curr["IRA_Balance"] - expected_ira) <= 100
        ), f"Year {curr['Year']}: IRA balance doesn't match expected growth"

        # Check Brokerage growth (accounting for draws)
        expected_brokerage = (prev["Brokerage_Balance"] - curr["Brokerage_Draw"]) * (
            1 + cfg.brokerage_growth
        )
        assert (
            abs(curr["Brokerage_Balance"] - expected_brokerage) <= 100
        ), f"Year {curr['Year']}: Brokerage balance doesn't match expected growth"

        # Check Roth growth (accounting for draws and conversions)
        expected_roth = (
            prev["Roth_Balance"] - curr["Roth_Draw"] + curr["Roth_Conversion"]
        ) * (1 + cfg.roth_growth)
        assert (
            abs(curr["Roth_Balance"] - expected_roth) <= 100
        ), f"Year {curr['Year']}: Roth balance doesn't match expected growth"


def test_magi_calculation():
    """Test that MAGI is calculated correctly using the actual tax logic"""
    cfg = load_yaml(yaml_path)
    rows = run_plan(cfg)

    for row in rows:
        # Use the same logic as the engine to calculate MAGI
        other_ordinary = row["IRA_Draw"] + row["Roth_Conversion"] + row["RMD"]
        taxable_ss = ss_taxable_amount(
            ss_total=row["Social_Security"],
            other_ordinary=other_ordinary,
            filing=row["Filing"],
        )
        expected_magi = other_ordinary + taxable_ss

        # Allow for rounding differences
        assert (
            abs(row["MAGI"] - expected_magi) <= 1
        ), f"Year {row['Year']}: MAGI doesn't match expected calculation"
