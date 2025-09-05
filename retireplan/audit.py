from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from retireplan import inputs
from retireplan.engine import run_plan


@dataclass
class AuditSummary:
    rows: int
    errors: int


def audit_rows_against_cfg(
    _cfg, rows: List[Dict[str, Any]], verbose: bool = False
) -> AuditSummary:
    """
    Lightweight identities using canon keys. Keep as-is; replace only names.
    """
    errs = 0
    for r in rows:
        ta = (
            (r.get("IRA_Balance", 0) or 0)
            + (r.get("Brokerage_Balance", 0) or 0)
            + (r.get("Roth_Balance", 0) or 0)
        )
        if ta != r.get("Total_Assets", 0):
            if verbose:
                print(
                    f"[{r.get('Year')}] Total_Assets exp {ta} got {r.get('Total_Assets')}"
                )
            errs += 1
    return AuditSummary(rows=len(rows), errors=errs)


def main() -> None:
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    s = audit_rows_against_cfg(cfg, rows, verbose=True)
    print(
        f"Rows audited: {s.rows}  |  Result: {'OK' if s.errors == 0 else f'{s.errors} issues'}"
    )


if __name__ == "__main__":
    main()
