import pytest

from retireplan.engine.core import run_plan
from retireplan.engine.policy import FED_BRACKETS
from retireplan.engine.taxes import (
    compute_tax_magi,
    progressive_tax,
    ss_taxable_amount,
)
from tests.test_run_plan_baseline import minimal_two_person_config, rmd_survivor_config


def test_federal_tax_zero_income():
    assert progressive_tax(0, "MFJ") == 0
    assert progressive_tax(0, "Single") == 0
    assert progressive_tax(-100, "MFJ") == 0


def test_federal_tax_mfj_first_bracket():
    assert progressive_tax(10_000, "MFJ") == 1_000
    assert progressive_tax(23_200, "MFJ") == 2_320


def test_federal_tax_single_first_bracket():
    assert progressive_tax(10_000, "Single") == 1_000
    assert progressive_tax(11_600, "Single") == 1_160


def test_federal_tax_mfj_crosses_brackets():
    expected = 23_200 * 0.10 + (50_000 - 23_200) * 0.12

    assert progressive_tax(50_000, "MFJ") == pytest.approx(expected)


def test_federal_tax_single_crosses_brackets():
    expected = 11_600 * 0.10 + (47_150 - 11_600) * 0.12 + (50_000 - 47_150) * 0.22

    assert progressive_tax(50_000, "Single") == pytest.approx(expected)


def test_federal_bracket_tables_are_current_expected_values():
    assert FED_BRACKETS["MFJ"][:3] == [
        (23_200, 0.10),
        (94_300, 0.12),
        (201_050, 0.22),
    ]
    assert FED_BRACKETS["Single"][:3] == [
        (11_600, 0.10),
        (47_150, 0.12),
        (100_525, 0.22),
    ]


def test_standard_deduction_mfj_vs_single():
    mfj_cfg = minimal_two_person_config()
    mfj_cfg.year1_spend = 0
    mfj_cfg.year1_brokerage_draw = 0
    mfj_cfg.standard_deduction_base = 31_500

    single_cfg = rmd_survivor_config()
    single_cfg.final_age_person1 = 73
    single_cfg.final_age_person2 = 75
    single_cfg.standard_deduction_base = 31_500

    mfj_row = run_plan(mfj_cfg)[1]
    survivor_row = run_plan(single_cfg)[1]

    assert mfj_row["Filing_Status_Used"] == "MFJ"
    assert mfj_row["Federal_Standard_Deduction_Used"] == 31_500
    assert survivor_row["Filing_Status_Used"] == "Single"
    assert survivor_row["Federal_Standard_Deduction_Used"] == 15_750


def test_same_income_tax_higher_single_than_mfj():
    taxable_income = 100_000

    assert progressive_tax(taxable_income, "Single") > progressive_tax(
        taxable_income, "MFJ"
    )


def test_compute_tax_magi_applies_standard_deduction_floor():
    _tax, _ss_tax, taxable_income, magi = compute_tax_magi(
        ira_ordinary=20_000,
        roth_conversion=5_000,
        ss_total=0,
        std_deduction=30_000,
        filing="MFJ",
    )

    assert magi == 25_000
    assert taxable_income == 0


def test_compute_tax_magi_taxable_income_before_and_after_deduction():
    _tax, ss_tax, taxable_income, magi = compute_tax_magi(
        ira_ordinary=40_000,
        roth_conversion=10_000,
        ss_total=20_000,
        std_deduction=15_000,
        filing="Single",
    )
    taxable_before_deduction = 40_000 + 10_000 + ss_tax

    assert magi == taxable_before_deduction
    assert taxable_income == taxable_before_deduction - 15_000


def test_survivor_year_uses_single_tax_assumptions():
    cfg = rmd_survivor_config()
    cfg.final_age_person1 = 73
    cfg.final_age_person2 = 75
    cfg.balances_ira = 1_000_000
    cfg.standard_deduction_base = 31_500
    cfg.estimated_state_tax_rate = 0

    survivor_row = run_plan(cfg)[1]

    assert survivor_row["Survivor_Year"] is True
    assert survivor_row["Filing_Status_Used"] == "Single"
    assert survivor_row["Federal_Tax_Bracket_Set_Used"] == "Single"
    assert survivor_row["Federal_Standard_Deduction_Used"] == 15_750


def test_taxable_social_security_never_exceeds_85_percent():
    for filing in ("MFJ", "Single"):
        ss_total = 50_000
        taxable_ss = ss_taxable_amount(
            ss_total=ss_total,
            other_ordinary=1_000_000,
            filing=filing,
        )

        assert taxable_ss <= ss_total * 0.85


def test_ira_draws_rmds_and_roth_conversions_are_ordinary_taxable_magi_income():
    cfg = rmd_survivor_config()
    cfg.balances_ira = 1_000_000
    cfg.target_spend = 50_000
    cfg.magi_target_base = 80_000
    cfg.aca_magi_floor = 0
    cfg.aca_magi_ceiling = 80_000
    cfg.standard_deduction_base = 0
    cfg.estimated_state_tax_rate = 0

    row = run_plan(cfg)[1]

    assert row["IRA_Taxable_Income"] == (
        row["IRA_Draw_Taxable_Income"] + row["IRA_RMD_Taxable_Income"]
    )
    assert row["Ordinary_Income_Taxable"] == (
        row["IRA_Taxable_Income"] + row["Roth_Conversion_Taxable_Income"]
    )
    assert row["MAGI"] == (
        row["MAGI_IRA_Draws"]
        + row["MAGI_RMD"]
        + row["MAGI_Roth_Conversions"]
        + row["MAGI_Brokerage_Gains"]
        + row["MAGI_Social_Security"]
    )


def test_roth_conversion_taxable_but_not_spending():
    cfg = minimal_two_person_config()
    cfg.year1_spend = 0
    cfg.year1_brokerage_draw = 0
    cfg.balances_brokerage = 0
    cfg.brokerage_cash = 0
    cfg.balances_roth = 0
    cfg.balances_ira = 100_000
    cfg.target_spend = 0
    cfg.magi_target_base = 10_000
    cfg.aca_magi_floor = 0
    cfg.aca_magi_ceiling = 10_000
    cfg.standard_deduction_base = 0
    cfg.estimated_state_tax_rate = 0

    row = run_plan(cfg)[1]

    assert row["Roth_Conversion"] > 0
    assert row["Roth_Conversion_Taxable_Income"] == row["Roth_Conversion"]
    assert row["Roth_Conversion_MAGI_Income"] == row["Roth_Conversion"]
    assert row["Target_Spend"] == 0
    assert row["Total_Spend"] == row["Taxes_Due"]
