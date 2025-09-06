# test_precision.py
from decimal import Decimal
from retireplan import inputs
from retireplan.engine import run_plan
from retireplan.precision import round_row


def test_decimal_precision():
    """Test that monetary calculations use Decimal precision and rounding works correctly"""
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)

    # Columns that should be Decimal (monetary values)
    decimal_columns = [
        "Total_Spend",
        "Taxes_Due",
        "Cash_Events",
        "Base_Spend",
        "Social_Security",
        "IRA_Draw",
        "Brokerage_Draw",
        "Roth_Draw",
        "Roth_Conversion",
        "RMD",
        "MAGI",
        "Std_Deduction",
        "IRA_Balance",
        "Brokerage_Balance",
        "Roth_Balance",
        "Total_Assets",
        "Shortfall",
    ]

    # Columns that should be integers
    integer_columns = ["Year", "Your_Age", "Spouse_Age"]

    # Check that monetary values are Decimal before rounding
    for row in rows:
        for key, value in row.items():
            if key in decimal_columns:
                assert isinstance(
                    value, Decimal
                ), f"Value for {key} should be Decimal, got {type(value)}"
            elif key in integer_columns:
                assert isinstance(
                    value, int
                ), f"Value for {key} should be int, got {type(value)}"

    # Check that rounding works correctly
    rounded_rows = [round_row(row) for row in rows]
    for rounded_row in rounded_rows:
        for key, value in rounded_row.items():
            if key in integer_columns:
                assert (
                    isinstance(value, int) or value is None
                ), f"{key} should be int after rounding"
            elif key in decimal_columns:
                assert (
                    isinstance(value, int) or value is None
                ), f"{key} should be int after rounding (dollar amounts)"
