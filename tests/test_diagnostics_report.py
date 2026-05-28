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
        "Federal_Tax",
        "Filing_Status_Used",
        "Federal_Standard_Deduction_Used",
        "Federal_Tax_Bracket_Set_Used",
        "Taxable_Income",
        "Ordinary_Income_Taxable",
        "Capital_Gains_Taxable",
        "Total_Taxable_Income_Before_Deduction",
        "Total_Taxable_Income_After_Deduction",
        "Federal_Taxable_Income_Before_Deduction",
        "Federal_Taxable_Income_After_Deduction",
        "Federal_Tax_On_Ordinary_Income",
        "Estimated_State_Taxable_Income",
        "Estimated_State_Tax",
        "IRA_Taxable_Income",
        "IRA_Draw_Taxable_Income",
        "IRA_RMD_Taxable_Income",
        "IRA_Extra_Draw_Taxable_Income",
        "RMD_Gross",
        "RMD_Used_For_Spending",
        "RMD_Surplus_To_Brokerage",
        "Roth_Conversion_Gross",
        "Roth_Conversion_Taxable_Income",
        "Roth_Conversion_MAGI_Income",
        "MAGI",
        "Target_MAGI",
        "MAGI_Remaining",
        "MAGI_Status",
        "MAGI_IRA_Draws",
        "MAGI_RMD",
        "MAGI_Roth_Conversions",
        "MAGI_Brokerage_Gains",
        "MAGI_Social_Security",
        "Brokerage_Taxable_Income",
        "SS_Person1_Gross",
        "SS_Person2_Gross",
        "SS_Total_Gross",
        "SS_Taxable_Amount",
        "SS_Nontaxable_Amount",
        "SS_Included_In_MAGI",
        "SS_Survivor_Adjustment",
        "SS_Filing_Status_Used",
        "ACA_Subsidy",
        "Std_Deduction",
        "Survivor_Year",
        "Living_Person",
        "Widow_Tax_Mode",
        "Survivor_Spending_Used",
        "Survivor_Filing_Status_Used",
        "Survivor_Standard_Deduction_Used",
        "IRA_Balance_Start_Of_Year",
        "IRA_Total_Taxable_Income",
        "IRA_Balance_End_Of_Year",
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
