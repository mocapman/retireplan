from retireplan import inputs
from retireplan.audit import audit_rows_against_cfg
from retireplan.engine import run_plan


def test_engine_identities_hold():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    summary = audit_rows_against_cfg(cfg, rows, verbose=True)
    assert summary.errors == 0
