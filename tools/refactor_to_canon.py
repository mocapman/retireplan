# tools/refactor_to_canon.py
from __future__ import annotations
import sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_DIRS = ["retireplan", "tests"]
EXCLUDE_DIRS = {".venv", "out", ".git", "__pycache__"}

# Old -> New (canonical) names
REPLACEMENTS = [
    ("Age_You", "Your_Age"),
    ("Age_Spouse", "Spouse_Age"),
    ("Phase", "Lifestyle"),
    # 'Living' remains internal if you still need it, but we don't emit it.
    ("Spend_Target", "Total_Spend"),
    ("Taxes\\b", "Taxes_Due"),  # whole-word 'Taxes' only
    ("Events_Cash", "Cash_Events"),
    ("Discretionary_Spend", "Base_Spend"),
    ("SS_Income", "Social_Security"),
    ("Draw_IRA", "IRA_Draw"),
    ("Draw_Brokerage", "Brokerage_Draw"),
    ("Draw_Roth", "Roth_Draw"),
    ("End_Bal_IRA", "IRA_Balance"),
    ("End_Bal_Brokerage", "Brokerage_Balance"),
    ("End_Bal_Roth", "Roth_Balance"),
    ("Roth Balance", "Roth_Balance"),  # labels caught in comments/strings
    ("Std_Deduction|Sted_Deduction", "Std_Deduction"),
    # Keep these as-is, listed for completeness
    # ("RMD","RMD"), ("MAGI","MAGI"), ("Total_Assets","Total_Assets"), ("Shortfall","Shortfall"),
]


# Files to process
def iter_files():
    for d in INCLUDE_DIRS:
        base = ROOT / d
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix not in {".py", ".yaml", ".yml", ".csv"}:
                continue
            if any(seg in EXCLUDE_DIRS for seg in p.parts):
                continue
            yield p


def apply_replacements(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = re.sub(old, new, text)
    return text


def main():
    changed = 0
    for p in iter_files():
        orig = p.read_text(encoding="utf-8")
        new = apply_replacements(orig)
        if new != orig:
            bak = p.with_suffix(p.suffix + ".bak")
            bak.write_text(orig, encoding="utf-8")
            p.write_text(new, encoding="utf-8")
            changed += 1
            print(f"Updated: {p.relative_to(ROOT)}  (backup: {bak.name})")
    print(f"\nFiles changed: {changed}")
    print("Done. Run your test suite next.")


if __name__ == "__main__":
    sys.exit(main())
