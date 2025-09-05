from retireplan import inputs
from retireplan.engine import run_plan


def test_events_affect_cash_and_identity():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    # Two events in start year: +12k expense and -5k inflow
    events = [
        {"year": cfg.start_year, "amount": 12000},
        {"year": cfg.start_year, "amount": -5000},
    ]
    rows = run_plan(cfg, events=events)
    y0 = rows[0]
    assert y0["Events_Cash"] == 7000
    assert y0["Total_Spend"] == y0["Spend_Target"] + y0["Taxes"] + y0["Events_Cash"]


def test_roth_conversion_never_exceeds_remaining_ira():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    cfg.draw_order = "Brokerage, Roth, IRA"  # maximize remaining IRA for conversion
    rows = run_plan(cfg)
    y0 = rows[0]
    ira_start = cfg.balances_ira
    # available for conversion = IRA start - cash IRA draws - RMD (cannot convert RMD)
    max_conv = max(0, ira_start - y0["Draw_IRA"] - y0["RMD"])
    assert y0["Roth_Conversion"] <= max_conv + 2  # rounding wiggle
