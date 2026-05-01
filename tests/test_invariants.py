from dataclasses import dataclass
from retireplan import inputs
from retireplan.engine.core import run_plan


@dataclass
class AuditSummary:
    errors: int


def audit_rows_against_cfg(cfg, rows, verbose=False):
    errors = 0
    for row in rows:
        total = row["IRA_Balance"] + row["Brokerage_Balance"] + row["Roth_Balance"]
        if abs(int(total) - int(row["Total_Assets"])) > 1:
            errors += 1
            if verbose:
                print(
                    f"Year {row['Year']}: Total_Assets mismatch: "
                    f"{total} vs {row['Total_Assets']}"
                )
    return AuditSummary(errors=errors)


def test_engine_identities_hold():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    summary = audit_rows_against_cfg(cfg, rows, verbose=True)
    assert summary.errors == 0
