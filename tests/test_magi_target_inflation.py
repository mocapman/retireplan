from retireplan import inputs
from retireplan.engine import run_plan


def _first_two_pre_medicare(rows, aca_age):
    xs = [r for r in rows if r["Age_You"] < aca_age]
    return xs[0], xs[1] if len(xs) > 1 else (xs[0], xs[0])


def test_magi_target_inflates_and_engine_fills_when_headroom():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    # Maximize headroom and minimize ordinary income
    cfg.draw_order = "Brokerage, Roth, IRA"
    cfg.gogo_annual = cfg.slow_annual = cfg.nogo_annual = 30000
    cfg.balances_brokerage = max(cfg.balances_brokerage, 200_000)
    cfg.balances_ira = max(cfg.balances_ira, 50_000)

    rows = run_plan(cfg)
    y0, y1 = _first_two_pre_medicare(rows, cfg.aca_end_age)

    # Engine should hit target within tolerance each year
    def target(years_since_start):
        return round(cfg.magi_target_base * ((1 + cfg.inflation) ** years_since_start))

    assert abs(y0["MAGI"] - target(y0["Year"] - cfg.start_year)) <= 500
    assert abs(y1["MAGI"] - target(y1["Year"] - cfg.start_year)) <= 500

    # MAGI grows roughly by inflation ratio between consecutive pre-Medicare years
    ratio = (y1["MAGI"] + 1) / (y0["MAGI"] + 1)
    assert abs(ratio - (1 + cfg.inflation)) <= 0.1
