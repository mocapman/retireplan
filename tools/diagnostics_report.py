from __future__ import annotations

from typing import Iterable, Mapping, Any


DIAGNOSTIC_FIELDS = [
    "Year",
    "Person1_Age",
    "Person2_Age",
    "Filing",
    "Lifestyle",
    "Target_Spend",
    "Total_Spend",
    "Cash_Events",
    "Social_Security",
    "IRA_Draw",
    "Brokerage_Draw",
    "Roth_Draw",
    "Roth_Conversion",
    "RMD",
    "MAGI",
    "Target_MAGI",
    "MAGI_Remaining",
    "MAGI_Status",
    "ACA_Subsidy",
    "Std_Deduction",
    "Taxes_Due",
    "Shortfall",
    "IRA_Balance",
    "Brokerage_Balance",
    "Roth_Balance",
    "Total_Assets",
]


def build_diagnostic_report(rows: Iterable[Mapping[str, Any]]) -> str:
    """Return a readable year-by-year diagnostic report for run_plan rows."""
    rows = list(rows)
    fields = [field for field in DIAGNOSTIC_FIELDS if any(field in row for row in rows)]

    if not rows:
        return "No projection rows."

    header = " | ".join(fields)
    separator = " | ".join("---" for _ in fields)
    lines = [header, separator]

    for row in rows:
        lines.append(" | ".join(_format_value(row.get(field, "")) for field in fields))

    return "\n".join(lines)


def _format_value(value: Any) -> str:
    """Format report values without changing numeric meaning."""
    if value is None:
        return ""
    return str(value)
