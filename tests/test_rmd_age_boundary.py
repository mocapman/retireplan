from retireplan import inputs
from retireplan.engine.engine import run_plan


def _age(cfg, year):
    return year - cfg.birth_year_you


def test_rmd_triggers_only_at_start_age():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    # Year so that Age_You == rmd_start_age - 1
    cfg.start_year = cfg.birth_year_you + cfg.rmd_start_age - 1
    rows = run_plan(cfg)
    y0 = rows[0]
    assert y0["Your_Age"] == cfg.rmd_start_age - 1
    assert y0["RMD"] == 0

    # Next year, RMD must appear (if IRA balance > 0)
    cfg.start_year += 1
    rows2 = run_plan(cfg)
    y1 = rows2[0]
    assert y1["Your_Age"] == cfg.rmd_start_age
    assert y1["RMD"] >= 0  # nonnegative; >0 if IRA present
    if y1["IRA_Balance"] > 0 or y1["IRA_Draw"] > 0:
        assert y1["RMD"] > 0
