from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import csv

from retireplan import inputs, schema
from retireplan.engine import run_plan


def _print_cut(rows: List[Dict[str, Any]], note: str | None = None) -> None:
    hdr = [
        "Year",
        "Your_Age",
        "Spouse_Age",
        "Lifestyle",
        "Filing",
        "Total_Spend",
        "Taxes_Due",
        "Social_Security",
        "IRA_Draw",
        "Brokerage_Draw",
        "Roth_Draw",
        "Roth_Conversion",
        "RMD",
        "MAGI",
        "Shortfall",
        "IRA_Balance",
        "Brokerage_Balance",
        "Roth_Balance",
        "Total_Assets",
        "View",
        "Note",
    ]
    print("  " + "  ".join(hdr))
    for r in rows:
        print(
            f"{r['Year']:<6} {r['Your_Age']:<8} {r['Spouse_Age']:<11} "
            f"{r['Lifestyle']:<5} {r['Filing']:<5}  "
            f"{r['Total_Spend']:<12} {r['Taxes_Due']:<5} {r['Social_Security']:<9} "
            f"{r['IRA_Draw']:<8} {r['Brokerage_Draw']:<14} {r['Roth_Draw']:<9} "
            f"{r['Roth_Conversion']:<15} {r['RMD']:<5} {r['MAGI']:<6} "
            f"{r['Shortfall']:<9} {r['IRA_Balance']:<11} {r['Brokerage_Balance']:<16} "
            f"{r['Roth_Balance']:<11} {r['Total_Assets']:<12} "
            f"{r.get('View',''):<12} {note or r.get('Note','')}"
        )


def _write_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    keys = schema.keys()
    headers = schema.labels()
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        for r in rows:
            w.writerow([r.get(k, None) for k in keys])


def main() -> None:
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)

    # Baseline
    print("=== baseline_ira_first ===")
    rows = run_plan(cfg)
    _print_cut(rows, note=None)
    _write_csv(rows, out_dir / "baseline_ira_first.csv")

    # Alternate
    print("\n=== alt_brokerage_first ===")
    cfg2 = inputs.load_yaml("examples/sample_inputs.yaml")
    cfg2.draw_order = "Brokerage, Roth, IRA"
    rows2 = run_plan(cfg2)
    _print_cut(rows2, note=None)
    _write_csv(rows2, out_dir / "alt_brokerage_first.csv")

    print("\nWrote scenario CSVs and summaries to:", out_dir)


if __name__ == "__main__":
    main()
