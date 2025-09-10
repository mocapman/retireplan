# precision.py
from __future__ import annotations
from typing import Any, Dict, List, Callable
from decimal import Decimal, ROUND_HALF_UP
import math

# Precision settings
DOLLAR_PRECISION = 0  # Whole dollars
PERCENT_PRECISION = 4  # 4 decimal places for percentages
YEAR_PRECISION = 0  # Whole years
COUNT_PRECISION = 0  # Whole numbers


# Rounding functions
def round_dollar(value: Any) -> int:
    """Round to whole dollars"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return int(value.quantize(Decimal("1."), rounding=ROUND_HALF_UP))
    return round(value) if value is not None else None


def round_percent(value: Any) -> float:
    """Round to 4 decimal places for percentages"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value.quantize(Decimal("1.0000"), rounding=ROUND_HALF_UP))
    return round(value, 4) if value is not None else None


def round_year(value: Any) -> int:
    """Round to whole years"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return int(value.quantize(Decimal("1."), rounding=ROUND_HALF_UP))
    return round(value) if value is not None else None


def round_count(value: Any) -> int:
    """Round to whole numbers"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return int(value.quantize(Decimal("1."), rounding=ROUND_HALF_UP))
    return round(value) if value is not None else None


# Column-specific rounding rules
ROUNDING_RULES: Dict[str, Callable[[Any], Any]] = {
    # Dollar amounts
    "Total_Spend": round_dollar,
    "Taxes_Due": round_dollar,
    "Cash_Events": round_dollar,
    "Target_Spend": round_dollar,
    "Social_Security": round_dollar,
    "IRA_Draw": round_dollar,
    "Brokerage_Draw": round_dollar,
    "Roth_Draw": round_dollar,
    "Roth_Conversion": round_dollar,
    "RMD": round_dollar,
    "MAGI": round_dollar,
    "Std_Deduction": round_dollar,
    "IRA_Balance": round_dollar,
    "Brokerage_Balance": round_dollar,
    "Roth_Balance": round_dollar,
    "Total_Assets": round_dollar,
    "Shortfall": round_dollar,
    # Years and counts
    "Year": round_year,
    "Person1_Age": round_year,
    "Person2_Age": round_year,
    # Percentages (if any)
    # "Some_Percentage_Column": round_percent,
}


def round_value(key: str, value: Any) -> Any:
    """Round a value based on its column key"""
    if value is None:
        return None

    if key in ROUNDING_RULES:
        return ROUNDING_RULES[key](value)

    # Default: return as-is for non-numeric or string columns
    return value


def round_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Round all values in a row according to their column rules"""
    return {k: round_value(k, v) for k, v in row.items()}


def round_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Round all values in all rows according to their column rules"""
    return [round_row(row) for row in rows]
