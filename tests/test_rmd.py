from retireplan import inputs
from retireplan.engine.core import run_plan
from retireplan.engine.policy import rmd_factor


def test_rmd_triggers_at_start_age_and_no_conversions_after_medicare():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")

    # Start at age >= rmd_start_age to force an RMD in first year.
    # Also ensure Medicare age reached so MAGI target is zero -> no conversions.
    years_to_bump = (cfg.rmd_start_age + 2) - (cfg.start_year - cfg.birth_year_you)
    cfg.start_year += max(0, years_to_bump)
    # Keep spend modest so RMD covers most needs and we can check the amount
    cfg.target_spend = 20000
    cfg.gogo_percent = 100.0
    cfg.slow_percent = 100.0
    cfg.nogo_percent = 100.0

    rows = run_plan(cfg)
    y0 = rows[0]

    # RMD = IRA_start / factor(age)
    ira_start = cfg.balances_ira
    expected_rmd = round(ira_start / rmd_factor(y0["Your_Age"]))
    assert abs(y0["RMD"] - expected_rmd) <= 2

    # After Medicare age, conversions should be zero
    assert y0["Your_Age"] >= cfg.aca_end_age
    assert y0["Roth_Conversion"] == 0
