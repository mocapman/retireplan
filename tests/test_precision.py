from retireplan import inputs
from retireplan.engine.core import run_plan


def test_decimal_precision():
    """Test that run_plan outputs integer dollar amounts and integer ages/years"""
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)

    monetary_columns = [
        "Total_Spend",
        "Taxes_Due",
        "Cash_Events",
        "Target_Spend",
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
    integer_columns = ["Year", "Person1_Age", "Person2_Age"]

    for row in rows:
        for key in monetary_columns:
            assert isinstance(
                row[key], int
            ), f"{key} should be int after run_plan, got {type(row[key])}"
        for key in integer_columns:
            assert isinstance(
                row[key], int
            ), f"{key} should be int, got {type(row[key])}"
