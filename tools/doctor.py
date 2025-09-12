# retireplan/doctor.py
from __future__ import annotations

import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PKGS = [
    "pandas",
    "numpy",
    "PySimpleGUI",
    "matplotlib",
    "openpyxl",
    "PyYAML",
    "pytest",
    "black",
    "ruff",
    "mypy",
]

FILES = [
    "retireplan/__init__.py",
    "retireplan/gui.py",
    "retireplan/theme.py",
    "retireplan/inputs.py",
    "retireplan/policy.py",
    "retireplan/core.py",
    "retireplan/accounts.py",
    "retireplan/taxes.py",
    "retireplan/social_security.py",
    "retireplan/spending.py",
    "retireplan/projections.py",
    "retireplan/io_csv.py",
]


def pkg_ver(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "NOT INSTALLED"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    print("=== RetirePlan Doctor ===")
    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    print(f"OS: {platform.system()} {platform.release()}\n")

    # Packages
    print("Packages:")
    missing = 0
    for p in PKGS:
        v = pkg_ver(p)
        if v == "NOT INSTALLED":
            missing += 1
        print(f"  - {p:14} {v}")
    print()

    # Files
    print("Project files:")
    missing_files = 0
    for rel in FILES:
        exists = (root / rel).exists()
        if not exists:
            missing_files += 1
        print(f"  - {rel:30} {'OK' if exists else 'MISSING'}")
    print()

    # Theme smoke test (no window)
    theme_ok = True
    try:
        import PySimpleGUI as sg  # noqa
        from retireplan import theme

        theme.apply()
    except Exception as e:
        theme_ok = False
        print(f"Theme error: {e!r}")

    print(f"Theme: {'OK' if theme_ok else 'FAILED'}")

    total_errors = missing + missing_files + (0 if theme_ok else 1)
    print(f"\nSummary: {('OK' if total_errors==0 else f'{total_errors} issues found')}")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
