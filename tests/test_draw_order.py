from copy import deepcopy

from retireplan import inputs
from retireplan.engine import run_plan


def _first_pre_medicare(rows, aca_age):
    for r in rows:
        if r["Your_Age"] < aca_age:
            return r
    return rows[0]


def test_draw_order_changes_distribution():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")

    # Baseline: IRA -> Brokerage -> Roth
    cfg1 = deepcopy(cfg)
    cfg1.draw_order = "IRA, Brokerage, Roth"
    rows1 = run_plan(cfg1)
    y1 = _first_pre_medicare(rows1, cfg.aca_end_age)

    # Alternate: Brokerage -> Roth -> IRA
    cfg2 = deepcopy(cfg)
    cfg2.draw_order = "Brokerage, Roth, IRA"
    rows2 = run_plan(cfg2)
    y2 = _first_pre_medicare(rows2, cfg.aca_end_age)

    # Same spending target
    assert abs(y1["Total_Spend"] - y2["Total_Spend"]) <= 2

    # Distribution changes as expected
    assert y1["IRA_Draw"] >= y2["IRA_Draw"]
    assert y2["Brokerage_Draw"] >= y1["Brokerage_Draw"]

    # MAGI typically higher with IRA-first (ordinary income larger).
    assert y1["MAGI"] >= y2["MAGI"]
