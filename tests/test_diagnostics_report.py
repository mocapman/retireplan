from retireplan.engine.core import run_plan
from tests.test_run_plan_baseline import minimal_two_person_config
from tools.diagnostics_report import build_diagnostic_report


def test_build_diagnostic_report_includes_current_math_fields():
    rows = run_plan(minimal_two_person_config())

    report = build_diagnostic_report(rows)

    for field in (
        "Year",
        "Person1_Age",
        "Person2_Age",
        "Filing",
        "Lifestyle",
        "Target_Spend",
        "Total_Spend",
        "Cash_Events",
        "Social_Security",
        "IRA_Draw",
        "Brokerage_Draw",
        "Brokerage_Cash_Used",
        "Brokerage_Holdings_Sold",
        "Brokerage_Basis_Used",
        "Brokerage_Gain_Ratio",
        "Brokerage_Capital_Gains",
        "Brokerage_MAGI_Income",
        "Roth_Draw",
        "Roth_Conversion",
        "RMD",
        "MAGI",
        "Target_MAGI",
        "MAGI_Remaining",
        "MAGI_Status",
        "ACA_Subsidy",
        "Std_Deduction",
        "Taxes_Due",
        "Shortfall",
        "IRA_Balance",
        "Brokerage_Balance",
        "Roth_Balance",
        "Total_Assets",
    ):
        assert field in report

    assert "2025 | 60 | 59 | MFJ | GoGo | 1000 | 1000" in report
    assert "2027 | 62 | 61 | MFJ | NoGo | 700 | 700" in report


def test_build_diagnostic_report_omits_fields_that_are_not_present():
    report = build_diagnostic_report([{"Year": 2025, "MAGI": 0}])

    assert report.splitlines()[0] == "Year | MAGI"
    assert "Taxes_Due" not in report
    assert "2025 | 0" in report


def test_build_diagnostic_report_handles_no_rows():
    assert build_diagnostic_report([]) == "No projection rows."
