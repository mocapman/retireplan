from retireplan import schema
from retireplan.engine.core import run_plan
from retireplan.inputs import load_yaml
from tests.test_run_plan_baseline import minimal_two_person_config


def assert_all_rows_contain_schema_keys(rows):
    expected_keys = set(schema.keys())

    assert rows
    for row in rows:
        missing_keys = expected_keys - set(row.keys())
        assert missing_keys == set()


def test_minimal_run_plan_rows_contain_all_schema_keys():
    rows = run_plan(minimal_two_person_config())

    assert_all_rows_contain_schema_keys(rows)


def test_default_config_run_plan_rows_contain_all_schema_keys():
    cfg = load_yaml("retireplan/default_config.yaml")
    rows = run_plan(cfg)

    assert_all_rows_contain_schema_keys(rows)


def test_brokerage_diagnostic_fields_are_schema_export_fields_not_gui_default():
    diagnostic_fields = {
        "Brokerage_Cash_Used",
        "Brokerage_Holdings_Sold",
        "Brokerage_Basis_Used",
        "Brokerage_Gain_Ratio",
        "Brokerage_Capital_Gains",
    }

    assert diagnostic_fields.issubset(set(schema.keys()))
    assert diagnostic_fields.isdisjoint(set(schema.visible_keys()))


def test_tax_diagnostic_fields_are_schema_export_fields_not_gui_default():
    diagnostic_fields = {
        "Federal_Tax",
        "Filing_Status_Used",
        "Federal_Standard_Deduction_Used",
        "Federal_Tax_Bracket_Set_Used",
        "Federal_Taxable_Income_Before_Deduction",
        "Federal_Taxable_Income_After_Deduction",
        "Estimated_State_Taxable_Income",
        "Estimated_State_Tax",
        "IRA_Taxable_Income",
        "IRA_RMD_Taxable_Income",
        "IRA_Extra_Draw_Taxable_Income",
        "RMD_Gross",
        "RMD_Used_For_Spending",
        "RMD_Surplus_To_Brokerage",
        "Roth_Conversion_Taxable_Income",
        "SS_Person1_Gross",
        "SS_Person2_Gross",
        "SS_Total_Gross",
        "SS_Taxable_Amount",
        "SS_Nontaxable_Amount",
        "SS_Survivor_Adjustment",
        "SS_Filing_Status_Used",
        "Survivor_Year",
        "Living_Person",
        "Widow_Tax_Mode",
        "Survivor_Spending_Used",
        "Survivor_Filing_Status_Used",
        "Survivor_Standard_Deduction_Used",
        "IRA_Balance_Start_Of_Year",
        "IRA_Balance_End_Of_Year",
    }

    assert diagnostic_fields.issubset(set(schema.keys()))
    assert diagnostic_fields.isdisjoint(set(schema.visible_keys()))
