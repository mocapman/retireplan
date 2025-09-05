from __future__ import annotations

import pandas as pd

COLUMNS = [
    "Year",
    "Age_You",
    "Age_Spouse",
    "Phase",
    "Living",
    "Spend_Target",
    "Taxes",
    "Total_Spend",
    "SS_Income",
    "Draw_Brokerage",
    "Draw_Roth",
    "Draw_IRA",
    "Roth_Conversion",
    "RMD",
    "MAGI",
    "Std_Deduction",
    "End_Bal_Brokerage",
    "End_Bal_Roth",
    "End_Bal_IRA",
    "Total_Assets",
]


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=COLUMNS)
    return df
