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
    {"key": "Total_Spend", "label": "Total_Spend", "visible": True},
    {"key": "Taxes_Due", "label": "Taxes_Due", "visible": True},
    {"key": "Cash_Events", "label": "Cash_Events", "visible": True},
    {"key": "Base_Spend", "label": "Base_Spend", "visible": True},
    {"key": "Social_Security", "label": "Social_Security", "visible": True},
    {"key": "IRA_Draw", "label": "IRA_Draw", "visible": True},
    {"key": "Brokerage_Draw", "label": "Brokerage_Draw", "visible": True},
    {"key": "Roth_Draw", "label": "Roth_Draw", "visible": True},
    {"key": "Roth_Conversion", "label": "Roth_Conversion", "visible": True},
    {"key": "RMD", "label": "RMD", "visible": True},
    # Default hidden in GUI
    {"key": "MAGI", "label": "MAGI", "visible": False},
    {"key": "Std_Deduction", "label": "Std_Deduction", "visible": False},
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


def visible_keys() -> List[str]:
    """Keys that default to visible in the GUI."""
    return [c["key"] for c in COLUMNS if c.get("visible", True)]


def columns() -> List[Dict[str, Any]]:
    """Raw schema (do not mutate in-place)."""
    return [dict(c) for c in COLUMNS]
