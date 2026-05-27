from types import SimpleNamespace

from retireplan.gui.results_display import (
    calculate_results_summary,
    format_currency,
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
        target_spend=145000,
        gogo_years=10,
        gogo_percent=100,
        slow_years=8,
        slow_percent=80,
        balances_brokerage=543000,
        balances_roth=200000,
        balances_ira=1000000,
    )

    snapshot = format_input_snapshot(cfg)

    assert "Target Spend: $145,000" in snapshot
    assert "GoGo Years: 10" in snapshot
    assert "GoGo %: 100%" in snapshot
    assert "SlowGo Years: 8" in snapshot
    assert "SlowGo %: 80%" in snapshot
    assert "Brokerage: $543,000" in snapshot
    assert "Roth: $200,000" in snapshot
    assert "IRA: $1,000,000" in snapshot
    assert "State Deduction" not in snapshot
    assert "State Rate" not in snapshot
    assert "Draw Order" not in snapshot
