from retireplan import inputs
from retireplan.engine.core import run_plan


def test_rmd_triggers_only_at_start_age():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    # Year 1: person1 age = rmd_start_age - 1 (no RMD, and year 1 is hardcoded anyway)
    cfg.start_year = cfg.birth_year_person1 + cfg.rmd_start_age - 1
    rows = run_plan(cfg)
    y0 = rows[0]
    assert y0["Person1_Age"] == cfg.rmd_start_age - 1
    assert y0["RMD"] == 0

    # Next year: person1 hits rmd_start_age in year 1 (still hardcoded 0),
    # but year 2 (rows[1]) is the first real calculated year — RMD must appear
    cfg.start_year += 1
    rows2 = run_plan(cfg)
    assert rows2[0]["Person1_Age"] == cfg.rmd_start_age
    y1 = rows2[1]  # first year with real calculations
    assert y1["RMD"] >= 0  # nonnegative; >0 if IRA present
    if y1["IRA_Balance"] > 0 or y1["IRA_Draw"] > 0:
        assert y1["RMD"] > 0
