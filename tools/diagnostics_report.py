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
    "Social_Security",
    "IRA_Draw",
    "Brokerage_Draw",
    "Brokerage_Cash_Used",
    "Brokerage_Holdings_Sold",
    "Brokerage_Basis_Used",
    "Brokerage_Gain_Ratio",
    "Brokerage_Capital_Gains",
    "Brokerage_MAGI_Income",
    "Roth_Draw",
    "Roth_Conversion",
    "RMD",
    "Federal_Tax",
    "Filing_Status_Used",
    "Federal_Standard_Deduction_Used",
    "Federal_Tax_Bracket_Set_Used",
    "Taxable_Income",
    "Ordinary_Income_Taxable",
    "Capital_Gains_Taxable",
    "Total_Taxable_Income_Before_Deduction",
    "Total_Taxable_Income_After_Deduction",
    "Federal_Taxable_Income_Before_Deduction",
    "Federal_Taxable_Income_After_Deduction",
    "Federal_Tax_On_Ordinary_Income",
    "Estimated_State_Taxable_Income",
    "Estimated_State_Tax",
    "IRA_Taxable_Income",
    "IRA_Draw_Taxable_Income",
    "IRA_RMD_Taxable_Income",
    "IRA_Extra_Draw_Taxable_Income",
    "RMD_Gross",
    "RMD_Used_For_Spending",
    "RMD_Surplus_To_Brokerage",
    "Roth_Conversion_Gross",
    "Roth_Conversion_Taxable_Income",
    "Roth_Conversion_MAGI_Income",
    "MAGI",
    "MAGI_Floor",
    "Target_MAGI",
    "MAGI_Ceiling",
    "MAGI_Remaining",
    "MAGI_Remaining_To_Ceiling",
    "MAGI_Status",
    "MAGI_IRA_Draws",
    "MAGI_RMD",
    "MAGI_Roth_Conversions",
    "MAGI_Brokerage_Gains",
    "MAGI_Social_Security",
    "Brokerage_Taxable_Income",
    "SS_Person1_Gross",
    "SS_Person2_Gross",
    "SS_Total_Gross",
    "SS_Taxable_Amount",
    "SS_Nontaxable_Amount",
    "SS_Included_In_MAGI",
    "SS_Survivor_Adjustment",
    "SS_Filing_Status_Used",
    "Std_Deduction",
    "Survivor_Year",
    "Living_Person",
    "Widow_Tax_Mode",
    "Survivor_Spending_Used",
    "Survivor_Filing_Status_Used",
    "Survivor_Standard_Deduction_Used",
    "IRA_Balance_Start_Of_Year",
    "IRA_Total_Taxable_Income",
    "IRA_Balance_End_Of_Year",
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
