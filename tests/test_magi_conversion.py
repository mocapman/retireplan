from retireplan import inputs
from retireplan.engine.core import run_plan


def test_conversions_fill_magi_before_medicare_when_headroom_exists():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")

    # Create headroom for MAGI by drawing from brokerage first and lowering spend
    cfg.draw_order = "Brokerage, Roth, IRA"
    cfg.target_spend = 30000
    cfg.gogo_percent = 100.0
    cfg.slow_percent = 100.0
    cfg.nogo_percent = 100.0
    cfg.balances_brokerage = max(cfg.balances_brokerage, 200000)
    cfg.balances_ira = max(50000, cfg.balances_ira)  # ensure some IRA to convert

    rows = run_plan(cfg)

    # Pick first pre-Medicare year (your age < ACA end age)
    y0 = next(r for r in rows if r["Your_Age"] < cfg.aca_end_age)

    # Conversions should be positive and MAGI near the inflated target
    assert y0["Roth_Conversion"] > 0
    expected_target = round(
        cfg.magi_target_base * ((1 + cfg.inflation) ** (y0["Year"] - cfg.start_year))
    )
    assert abs(y0["MAGI"] - expected_target) <= 500  # allow rounding/tax-step drift
