from retireplan import inputs
from retireplan.engine.engine import run_plan


def _first_pre_medicare(rows, aca_age):
    for r in rows:
        if r["Your_Age"] < aca_age:
            return r
    return None


def _first_post_medicare(rows, aca_age):
    for r in rows:
        if r["Your_Age"] >= aca_age:
            return r
    return None


def test_magi_fills_to_inflated_target_pre_medicare():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    cfg.draw_order = "Brokerage, Roth, IRA"  # minimize ordinary income
    cfg.target_spend = 30000
    cfg.gogo_percent = cfg.slow_percent = cfg.nogo_percent = 100.0
    cfg.balances_brokerage = max(cfg.balances_brokerage, 200_000)
    cfg.balances_ira = max(cfg.balances_ira, 50_000)

    rows = run_plan(cfg)
    y = _first_pre_medicare(rows, cfg.aca_end_age)
    assert y is not None

    years_since_start = y["Year"] - cfg.start_year
    expected_target = round(
        cfg.magi_target_base * ((1 + cfg.inflation) ** years_since_start)
    )
    assert abs(y["MAGI"] - expected_target) <= 500  # rounding/tax step tolerance
    assert y["Roth_Conversion"] > 0


def test_no_conversions_post_medicare_and_rmd_works():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")

    # force post-Medicare start and trigger RMD in first year
    bump_to_post_medicare = (cfg.aca_end_age + 1) - (
        cfg.start_year - cfg.birth_year_you
    )
    cfg.start_year += max(0, bump_to_post_medicare)
    years_to_rmd = (cfg.rmd_start_age + 1) - (cfg.start_year - cfg.birth_year_you)
    cfg.start_year += max(0, years_to_rmd)

    rows = run_plan(cfg)
    y0 = rows[0]

    # No conversions after Medicare
    assert y0["Your_Age"] >= cfg.aca_end_age
    assert y0["Roth_Conversion"] == 0

    # If RMD is present, it should match factor logic approximately
    if y0["RMD"] > 0:
        # IRA start-of-year approximated by reversing year-end growth and adds draws+RMD
        # Simpler check: required amount aligns with table within tolerance
        from retireplan.engine.policy import rmd_factor as rf

        expect = round(cfg.balances_ira / rf(y0["Your_Age"]))
        assert abs(y0["RMD"] - expect) <= 2
