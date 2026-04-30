from __future__ import annotations

from typing import List, Dict, Any

from retireplan import inputs
from retireplan.engine.core import run_plan


def _rows_early_years(rows: List[Dict[str, Any]], n: int = 12) -> List[Dict[str, Any]]:
    return rows[: min(n, len(rows))]


def main() -> None:
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)

    print("=== Config checks ===")
    print(f"filing_status={cfg.filing_status} OK")
    print()

    print("=== Early-year budget breakdown ===")
    hdr = [
        "Year",
        "Filing",
        "Lifestyle",
        "Total_Spend",
        "Taxes_Due",
        "Social_Security",
        "IRA_Draw",
        "Brokerage_Draw",
        "Roth_Draw",
        "Roth_Conversion",
        "RMD",
        "MAGI",
        "Std_Deduction",
        "Shortfall",
    ]
    print(" ".join(f"{h:>10}" for h in hdr))
    for r in _rows_early_years(rows):
        print(
            f"{r['Year']:>4} {r['Filing']:<7} {r['Lifestyle']:<6} "
            f"{r['Total_Spend']:>10} {r['Taxes_Due']:>8} {r['Social_Security']:>6} "
            f"{r['IRA_Draw']:>9} {r['Brokerage_Draw']:>12} {r['Roth_Draw']:>9} "
            f"{r['Roth_Conversion']:>14} {r['RMD']:>6} {r['MAGI']:>8} "
            f"{r['Std_Deduction']:>13} {r['Shortfall']:>9}"
        )


if __name__ == "__main__":
    main()
