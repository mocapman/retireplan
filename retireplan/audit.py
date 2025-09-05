from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from retireplan import inputs, projections
from retireplan.engine import run_plan
from retireplan.taxes import compute_tax_magi


@dataclass
class AuditSummary:
    rows: int
    errors: int


def _filing_this_year(cfg, living: str) -> str:
    return "MFJ" if (cfg.filing_status == "MFJ" and living == "Joint") else "Single"


def _close(a: float, b: float, tol: float = 2.0) -> bool:
    return abs(float(a) - float(b)) <= tol


def audit_rows_against_cfg(cfg, rows: list[dict], verbose: bool = False) -> AuditSummary:
    errs = 0

    # Start balances for the first row from cfg; for subsequent rows use REPORTED prior ends
    b_start = float(cfg.balances_brokerage)
    r_start = float(cfg.balances_roth)
    i_start = float(cfg.balances_ira)

    for idx, row in enumerate(rows):
        y = int(row["Year"])

        # 1) Identity: Total_Spend = Spend_Target + Taxes + Events_Cash
        total_spend_expected = (
            float(row["Spend_Target"]) + float(row["Taxes"]) + float(row["Events_Cash"])
        )
        if not _close(round(total_spend_expected), float(row["Total_Spend"])):
            errs += 1
            if verbose:
                print(
                    f"[{y}] Total_Spend exp {round(total_spend_expected)} got {row['Total_Spend']}"
                )

        # 2) Identity: Shortfall = max(0, Total_Spend - SS_Income - sum(draws))
        need = max(0.0, float(row["Total_Spend"]) - float(row["SS_Income"]))
        draws_sum = float(row["Draw_Brokerage"]) + float(row["Draw_Roth"]) + float(row["Draw_IRA"])
        shortfall_expected = max(0.0, need - draws_sum)
        if not _close(round(shortfall_expected), float(row["Shortfall"])):
            errs += 1
            if verbose:
                print(f"[{y}] Shortfall exp {round(shortfall_expected)} got {row['Shortfall']}")

        # 3) Taxes/MAGI recompute (based on displayed IRA draw and SS income)
        filing = _filing_this_year(cfg, str(row["Living"]))
        tax2, _ss_tax2, _taxable2, magi2 = compute_tax_magi(
            ira_ordinary=float(row["Draw_IRA"]),
            roth_conversion=0.0,
            ss_total=float(row["SS_Income"]),
            std_deduction=float(row["Std_Deduction"]),
            filing=filing,
        )
        if not _close(round(tax2), float(row["Taxes"])):
            errs += 1
            if verbose:
                print(f"[{y}] Taxes exp {round(tax2)} got {row['Taxes']}")
        if not _close(round(magi2), float(row["MAGI"])):
            errs += 1
            if verbose:
                print(f"[{y}] MAGI exp {round(magi2)} got {row['MAGI']}")

        # 4) End balances recompute using REPORTED prior ends as next starts
        if idx > 0:
            # use the previous row's reported ends as this row's starts
            prev = rows[idx - 1]
            b_start = float(prev["End_Bal_Brokerage"])
            r_start = float(prev["End_Bal_Roth"])
            i_start = float(prev["End_Bal_IRA"])

        # clamp negatives caused by rounded draws crossing the true balance
        b_end_exp = max(0.0, b_start - float(row["Draw_Brokerage"]))
        r_end_exp = max(0.0, r_start - float(row["Draw_Roth"]))
        i_end_exp = max(0.0, i_start - float(row["Draw_IRA"]))

        b_end_exp *= 1.0 + float(cfg.brokerage_growth)
        r_end_exp *= 1.0 + float(cfg.roth_growth)
        i_end_exp *= 1.0 + float(cfg.ira_growth)

        if not _close(round(b_end_exp), float(row["End_Bal_Brokerage"])):
            errs += 1
            if verbose:
                print(
                    f"[{y}] End_Bal_Brokerage exp {round(b_end_exp)} got {row['End_Bal_Brokerage']}"
                )
        if not _close(round(r_end_exp), float(row["End_Bal_Roth"])):
            errs += 1
            if verbose:
                print(f"[{y}] End_Bal_Roth exp {round(r_end_exp)} got {row['End_Bal_Roth']}")
        if not _close(round(i_end_exp), float(row["End_Bal_IRA"])):
            errs += 1
            if verbose:
                print(f"[{y}] End_Bal_IRA exp {round(i_end_exp)} got {row['End_Bal_IRA']}")

        total_assets_exp = round(
            float(row["End_Bal_Brokerage"]) + float(row["End_Bal_Roth"]) + float(row["End_Bal_IRA"])
        )
        if not _close(total_assets_exp, float(row["Total_Assets"])):
            errs += 1
            if verbose:
                print(f"[{y}] Total_Assets exp {total_assets_exp} got {row['Total_Assets']}")

        # next loop will take this row's reported ends as starts (handled above)

    return AuditSummary(rows=len(rows), errors=errs)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Audit projection math.")
    p.add_argument("--csv", help="Path to projections CSV. If omitted, audits engine output.")
    p.add_argument("--cfg", default="examples/sample_inputs.yaml", help="Path to inputs YAML.")
    p.add_argument("--verbose", action="store_true", help="Print mismatches.")
    args = p.parse_args(argv)

    cfg = inputs.load_yaml(args.cfg)
    if args.csv:
        path = Path(args.csv)
        if not path.exists():
            print(f"File not found: {path}")
            return 2
        df = pd.read_csv(path)
        missing = set(projections.COLUMNS) - set(df.columns)
        if missing:
            print(f"CSV missing columns: {', '.join(sorted(missing))}")
            return 2
        rows = df.to_dict(orient="records")
    else:
        rows = run_plan(cfg)

    s = audit_rows_against_cfg(cfg, rows, verbose=args.verbose)
    print(f"Rows audited: {s.rows}  |  Result: {'OK' if s.errors == 0 else f'{s.errors} issues'}")
    return 0 if s.errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
