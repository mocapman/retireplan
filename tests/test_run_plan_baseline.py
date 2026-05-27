from decimal import Decimal

from retireplan.engine.core import _clean_shortfall, _rmd_age_for_year, run_plan
from retireplan.engine.taxes import compute_tax_magi
from retireplan.engine.timeline import YearCtx
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
        "Brokerage_Cash_Used",
        "Brokerage_Holdings_Sold",
        "Brokerage_Basis_Used",
        "Brokerage_Gain_Ratio",
        "Brokerage_Capital_Gains",
        "Brokerage_MAGI_Income",
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


def test_run_plan_brokerage_draw_within_cash_does_not_increase_magi():
    cfg = minimal_two_person_config()
    cfg.year1_spend = 0
    cfg.year1_brokerage_draw = 0
    cfg.brokerage_cash = 10000
    cfg.brokerage_cost_basis = 0
    cfg.brokerage_unrealized_gain = 0
    cfg.balances_brokerage = 10000

    rows = run_plan(cfg)

    assert rows[1]["Brokerage_Draw"] == 800
    assert rows[1]["Brokerage_Cash_Used"] == 800
    assert rows[1]["Brokerage_Holdings_Sold"] == 0
    assert rows[1]["Brokerage_Basis_Used"] == 0
    assert rows[1]["Brokerage_Gain_Ratio"] == 0.0
    assert rows[1]["Brokerage_Capital_Gains"] == 0
    assert rows[1]["Brokerage_MAGI_Income"] == 0
    assert rows[1]["MAGI"] == 0


def test_run_plan_brokerage_draw_beyond_cash_increases_magi_by_estimated_gain():
    cfg = minimal_two_person_config()
    cfg.year1_spend = 0
    cfg.year1_brokerage_draw = 0
    cfg.brokerage_cash = 500
    cfg.brokerage_cost_basis = 7500
    cfg.brokerage_unrealized_gain = 2000
    cfg.balances_brokerage = 10000
    cfg.standard_deduction_base = 0

    rows = run_plan(cfg)

    assert rows[1]["Brokerage_Draw"] == 806
    assert rows[1]["Brokerage_Cash_Used"] == 500
    assert rows[1]["Brokerage_Holdings_Sold"] == 306
    assert rows[1]["Brokerage_Basis_Used"] == 242
    assert rows[1]["Brokerage_Gain_Ratio"] == 0.2105
    assert rows[1]["Brokerage_Capital_Gains"] == 65
    assert rows[1]["Brokerage_MAGI_Income"] == 65
    assert rows[1]["MAGI"] == 65
    assert rows[1]["Taxes_Due"] > 0
    assert rows[1]["Total_Spend"] == (
        rows[1]["Target_Spend"] + rows[1]["Taxes_Due"] + rows[1]["Cash_Events"]
    )
    assert rows[1]["Brokerage_Draw"] == rows[1]["Total_Spend"]
    assert rows[1]["Shortfall"] == 0


def test_run_plan_positive_tax_is_funded_by_additional_draws_once():
    cfg = minimal_two_person_config()
    cfg.year1_spend = 0
    cfg.year1_brokerage_draw = 0
    cfg.balances_brokerage = 0
    cfg.brokerage_cash = 0
    cfg.brokerage_cost_basis = 0
    cfg.brokerage_unrealized_gain = 0
    cfg.balances_roth = 0
    cfg.balances_ira = 100000
    cfg.draw_order = "IRA, Brokerage, Roth"
    cfg.standard_deduction_base = 0

    rows = run_plan(cfg)
    funded_tax_row = rows[1]

    assert funded_tax_row["Target_Spend"] == 800
    assert funded_tax_row["Taxes_Due"] == 89
    assert funded_tax_row["Cash_Events"] == 0
    assert funded_tax_row["Total_Spend"] == 889
    assert funded_tax_row["IRA_Draw"] == 889
    assert funded_tax_row["IRA_Balance"] == 99111
    assert funded_tax_row["Shortfall"] == 0


def test_run_plan_shortfall_is_based_on_total_spend_with_cash_events():
    cfg = minimal_two_person_config()
    cfg.year1_spend = 0
    cfg.year1_brokerage_draw = 0
    cfg.balances_brokerage = 500
    cfg.brokerage_cash = 500
    cfg.brokerage_cost_basis = 0
    cfg.brokerage_unrealized_gain = 0
    cfg.balances_roth = 0
    cfg.balances_ira = 0

    rows = run_plan(cfg, events=[{"year": 2026, "amount": 500}])
    shortfall_row = rows[1]

    assert shortfall_row["Target_Spend"] == 800
    assert shortfall_row["Taxes_Due"] == 0
    assert shortfall_row["Cash_Events"] == 500
    assert shortfall_row["Total_Spend"] == 1300
    assert shortfall_row["Brokerage_Draw"] == 500
    assert shortfall_row["Shortfall"] == 800


def test_clean_shortfall_treats_tiny_rounding_residual_as_zero():
    assert _clean_shortfall(Decimal("0.01")) == Decimal(0)
    assert _clean_shortfall(Decimal("1.0")) == Decimal(0)


def test_clean_shortfall_preserves_real_unfunded_amounts():
    assert _clean_shortfall(Decimal("1.01")) == Decimal("1.01")
    assert _clean_shortfall(Decimal("800")) == Decimal("800")


def test_compute_tax_magi_includes_brokerage_capital_gains_in_taxable_income():
    _tax, _ss_tax, taxable_income, magi = compute_tax_magi(
        ira_ordinary=0,
        roth_conversion=0,
        ss_total=0,
        std_deduction=0,
        filing="MFJ",
        brokerage_capital_gains=1234,
    )

    assert taxable_income == 1234
    assert magi == 1234


def rmd_survivor_config() -> Inputs:
    cfg = minimal_two_person_config()
    cfg.start_year = 2025
    cfg.birth_year_person1 = 1952
    cfg.birth_year_person2 = 1952
    cfg.final_age_person1 = 75
    cfg.final_age_person2 = 75
    cfg.balances_brokerage = 0
    cfg.brokerage_cash = 0
    cfg.brokerage_cost_basis = 0
    cfg.brokerage_unrealized_gain = 0
    cfg.balances_roth = 0
    cfg.balances_ira = 26500
    cfg.year1_spend = 0
    cfg.year1_brokerage_draw = 0
    cfg.target_spend = 0
    cfg.standard_deduction_base = 0
    cfg.rmd_start_age = 73
    return cfg


def test_rmd_still_occurs_when_person1_is_alive_at_rmd_age():
    cfg = rmd_survivor_config()

    rows = run_plan(cfg)

    assert rows[1]["Person1_Age"] == 74
    assert rows[1]["RMD"] > 0
    assert rows[1]["IRA_Draw"] == 0
    assert rows[1]["MAGI"] == rows[1]["RMD"]
    assert rows[1]["Taxes_Due"] > 0


def test_rmd_continues_when_only_person2_survives_at_rmd_age():
    cfg = rmd_survivor_config()
    cfg.final_age_person1 = 73
    cfg.final_age_person2 = 75

    rows = run_plan(cfg)
    survivor_row = rows[1]

    assert survivor_row["Person1_Age"] == 74
    assert survivor_row["Person2_Age"] == 74
    assert survivor_row["Filing"] == "Single"
    assert survivor_row["RMD"] > 0
    assert survivor_row["IRA_Draw"] == 0
    assert survivor_row["MAGI"] == survivor_row["RMD"]
    assert survivor_row["Taxes_Due"] > 0


def test_rmd_age_is_none_when_neither_person_is_alive():
    yc = YearCtx(
        year=2030,
        age_person1=78,
        age_person2=78,
        phase="NoGo",
        person1_alive=False,
        person2_alive=False,
    )

    assert _rmd_age_for_year(yc) is None


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
