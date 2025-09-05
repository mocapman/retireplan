from retireplan import inputs
from retireplan.engine import run_plan


def test_nonnegative_and_totals():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    for r in rows:
        assert r["End_Bal_IRA"] >= 0
        assert r["End_Bal_Brokerage"] >= 0
        assert r["End_Bal_Roth"] >= 0
        assert r["Draw_IRA"] >= 0 and r["Draw_Brokerage"] >= 0 and r["Draw_Roth"] >= 0

        summed = r["End_Bal_IRA"] + r["End_Bal_Brokerage"] + r["End_Bal_Roth"]
        assert abs(r["Total_Assets"] - summed) <= 2  # allow rounding delta
