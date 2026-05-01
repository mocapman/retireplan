from retireplan import inputs
from retireplan.engine.core import run_plan
from retireplan.engine.social_security import ss_for_year


def test_survivor_steps_up_to_higher_benefit():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)

    # Find first Single (survivor) year where at least one benefit is scheduled
    for r in rows:
        if r["Filing"] == "Single":
            idx = int(r["Year"] - cfg.start_year)
            you_sched = ss_for_year(
                r["Person1_Age"],
                cfg.ss_person1_start_age,
                cfg.ss_person1_annual_at_start,
                idx,
                cfg.inflation,
            )
            sp_sched = ss_for_year(
                r["Person2_Age"],
                cfg.ss_person2_start_age,
                cfg.ss_person2_annual_at_start,
                idx,
                cfg.inflation,
            )
            expected = round(max(you_sched, sp_sched))
            assert r["Social_Security"] == expected
            break
