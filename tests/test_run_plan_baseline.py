from retireplan.engine.core import run_plan
from retireplan.inputs import Inputs
from retireplan import schema


def minimal_two_person_config() -> Inputs:
    return Inputs(
        birth_year_person1=1965,
        birth_year_person2=1966,
        final_age_person1=62,
        final_age_person2=61,
        filing_status="MFJ",
        balances_brokerage=10000,
        brokerage_cash=0,
        brokerage_cost_basis=0,
        brokerage_unrealized_gain=0,
        balances_roth=5000,
        balances_ira=20000,
        start_year=2025,
        year1_spend=1000,
        year1_cash_events=0,
        year1_brokerage_draw=1000,
        year1_ira_draw=0,
        year1_roth_draw=0,
        year1_roth_conversion=0,
        year1_magi_income=0,
        year1_magi_losses=0,
        year1_income_to_date=0,
        year1_projected_income=0,
        year1_capital_gains_to_date=0,
        year1_projected_capital_gains=0,
        year1_capital_losses_to_date=0,
        year1_projected_capital_losses=0,
        magi_income_ytd=0,
        magi_income_projected=0,
        magi_income_annual=0,
        magi_income_years=0,
        magi_gains_ytd=0,
        magi_gains_projected=0,
        magi_gains_annual=0,
        magi_gains_years=0,
        magi_losses_ytd=0,
        magi_losses_projected=0,
        magi_losses_annual=0,
        magi_losses_years=0,
        magi_conversions_ytd=0,
        magi_conversions_projected=0,
        magi_conversions_annual=0,
        magi_conversions_years=0,
        target_spend=1000,
        gogo_percent=100,
        slow_percent=80,
        nogo_percent=70,
        gogo_years=1,
        slow_years=1,
        survivor_percent=70,
        ss_person1_start_age=62,
        ss_person1_annual_at_start=0,
        ss_person2_start_age=62,
        ss_person2_annual_at_start=0,
        inflation=0,
        brokerage_growth=0,
        roth_growth=0,
        ira_growth=0,
        magi_target_base=0,
        standard_deduction_base=1000,
        estimated_state_deduction=0,
        estimated_state_tax_rate=0.0875,
        rmd_start_age=73,
        aca_end_age=65,
        aca_magi_floor=0,
        aca_magi_ceiling=1,
        aca_full_premium_monthly=0,
        aca_expected_subsidy_monthly=0,
        aca_subsidy_annual=None,
        draw_order="Brokerage, Roth, IRA",
    )


def test_run_plan_minimal_two_person_scenario_runs_three_years():
    rows = run_plan(minimal_two_person_config())

    assert len(rows) == 3
    assert [row["Year"] for row in rows] == [2025, 2026, 2027]
    assert [row["Person1_Age"] for row in rows] == [60, 61, 62]
    assert [row["Person2_Age"] for row in rows] == [59, 60, 61]
    assert [row["Lifestyle"] for row in rows] == ["GoGo", "Slow", "NoGo"]
    assert [row["Filing"] for row in rows] == ["MFJ", "MFJ", "MFJ"]


def test_run_plan_rows_include_current_schema_and_core_financial_fields():
    rows = run_plan(minimal_two_person_config())
    required_fields = set(schema.keys())

    for row in rows:
        assert required_fields.issubset(row.keys())

    core_fields = {
        "Total_Spend",
        "Target_Spend",
        "Taxes_Due",
        "MAGI",
        "Target_MAGI",
        "MAGI_Remaining",
        "MAGI_Status",
        "ACA_Subsidy",
        "Roth_Conversion",
        "Shortfall",
        "Brokerage_Balance",
        "Roth_Balance",
        "IRA_Balance",
        "Total_Assets",
    }
    for field in core_fields:
        assert field in rows[0]


def test_run_plan_baseline_spending_draws_and_balances_are_stable():
    rows = run_plan(minimal_two_person_config())

    assert [row["Target_Spend"] for row in rows] == [1000, 800, 700]
    assert [row["Total_Spend"] for row in rows] == [1000, 800, 700]
    assert [row["Brokerage_Draw"] for row in rows] == [1000, 800, 700]
    assert [row["Roth_Draw"] for row in rows] == [0, 0, 0]
    assert [row["IRA_Draw"] for row in rows] == [0, 0, 0]

    assert [row["Brokerage_Balance"] for row in rows] == [9000, 8200, 7500]
    assert [row["Roth_Balance"] for row in rows] == [5000, 5000, 5000]
    assert [row["IRA_Balance"] for row in rows] == [20000, 20000, 20000]
    assert [row["Total_Assets"] for row in rows] == [34000, 33200, 32500]


def test_run_plan_baseline_tax_magi_conversion_and_shortfall_outputs():
    rows = run_plan(minimal_two_person_config())

    assert [row["Taxes_Due"] for row in rows] == [0, 0, 0]
    assert [row["MAGI"] for row in rows] == [0, 0, 0]
    assert [row["Roth_Conversion"] for row in rows] == [0, 0, 0]
    assert [row["Shortfall"] for row in rows] == [0, 0, 0]
    assert [row["Social_Security"] for row in rows] == [0, 0, 0]
    assert [row["RMD"] for row in rows] == [0, 0, 0]


def test_run_plan_year1_magi_aca_seed_outputs_are_user_driven():
    cfg = minimal_two_person_config()
    cfg.year1_roth_conversion = 5000
    cfg.year1_magi_income = 42000
    cfg.year1_magi_losses = 2000
    cfg.magi_target_base = 85000
    cfg.aca_magi_floor = 43000
    cfg.aca_magi_ceiling = 85000
    cfg.aca_expected_subsidy_monthly = 1500

    rows = run_plan(cfg)

    assert rows[0]["MAGI"] == 45000
    assert rows[0]["Roth_Conversion"] == 5000
    assert rows[0]["Target_MAGI"] == 85000
    assert rows[0]["MAGI_Remaining"] == 40000
    assert rows[0]["ACA_Subsidy"] == 18000
    assert rows[0]["MAGI_Status"] == "IN_RANGE"
    assert rows[1]["Target_MAGI"] == 0
    assert rows[1]["MAGI_Remaining"] == 0
    assert rows[1]["ACA_Subsidy"] == 0
    assert rows[1]["MAGI_Status"] == ""
