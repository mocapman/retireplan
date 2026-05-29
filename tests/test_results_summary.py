from types import SimpleNamespace

from retireplan.gui.results_display import (
    calculate_results_summary,
    format_currency,
    format_input_changes,
    format_input_snapshot,
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


def test_format_currency_uses_whole_dollar_formatting():
    assert format_currency(1234.49) == "$1,234"
    assert format_currency(1234.5) == "$1,234"


def test_format_input_snapshot_includes_key_scenario_inputs():
    cfg = SimpleNamespace(
        final_age_person1=75,
        final_age_person2=85,
        target_spend=145000,
        magi_target_base=85000,
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
    assert "MAGI Target: $85,000" in snapshot
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
        magi_target_base=85000,
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
        magi_target_base=85000,
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
    assert "GoGo Years: 10/100% -> 12/100%" in changes
    assert "SlowGo Years: 8/80% -> 8/75%" in changes
    assert "MAGI Target" not in changes
    assert "Total Assets" not in changes


def test_format_input_changes_reports_no_changes_from_baseline():
    baseline = SimpleNamespace(
        final_age_person1=75,
        final_age_person2=85,
        target_spend=145000,
        magi_target_base=85000,
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
