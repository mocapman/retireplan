from retireplan import inputs
from retireplan.engine.core import run_plan


def test_nonnegative_and_totals():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for r in rows:
        assert r["IRA_Balance"] >= 0
        assert r["Brokerage_Balance"] >= 0
        assert r["Roth_Balance"] >= 0
        assert r["IRA_Draw"] >= 0 and r["Brokerage_Draw"] >= 0 and r["Roth_Draw"] >= 0

        summed = r["IRA_Balance"] + r["Brokerage_Balance"] + r["Roth_Balance"]
        assert abs(r["Total_Assets"] - summed) <= 2  # allow rounding delta
