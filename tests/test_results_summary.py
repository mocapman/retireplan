from types import SimpleNamespace

from retireplan.gui.results_display import (
    calculate_results_summary,
    format_currency,
    format_input_changes,
    format_input_snapshot,
    ResultsDisplay,
)


def test_calculate_results_summary_totals_tax_fields_and_final_assets():
    rows = [
        {
            "Federal_Tax": 100,
            "Estimated_State_Tax": 25,
            "Taxes_Due": 125,
            "Total_Assets": 10000,
        },
        {
            "Federal_Tax": 200,
            "Estimated_State_Tax": 50,
            "Taxes_Due": 250,
            "Total_Assets": 9000,
        },
    ]

    summary = calculate_results_summary(rows)

    assert summary["Federal_Tax"] == 300
    assert summary["Estimated_State_Tax"] == 75
    assert summary["Taxes_Due"] == 375
    assert summary["Total_Assets"] == 9000


def test_calculate_results_summary_handles_empty_or_missing_values():
    summary = calculate_results_summary(
        [
            {
                "Federal_Tax": "",
                "Estimated_State_Tax": None,
                "Taxes_Due": "not available",
                "Total_Assets": 1234,
            }
        ]
    )

    assert summary["Federal_Tax"] == 0
    assert summary["Estimated_State_Tax"] == 0
    assert summary["Taxes_Due"] == 0
    assert summary["Total_Assets"] == 1234
    assert calculate_results_summary([])["Total_Assets"] == 0


def test_summary_text_labels_total_tax_as_lifetime_taxes():
    text = ResultsDisplay.format_summary_text(
        None,
        {"Federal_Tax": 100, "Estimated_State_Tax": 25, "Taxes_Due": 125},
    )

    assert "Lifetime Taxes: $125" in text
    assert "Total Taxes" not in text


def test_format_currency_uses_whole_dollar_formatting():
    assert format_currency(1234.49) == "$1,234"
    assert format_currency(1234.5) == "$1,234"


def test_projection_column_order_accepts_keys_or_gui_labels_without_duplicates():
    display = ResultsDisplay.__new__(ResultsDisplay)
    headers = ["Year", "Age1", "Age2", "Filing", "MAGI", "Assets"]
    keys = [
        "Year",
        "Person1_Age",
        "Person2_Age",
        "Filing",
        "MAGI",
        "Total_Assets",
    ]

    order = ["Year", "MAGI", "MAGI", "Age1", "Person2_Age"]

    indices = display._resolve_column_order(order, headers, keys)

    assert indices == [0, 4, 1, 2, 3, 5]


def test_projection_money_columns_are_identified_by_schema_key():
    display = ResultsDisplay.__new__(ResultsDisplay)

    assert not display._is_money_column("Year")
    assert not display._is_money_column("Person1_Age")
    assert not display._is_money_column("Filing")
    assert display._is_money_column("MAGI")
    assert display._is_money_column("Total_Assets")


def test_saved_projection_column_order_uses_schema_keys():
    class FakeSheet:
        def headers(self):
            return ["Year", "Age1", "MAGI", "Assets"]

    display = ResultsDisplay.__new__(ResultsDisplay)
    display.sheet = FakeSheet()

    assert display.get_current_column_order() == [
        "Year",
        "Person1_Age",
        "MAGI",
        "Total_Assets",
    ]


def test_format_input_snapshot_includes_key_scenario_inputs():
    cfg = SimpleNamespace(
        birth_year_person1=1967,
        birth_year_person2=1969,
        final_age_person1=75,
        final_age_person2=85,
        filing_status="MFJ",
        start_year=2026,
        year1_spend=120000,
        year1_brokerage_draw=100000,
        year1_ira_draw=20000,
        year1_roth_draw=0,
        target_spend=145000,
        year1_magi_floor=43000,
        year1_magi_target=85000,
        year1_magi_ceiling=85000,
        year1_extra_magi_income=29631,
        year1_magi_loss_offset=5332,
        year1_planned_roth_conversion=15000,
        aca_magi_floor=43000,
        aca_magi_target=85000,
        aca_magi_ceiling=85000,
        aca_extra_magi_income=2500,
        aca_magi_loss_offset=500,
        aca_planned_roth_conversion=15000,
        medicare_magi_floor=43000,
        medicare_magi_target=85000,
        medicare_magi_ceiling=200000,
        medicare_extra_magi_income=3500,
        medicare_magi_loss_offset=700,
        medicare_planned_roth_conversion=12000,
        magi_floor_base=43000,
        magi_target_base=85000,
        magi_ceiling_base=85000,
        medicare_magi_ceiling_base=200000,
        aca_end_age=65,
        year1_magi_income=29631,
        year1_magi_losses=5332,
        year1_roth_conversion=15000,
        aca_annual_magi_income=2500,
        aca_annual_magi_loss=500,
        aca_annual_roth_conversion=15000,
        medicare_annual_magi_income=3500,
        medicare_annual_magi_loss=700,
        medicare_annual_roth_conversion=12000,
        gogo_years=10,
        gogo_percent=100,
        slow_years=8,
        slow_percent=80,
        nogo_percent=70,
        survivor_percent=70,
        draw_order="Brokerage, IRA, Roth",
        ss_person1_start_age=62,
        ss_person2_start_age=67,
        ss_person1_annual_at_start=32500,
        ss_person2_annual_at_start=7000,
        inflation=0.035,
        brokerage_growth=0.04,
        roth_growth=0.08,
        ira_growth=0.07,
        estimated_state_deduction=0,
        estimated_state_tax_rate=0.0875,
        standard_deduction_base=30000,
        rmd_start_age=73,
        brokerage_cash=400000,
        brokerage_cost_basis=100000,
        brokerage_unrealized_gain=43000,
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )

    snapshot = format_input_snapshot(cfg)

    assert snapshot.startswith("Inputs:\n")
    assert "Personal:" in snapshot
    assert "Accounts:" in snapshot
    assert "Spending:" in snapshot
    assert "Rates:" in snapshot
    assert "Tax:" in snapshot
    assert "Roth Planning:" in snapshot
    assert "Person 1 Birth Year: 1967" in snapshot
    assert "Person 2 Birth Year: 1969" in snapshot
    assert "Person 1 Final Age: 75" in snapshot
    assert "Person 2 Final Age: 85" in snapshot
    assert "Filing Status: MFJ" in snapshot
    assert "SS Age 1: 62" in snapshot
    assert "SS Age 2: 67" in snapshot
    assert "SS Annual 1: $32,500" in snapshot
    assert "SS Annual 2: $7,000" in snapshot
    assert "Brkg Cash: $400,000" in snapshot
    assert "Brkg Basis: $100,000" in snapshot
    assert "Brkg Gain: $43,000" in snapshot
    assert "IRA: $1,000,000" in snapshot
    assert "Roth: $200,000" in snapshot
    assert "Target Spend: $145,000" in snapshot
    assert "Year 1 MAGI Floor: $43,000" in snapshot
    assert "Year 1 MAGI Target: $85,000" in snapshot
    assert "Year 1 MAGI Ceiling: $85,000" in snapshot
    assert "Year 1 Extra MAGI Income: $29,631" in snapshot
    assert "Year 1 MAGI Loss Offset: $5,332" in snapshot
    assert "Year 1 Planned Roth Conversion: $15,000" in snapshot
    assert "ACA MAGI Floor: $43,000" in snapshot
    assert "ACA MAGI Target: $85,000" in snapshot
    assert "ACA MAGI Ceiling: $85,000" in snapshot
    assert "ACA Extra MAGI Income: $2,500" in snapshot
    assert "ACA MAGI Loss Offset: $500" in snapshot
    assert "ACA Planned Roth Conversion: $15,000" in snapshot
    assert "Medicare MAGI Floor: $43,000" in snapshot
    assert "Medicare MAGI Target: $85,000" in snapshot
    assert "Medicare MAGI Ceiling: $200,000" in snapshot
    assert "Medicare Extra MAGI Income: $3,500" in snapshot
    assert "Medicare MAGI Loss Offset: $700" in snapshot
    assert "Medicare Planned Roth Conversion: $12,000" in snapshot
    assert "Medicare Age: 65" in snapshot
    assert "Start Year: 2026" in snapshot
    assert "Year 1 Spend: $120,000" in snapshot
    assert "Year 1 Brkg Draw: $100,000" in snapshot
    assert "Year 1 IRA Draw: $20,000" in snapshot
    assert "Draw Order: Brokerage, IRA, Roth" in snapshot
    assert "GoGo Years: 10/100%" in snapshot
    assert "SlowGo Years: 8/80%" in snapshot
    assert "NoGo %: 70%" in snapshot
    assert "Survivor %: 70%" in snapshot
    assert "Inflation: 3.50%" in snapshot
    assert "Brkg Growth: 4%" in snapshot
    assert "Roth Growth: 8%" in snapshot
    assert "IRA Growth: 7%" in snapshot
    assert "State Deduction: $0" in snapshot
    assert "State Rate: 8.75%" in snapshot
    assert "Standard Deduction: $30,000" in snapshot
    assert "RMD Start Age: 73" in snapshot
    assert "Total Assets" not in snapshot
    assert "Cash Balance" not in snapshot


def test_format_input_changes_shows_only_changes_from_baseline():
    baseline = SimpleNamespace(
        birth_year_person1=1967,
        birth_year_person2=1969,
        final_age_person1=75,
        final_age_person2=85,
        filing_status="MFJ",
        start_year=2026,
        year1_spend=120000,
        year1_brokerage_draw=100000,
        year1_ira_draw=20000,
        year1_roth_draw=0,
        target_spend=145000,
        year1_magi_floor=43000,
        year1_magi_target=85000,
        year1_magi_ceiling=85000,
        year1_extra_magi_income=29631,
        year1_magi_loss_offset=5332,
        year1_planned_roth_conversion=15000,
        aca_magi_floor=43000,
        aca_magi_target=85000,
        aca_magi_ceiling=85000,
        aca_extra_magi_income=2500,
        aca_magi_loss_offset=500,
        aca_planned_roth_conversion=15000,
        medicare_magi_floor=43000,
        medicare_magi_target=85000,
        medicare_magi_ceiling=85000,
        medicare_extra_magi_income=3500,
        medicare_magi_loss_offset=700,
        medicare_planned_roth_conversion=12000,
        magi_floor_base=43000,
        magi_target_base=85000,
        magi_ceiling_base=85000,
        medicare_magi_ceiling_base=85000,
        aca_end_age=65,
        year1_magi_income=29631,
        year1_magi_losses=5332,
        year1_roth_conversion=15000,
        aca_annual_magi_income=2500,
        aca_annual_magi_loss=500,
        aca_annual_roth_conversion=15000,
        medicare_annual_magi_income=3500,
        medicare_annual_magi_loss=700,
        medicare_annual_roth_conversion=12000,
        gogo_years=10,
        gogo_percent=100,
        slow_years=8,
        slow_percent=80,
        nogo_percent=70,
        survivor_percent=70,
        draw_order="Brokerage, IRA, Roth",
        ss_person1_start_age=62,
        ss_person2_start_age=67,
        ss_person1_annual_at_start=32500,
        ss_person2_annual_at_start=7000,
        inflation=0.035,
        brokerage_growth=0.04,
        roth_growth=0.08,
        ira_growth=0.07,
        estimated_state_deduction=0,
        estimated_state_tax_rate=0.0875,
        standard_deduction_base=30000,
        rmd_start_age=73,
        brokerage_cash=400000,
        brokerage_cost_basis=100000,
        brokerage_unrealized_gain=43000,
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )
    current = SimpleNamespace(
        birth_year_person1=1967,
        birth_year_person2=1969,
        final_age_person1=72,
        final_age_person2=85,
        filing_status="MFJ",
        start_year=2026,
        year1_spend=121000,
        year1_brokerage_draw=100000,
        year1_ira_draw=21000,
        year1_roth_draw=0,
        target_spend=150000,
        year1_magi_floor=43000,
        year1_magi_target=85000,
        year1_magi_ceiling=43000,
        year1_extra_magi_income=30000,
        year1_magi_loss_offset=5332,
        year1_planned_roth_conversion=20000,
        aca_magi_floor=43000,
        aca_magi_target=85000,
        aca_magi_ceiling=43000,
        aca_extra_magi_income=2500,
        aca_magi_loss_offset=750,
        aca_planned_roth_conversion=15000,
        medicare_magi_floor=43000,
        medicare_magi_target=85000,
        medicare_magi_ceiling=200000,
        medicare_extra_magi_income=3500,
        medicare_magi_loss_offset=700,
        medicare_planned_roth_conversion=18000,
        magi_floor_base=43000,
        magi_target_base=85000,
        magi_ceiling_base=43000,
        medicare_magi_ceiling_base=200000,
        aca_end_age=65,
        year1_magi_income=30000,
        year1_magi_losses=5332,
        year1_roth_conversion=20000,
        aca_annual_magi_income=2500,
        aca_annual_magi_loss=750,
        aca_annual_roth_conversion=15000,
        medicare_annual_magi_income=3500,
        medicare_annual_magi_loss=700,
        medicare_annual_roth_conversion=18000,
        gogo_years=12,
        gogo_percent=100,
        slow_years=8,
        slow_percent=75,
        nogo_percent=70,
        survivor_percent=70,
        draw_order="Brokerage, IRA, Roth",
        ss_person1_start_age=63,
        ss_person2_start_age=67,
        ss_person1_annual_at_start=32500,
        ss_person2_annual_at_start=7000,
        inflation=0.035,
        brokerage_growth=0.04,
        roth_growth=0.08,
        ira_growth=0.07,
        estimated_state_deduction=0,
        estimated_state_tax_rate=0.0875,
        standard_deduction_base=30000,
        rmd_start_age=73,
        brokerage_cash=398000,
        brokerage_cost_basis=101000,
        brokerage_unrealized_gain=44000,
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )

    changes = format_input_changes(current, baseline)

    assert changes.startswith("Inputs changed:\n")
    assert "Accounts:" in changes
    assert "Brkg Cash: $400,000 -> $398,000" in changes
    assert "Brkg Basis: $100,000 -> $101,000" in changes
    assert "Brkg Gain: $43,000 -> $44,000" in changes
    assert "Target Spend: $145,000 -> $150,000" in changes
    assert "SS Age 1: 62 -> 63" in changes
    assert "Year 1 Spend: $120,000 -> $121,000" in changes
    assert "Year 1 IRA Draw: $20,000 -> $21,000" in changes
    assert "Person 1 Final Age: 75 -> 72" in changes
    assert "ACA MAGI Ceiling: $85,000 -> $43,000" in changes
    assert "Medicare MAGI Ceiling: $85,000 -> $200,000" in changes
    assert "Year 1 Extra MAGI Income: $29,631 -> $30,000" in changes
    assert "Year 1 Planned Roth Conversion: $15,000 -> $20,000" in changes
    assert "ACA MAGI Loss Offset: $500 -> $750" in changes
    assert "Medicare Planned Roth Conversion: $12,000 -> $18,000" in changes
    assert "GoGo Years: 10/100% -> 12/100%" in changes
    assert "SlowGo Years: 8/80% -> 8/75%" in changes
    assert "ACA MAGI Target" not in changes
    assert "Total Assets" not in changes


def test_format_input_changes_reports_no_changes_from_baseline():
    baseline = SimpleNamespace(
        final_age_person1=75,
        final_age_person2=85,
        target_spend=145000,
        year1_magi_floor=43000,
        year1_magi_target=85000,
        year1_magi_ceiling=85000,
        year1_extra_magi_income=29631,
        year1_magi_loss_offset=5332,
        year1_planned_roth_conversion=15000,
        aca_magi_floor=43000,
        aca_magi_target=85000,
        aca_magi_ceiling=85000,
        aca_extra_magi_income=2500,
        aca_magi_loss_offset=500,
        aca_planned_roth_conversion=15000,
        medicare_magi_floor=43000,
        medicare_magi_target=85000,
        medicare_magi_ceiling=200000,
        medicare_extra_magi_income=3500,
        medicare_magi_loss_offset=700,
        medicare_planned_roth_conversion=12000,
        magi_floor_base=43000,
        magi_target_base=85000,
        magi_ceiling_base=85000,
        medicare_magi_ceiling_base=200000,
        aca_end_age=65,
        year1_magi_income=29631,
        year1_magi_losses=5332,
        year1_roth_conversion=15000,
        aca_annual_magi_income=2500,
        aca_annual_magi_loss=500,
        aca_annual_roth_conversion=15000,
        medicare_annual_magi_income=3500,
        medicare_annual_magi_loss=700,
        medicare_annual_roth_conversion=12000,
        gogo_years=10,
        gogo_percent=100,
        slow_years=8,
        slow_percent=80,
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )

    assert (
        format_input_changes(baseline, baseline)
        == "Inputs: No changes from default config"
    )
