from retireplan import inputs
from retireplan.engine.engine import run_plan
from retireplan.engine.social_security import ss_for_year


def test_survivor_steps_up_to_higher_benefit():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)

    # Find first Survivor year where at least one benefit is scheduled
    for r in rows:
        if r["Living"] == "Survivor":
            idx = int(r["Year"] - cfg.start_year)
            you_sched = ss_for_year(
                r["Your_Age"],
                cfg.ss_you_start_age,
                cfg.ss_you_annual_at_start,
                idx,
                cfg.inflation,
            )
            sp_sched = ss_for_year(
                r["Spouse_Age"],
                cfg.ss_spouse_start_age,
                cfg.ss_spouse_annual_at_start,
                idx,
                cfg.inflation,
            )
            expected = round(max(you_sched, sp_sched))
            assert r["Social_Security"] == expected
            break
