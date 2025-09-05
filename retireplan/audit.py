from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # only needed for --csv

from retireplan import inputs
from retireplan.engine import run_plan


@dataclass
class AuditSummary:
    rows: int
    errors: int


def _rmd_surplus(row: Dict) -> float:
    # Gross-budget model: sweep only RMD beyond need after SS
    need_after_ss = max(0.0, row["Total_Spend"] - row["SS_Income"])
    return max(0.0, row["RMD"] - need_after_ss)


def audit_rows_against_cfg(
    cfg, rows: List[Dict], verbose: bool = False
) -> AuditSummary:
    errs = 0
    tol = 2  # rounding tolerance

    # Growth rates from cfg
    g_b = cfg.brokerage_growth
    g_r = cfg.roth_growth
    g_i = cfg.ira_growth

    for t, r in enumerate(rows):
        # Identity 1: Total_Spend equals Spend_Target (budget)
        if abs(r["Total_Spend"] - r["Spend_Target"]) > tol:
            errs += 1
            if verbose:
                print(
                    f"[{int(r['Year'])}] Total_Spend exp {r['Spend_Target']} got {r['Total_Spend']}"
                )

        # Identity 2: Provided + Shortfall equals budget
        provided = (
            r["SS_Income"]
            + r["RMD"]
            + r["Draw_IRA"]
            + r["Draw_Brokerage"]
            + r["Draw_Roth"]
        )
        if abs((provided + r["Shortfall"]) - r["Spend_Target"]) > tol:
            errs += 1
            if verbose:
                print(
                    f"[{int(r['Year'])}] Provided+Shortfall exp {r['Spend_Target']} got {provided + r['Shortfall']}"
                )

        # Identity 3: End balances growth from prior year
        if t > 0:
            p = rows[t - 1]
            b0, r0, i0 = p["End_Bal_Brokerage"], p["End_Bal_Roth"], p["End_Bal_IRA"]

            rmd_sur = _rmd_surplus(r)

            b_exp = round((b0 - r["Draw_Brokerage"] + rmd_sur) * (1 + g_b))
            r_exp = round((r0 - r["Draw_Roth"] + r["Roth_Conversion"]) * (1 + g_r))
            i_exp = round(
                (i0 - r["RMD"] - r["Draw_IRA"] - r["Roth_Conversion"]) * (1 + g_i)
            )

            if abs(b_exp - r["End_Bal_Brokerage"]) > tol:
                errs += 1
                if verbose:
                    print(
                        f"[{int(r['Year'])}] End_Bal_Brokerage exp {b_exp} got {r['End_Bal_Brokerage']}"
                    )
            if abs(r_exp - r["End_Bal_Roth"]) > tol:
                errs += 1
                if verbose:
                    print(
                        f"[{int(r['Year'])}] End_Bal_Roth exp {r_exp} got {r['End_Bal_Roth']}"
                    )
            if abs(i_exp - r["End_Bal_IRA"]) > tol:
                errs += 1
                if verbose:
                    print(
                        f"[{int(r['Year'])}] End_Bal_IRA exp {i_exp} got {r['End_Bal_IRA']}"
                    )

    return AuditSummary(rows=len(rows), errors=errs)


def _load_rows_from_csv(path: Path) -> List[Dict]:
    if pd is None:
        raise RuntimeError("pandas not available for CSV read")
    df = pd.read_csv(path)
    return df.to_dict("records")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Audit retireplan engine outputs.")
    ap.add_argument("--csv", help="CSV of projections to audit")
    ap.add_argument("--cfg", default="examples/sample_inputs.yaml")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    cfg = inputs.load_yaml(args.cfg)
    rows = _load_rows_from_csv(Path(args.csv)) if args.csv else run_plan(cfg)
    summary = audit_rows_against_cfg(cfg, rows, verbose=args.verbose)

    if args.verbose and summary.errors:
        pass
    print(
        f"Rows audited: {summary.rows}  |  Result: {'OK' if summary.errors == 0 else f'{summary.errors} issues'}"
    )
    return 0 if summary.errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
