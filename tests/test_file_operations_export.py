import csv
from pathlib import Path
from types import SimpleNamespace

import retireplan.gui.file_operations as file_operations
from retireplan import schema
from retireplan.gui.file_operations import FileOperations


class ResultsDisplayStub:
    def __init__(self, rows):
        self._rows = rows

    def get_current_rows(self):
        return self._rows


def test_export_csv_writes_projection_rows_only_under_output(monkeypatch, tmp_path):
    row = {key: None for key in schema.keys()}
    row.update(
        {
            "Year": 2025,
            "Brokerage_Cash_Used": 500,
            "Brokerage_Holdings_Sold": 300,
            "Brokerage_Basis_Used": 237,
            "Brokerage_Gain_Ratio": 0.2105263158,
            "Brokerage_Capital_Gains": 63,
            "Brokerage_MAGI_Income": 63,
            "Federal_Tax": 99,
            "Taxable_Income": 988,
            "Ordinary_Income_Taxable": 1000,
            "Capital_Gains_Taxable": 63,
            "Total_Taxable_Income_Before_Deduction": 1063,
            "Total_Taxable_Income_After_Deduction": 988,
            "Estimated_State_Taxable_Income": 888,
            "Estimated_State_Tax": 89,
            "SS_Taxable_Amount": 0,
            "Roth_Conversion_Taxable_Income": 0,
            "IRA_Taxable_Income": 1000,
        }
    )
    app = SimpleNamespace(
        cfg=SimpleNamespace(draw_order="Brokerage, Roth, IRA", target_spend=1000),
        results_display=ResultsDisplayStub([row]),
    )
    info_messages = []

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        file_operations.messagebox,
        "showinfo",
        lambda title, message: info_messages.append((title, message)),
    )
    monkeypatch.setattr(
        file_operations.messagebox,
        "showwarning",
        lambda title, message: (_ for _ in ()).throw(AssertionError(message)),
    )
    monkeypatch.setattr(
        file_operations.messagebox,
        "showerror",
        lambda title, message: (_ for _ in ()).throw(AssertionError(message)),
    )

    FileOperations(app).export_csv()

    exported_files = list((tmp_path / "output").glob("Projections_*.csv"))
    assert len(exported_files) == 1
    assert info_messages

    with exported_files[0].open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[0] == schema.labels()
    assert "Brokerage_Capital_Gains" in rows[0]
    assert "Brokerage_MAGI_Income" in rows[0]
    assert "Federal_Tax" in rows[0]
    assert "Taxable_Income" in rows[0]
    assert "Ordinary_Income_Taxable" in rows[0]
    assert "Total_Taxable_Income_Before_Deduction" in rows[0]
    assert "Roth_Conversion_Taxable_Income" in rows[0]
    assert "SS_Taxable_Amount" in rows[0]
    assert "Estimated_State_Taxable_Income" in rows[0]
    assert "Estimated_State_Tax" in rows[0]
    assert len(rows) == 2
    assert ["# Config Settings"] not in rows
    assert not any(row and row[0].startswith("tax_health.") for row in rows)


def test_output_folder_is_ignored_by_git():
    gitignore = Path(".gitignore").read_text(encoding="utf-8").splitlines()

    assert "output/" in {line.strip() for line in gitignore}
