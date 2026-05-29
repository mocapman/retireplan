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

    snapshot = format_input_snapshot(cfg)

    assert "Person 1 Final Age: 75" in snapshot
    assert "Person 2 Final Age: 85" in snapshot
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
    assert "GoGo Years: 10/100%" in snapshot
    assert "SlowGo Years: 8/80%" in snapshot
    assert "Total Assets: $1,743,000" in snapshot
    assert "Brokerage:" not in snapshot
    assert "Roth:" not in snapshot
    assert "IRA:" not in snapshot
    assert "Cash Balance" not in snapshot
    assert "State Deduction" not in snapshot
    assert "State Rate" not in snapshot
    assert "Draw Order" not in snapshot


def test_format_input_changes_shows_only_changes_from_baseline():
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
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )
    current = SimpleNamespace(
        final_age_person1=72,
        final_age_person2=85,
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
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )

    changes = format_input_changes(current, baseline)

    assert "Target Spend: $145,000 -> $150,000" in changes
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
