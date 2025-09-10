from retireplan import inputs
from retireplan.engine.engine import run_plan


def test_events_affect_cash_and_identity():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    events = [
        {"year": cfg.start_year, "amount": 12000},
        {"year": cfg.start_year, "amount": -5000},
    ]
    rows = run_plan(cfg, events=events)
    y0 = rows[0]
    # Events sit inside the budget; Total_Spend equals the budget
    assert y0["Total_Spend"] == y0["Total_Spend"]
    # Discretionary is budget minus taxes and events
    discretionary = y0["Total_Spend"] - y0["Taxes_Due"] - y0["Cash_Events"]
    assert discretionary >= 0
