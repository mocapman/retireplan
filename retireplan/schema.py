from __future__ import annotations

from typing import List, Dict, Any


# Canonical column schema used by engine outputs, CSV, GUI, diagnostics, scenarios, and audit.
# No widths or types here. Labels == keys to avoid any renaming layer.
COLUMNS: List[Dict[str, Any]] = [
    {"key": "Year", "label": "Year", "visible": True},
    {"key": "Person1_Age", "label": "Person1_Age", "visible": True},
    {"key": "Person2_Age", "label": "Person2_Age", "visible": True},
    {"key": "Filing", "label": "Filing", "visible": True},
    {"key": "Lifestyle", "label": "Lifestyle", "visible": True},
    {"key": "Target_Spend", "label": "Target_Spend", "visible": True},
    {"key": "ACA_Premium", "label": "ACA_Premium", "visible": True},
    {"key": "Total_Spend", "label": "Total_Spend", "visible": True},
    {"key": "Taxes_Due", "label": "Taxes_Due", "visible": True},
    {"key": "Social_Security", "label": "Social_Security", "visible": True},
    {"key": "IRA_Draw", "label": "IRA_Draw", "visible": True},
    {"key": "Brokerage_Draw", "label": "Brokerage_Draw", "visible": True},
    {"key": "Roth_Draw", "label": "Roth_Draw", "visible": True},
    {"key": "Roth_Conversion", "label": "Roth_Conversion", "visible": True},
    {"key": "RMD", "label": "RMD", "visible": True},
    # Default hidden in GUI
    {"key": "Federal_Tax", "label": "Federal_Tax", "visible": False},
    {"key": "Filing_Status_Used", "label": "Filing_Status_Used", "visible": False},
    {
        "key": "Federal_Standard_Deduction_Used",
        "label": "Federal_Standard_Deduction_Used",
        "visible": False,
    },
    {
        "key": "Federal_Tax_Bracket_Set_Used",
        "label": "Federal_Tax_Bracket_Set_Used",
        "visible": False,
    },
    {
        "key": "Federal_Taxable_Income_Before_Deduction",
        "label": "Federal_Taxable_Income_Before_Deduction",
        "visible": False,
    },
    {
        "key": "Federal_Taxable_Income_After_Deduction",
        "label": "Federal_Taxable_Income_After_Deduction",
        "visible": False,
    },
    {
        "key": "Estimated_State_Taxable_Income",
        "label": "Estimated_State_Taxable_Income",
        "visible": False,
    },
    {"key": "Estimated_State_Tax", "label": "Estimated_State_Tax", "visible": False},
    {"key": "Brokerage_Cash_Used", "label": "Brokerage_Cash_Used", "visible": False},
    {
        "key": "Brokerage_Holdings_Sold",
        "label": "Brokerage_Holdings_Sold",
        "visible": False,
    },
    {"key": "Brokerage_Basis_Used", "label": "Brokerage_Basis_Used", "visible": False},
    {"key": "Brokerage_Gain_Ratio", "label": "Brokerage_Gain_Ratio", "visible": False},
    {
        "key": "Brokerage_Capital_Gains",
        "label": "Brokerage_Capital_Gains",
        "visible": False,
    },
    {"key": "MAGI", "label": "MAGI", "visible": True},
    {"key": "MAGI_Floor", "label": "MAGI_Floor", "visible": False},
    {"key": "Target_MAGI", "label": "Target_MAGI", "visible": False},
    {"key": "MAGI_Ceiling", "label": "MAGI_Ceiling", "visible": False},
    {"key": "MAGI_Remaining", "label": "MAGI_Remaining", "visible": False},
    {
        "key": "MAGI_Remaining_To_Ceiling",
        "label": "MAGI_Remaining_To_Ceiling",
        "visible": False,
    },
    {"key": "MAGI_Status", "label": "MAGI_Status", "visible": False},
    {"key": "Survivor_Year", "label": "Survivor_Year", "visible": False},
    {"key": "Living_Person", "label": "Living_Person", "visible": False},
    {"key": "Widow_Tax_Mode", "label": "Widow_Tax_Mode", "visible": False},
    {
        "key": "Survivor_Spending_Used",
        "label": "Survivor_Spending_Used",
        "visible": False,
    },
    {
        "key": "Survivor_Filing_Status_Used",
        "label": "Survivor_Filing_Status_Used",
        "visible": False,
    },
    {
        "key": "Survivor_Standard_Deduction_Used",
        "label": "Survivor_Standard_Deduction_Used",
        "visible": False,
    },
    {
        "key": "IRA_Balance_Start_Of_Year",
        "label": "IRA_Balance_Start_Of_Year",
        "visible": False,
    },
    {"key": "IRA_Taxable_Income", "label": "IRA_Taxable_Income", "visible": False},
    {
        "key": "IRA_RMD_Taxable_Income",
        "label": "IRA_RMD_Taxable_Income",
        "visible": False,
    },
    {
        "key": "IRA_Extra_Draw_Taxable_Income",
        "label": "IRA_Extra_Draw_Taxable_Income",
        "visible": False,
    },
    {
        "key": "IRA_Balance_End_Of_Year",
        "label": "IRA_Balance_End_Of_Year",
        "visible": False,
    },
    {"key": "RMD_Gross", "label": "RMD_Gross", "visible": False},
    {
        "key": "RMD_Used_For_Spending",
        "label": "RMD_Used_For_Spending",
        "visible": False,
    },
    {
        "key": "RMD_Surplus_To_Brokerage",
        "label": "RMD_Surplus_To_Brokerage",
        "visible": False,
    },
    {
        "key": "Roth_Conversion_Taxable_Income",
        "label": "Roth_Conversion_Taxable_Income",
        "visible": False,
    },
    {"key": "SS_Person1_Gross", "label": "SS_Person1_Gross", "visible": False},
    {"key": "SS_Person2_Gross", "label": "SS_Person2_Gross", "visible": False},
    {"key": "SS_Total_Gross", "label": "SS_Total_Gross", "visible": False},
    {"key": "SS_Taxable_Amount", "label": "SS_Taxable_Amount", "visible": False},
    {
        "key": "SS_Nontaxable_Amount",
        "label": "SS_Nontaxable_Amount",
        "visible": False,
    },
    {
        "key": "SS_Survivor_Adjustment",
        "label": "SS_Survivor_Adjustment",
        "visible": False,
    },
    {
        "key": "SS_Filing_Status_Used",
        "label": "SS_Filing_Status_Used",
        "visible": False,
    },
    {"key": "IRA_Balance", "label": "IRA_Balance", "visible": True},
    {"key": "Brokerage_Balance", "label": "Brokerage_Balance", "visible": True},
    {"key": "Roth_Balance", "label": "Roth_Balance", "visible": True},
    {"key": "Total_Assets", "label": "Total_Assets", "visible": True},
    # Default hidden in GUI
    {"key": "Shortfall", "label": "Shortfall", "visible": False},
]


def keys() -> List[str]:
    """Canonical keys in schema order."""
    return [c["key"] for c in COLUMNS]


def labels() -> List[str]:
    """Column labels in schema order."""
    return [c["label"] for c in COLUMNS]


GUI_LABELS = {
    "Person1_Age": "Age1",
    "Person2_Age": "Age2",
    "Lifestyle": "Phase",
    "Target_Spend": "Spend",
    "ACA_Premium": "ACA Prem",
    "Total_Spend": "Total",
    "Taxes_Due": "Taxes",
    "Social_Security": "SS",
    "IRA_Draw": "IRA Draw",
    "Brokerage_Draw": "Brkg Draw",
    "Roth_Draw": "Roth Draw",
    "Roth_Conversion": "Roth Conv",
    "IRA_Balance": "IRA Bal",
    "Brokerage_Balance": "Brkg Bal",
    "Roth_Balance": "Roth Bal",
    "Total_Assets": "Assets",
}


def gui_label(key: str) -> str:
    """Compact label for the visible GUI table only."""
    return GUI_LABELS.get(key, key)


def visible_keys() -> List[str]:
    """Keys that default to visible in the GUI."""
    return [c["key"] for c in COLUMNS if c.get("visible", True)]


def columns() -> List[Dict[str, Any]]:
    """Raw schema (do not mutate in-place)."""
    return [dict(c) for c in COLUMNS]
