from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tksheet import Sheet
from typing import Any, List

from retireplan.projections import to_2d_for_table


APP_GEOMETRY = "2525x1150"

SUMMARY_FIELDS = (
    ("Federal Tax", "Federal_Tax", "#0f172a", "#e0f2fe"),
    ("State Tax", "Estimated_State_Tax", "#172554", "#dbeafe"),
    ("Lifetime Taxes", "Taxes_Due", "#312e81", "#ede9fe"),
    ("Ending Assets", "Total_Assets", "#064e3b", "#dcfce7"),
)


def format_currency(val):
    try:
        val = float(val)
        return "${:,.0f}".format(val)
    except Exception:
        return val


def calculate_results_summary(rows: List[dict]) -> dict[str, float]:
    """Summarize existing projection rows for the results status bar."""
    if not rows:
        return {
            "Federal_Tax": 0,
            "Estimated_State_Tax": 0,
            "Taxes_Due": 0,
            "Total_Assets": 0,
        }

    return {
        "Federal_Tax": sum(_as_number(row.get("Federal_Tax")) for row in rows),
        "Estimated_State_Tax": sum(
            _as_number(row.get("Estimated_State_Tax")) for row in rows
        ),
        "Taxes_Due": sum(_as_number(row.get("Taxes_Due")) for row in rows),
        "Total_Assets": _as_number(rows[-1].get("Total_Assets")),
    }


def _as_number(value) -> float:
    try:
        if value in ("", None):
            return 0
        return float(value)
    except (TypeError, ValueError):
        return 0


def format_input_snapshot(cfg: Any) -> str:
    """Return a compact scenario-input summary for the results history."""
    if cfg is None:
        return "Inputs: unavailable"

    return "Inputs: " + " | ".join(
        f"{label}: {value}" for label, value in _input_snapshot_items(cfg)
    )


def format_input_changes(cfg: Any, baseline_cfg: Any) -> str:
    """Return only scenario inputs that differ from the startup config."""
    if cfg is None or baseline_cfg is None:
        return format_input_snapshot(cfg)

    current = _input_snapshot_items(cfg)
    baseline = dict(_input_snapshot_items(baseline_cfg))
    changes = [
        f"{label}: {baseline.get(label, 'n/a')} -> {value}"
        for label, value in current
        if baseline.get(label) != value
    ]
    if not changes:
        return "Inputs: No changes from default config"
    return "Inputs changed: " + " | ".join(changes)


def _input_snapshot_items(cfg: Any) -> tuple[tuple[str, str], ...]:
    """Return display-ready status inputs in a stable order."""
    total_assets = (
        _as_number(getattr(cfg, "balances_brokerage", 0))
        + _as_number(getattr(cfg, "balances_roth", 0))
        + _as_number(getattr(cfg, "balances_ira", 0))
    )
    return (
        ("Person 1 Final Age", _format_number(getattr(cfg, "final_age_person1", 0))),
        ("Person 2 Final Age", _format_number(getattr(cfg, "final_age_person2", 0))),
        ("Target Spend", format_currency(getattr(cfg, "target_spend", 0))),
        ("Year 1 MAGI Floor", format_currency(getattr(cfg, "year1_magi_floor", 0))),
        ("Year 1 MAGI Target", format_currency(getattr(cfg, "year1_magi_target", 0))),
        (
            "Year 1 MAGI Ceiling",
            format_currency(getattr(cfg, "year1_magi_ceiling", 0)),
        ),
        (
            "Year 1 Extra MAGI Income",
            format_currency(getattr(cfg, "year1_extra_magi_income", 0)),
        ),
        (
            "Year 1 MAGI Loss Offset",
            format_currency(getattr(cfg, "year1_magi_loss_offset", 0)),
        ),
        (
            "Year 1 Planned Roth Conversion",
            format_currency(getattr(cfg, "year1_planned_roth_conversion", 0)),
        ),
        ("ACA MAGI Floor", format_currency(getattr(cfg, "aca_magi_floor", 0))),
        ("ACA MAGI Target", format_currency(getattr(cfg, "aca_magi_target", 0))),
        ("ACA MAGI Ceiling", format_currency(getattr(cfg, "aca_magi_ceiling", 0))),
        (
            "ACA Extra MAGI Income",
            format_currency(getattr(cfg, "aca_extra_magi_income", 0)),
        ),
        (
            "ACA MAGI Loss Offset",
            format_currency(getattr(cfg, "aca_magi_loss_offset", 0)),
        ),
        (
            "ACA Planned Roth Conversion",
            format_currency(getattr(cfg, "aca_planned_roth_conversion", 0)),
        ),
        (
            "Medicare MAGI Floor",
            format_currency(getattr(cfg, "medicare_magi_floor", 0)),
        ),
        (
            "Medicare MAGI Target",
            format_currency(getattr(cfg, "medicare_magi_target", 0)),
        ),
        (
            "Medicare MAGI Ceiling",
            format_currency(getattr(cfg, "medicare_magi_ceiling", 0)),
        ),
        (
            "Medicare Extra MAGI Income",
            format_currency(getattr(cfg, "medicare_extra_magi_income", 0)),
        ),
        (
            "Medicare MAGI Loss Offset",
            format_currency(getattr(cfg, "medicare_magi_loss_offset", 0)),
        ),
        (
            "Medicare Planned Roth Conversion",
            format_currency(getattr(cfg, "medicare_planned_roth_conversion", 0)),
        ),
        ("Medicare Age", _format_number(getattr(cfg, "aca_end_age", 0))),
        (
            "GoGo Years",
            f"{_format_number(getattr(cfg, 'gogo_years', 0))}/"
            f"{_format_percent(getattr(cfg, 'gogo_percent', 0), scale=False)}",
        ),
        (
            "SlowGo Years",
            f"{_format_number(getattr(cfg, 'slow_years', 0))}/"
            f"{_format_percent(getattr(cfg, 'slow_percent', 0), scale=False)}",
        ),
        ("Total Assets", format_currency(total_assets)),
    )


def _format_percent(value: Any, scale: bool = True) -> str:
    try:
        value = float(value)
        if scale:
            value *= 100
        if value == int(value):
            return f"{int(value)}%"
        return f"{value:.2f}%"
    except (TypeError, ValueError):
        return "0%"


def _format_number(value: Any) -> str:
    try:
        value = float(value)
        if value == int(value):
            return str(int(value))
        return f"{value:g}"
    except (TypeError, ValueError):
        return "0"


class ResultsDisplay(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_rows: List[dict] = []
        self.summary_var = tk.StringVar(value=self.format_summary_text({}))
        self.summary_vars: dict[str, tk.StringVar] = {}
        self._history_lines: list[str] = []
        self._row_h = 24
        self._hdr_h = 28
        self.create_widgets()

    def create_widgets(self):
        self.sheet = Sheet(self, data=[], headers=[])
        self.sheet.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = tb.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        tb.Button(
            button_frame, text="Auto Size", bootstyle=INFO, command=self.autosize
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Export CSV",
            bootstyle=SECONDARY,
            command=self.export_csv,
        ).pack(side=tk.LEFT, padx=5)

        status_frame = tk.Frame(self, bg="#111827", padx=10, pady=8)
        status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        for label, key, bg, fg in SUMMARY_FIELDS:
            var = tk.StringVar(value=f"{label}: $0")
            self.summary_vars[key] = var
            tk.Label(
                status_frame,
                textvariable=var,
                anchor=tk.W,
                bg=bg,
                fg=fg,
                font=("Segoe UI", 13, "bold"),
                padx=12,
                pady=5,
            ).pack(side=tk.LEFT, padx=(0, 8))

        history_frame = tk.Frame(self, bg="#0b1120")
        history_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        history_scrollbar = tk.Scrollbar(history_frame, orient=tk.VERTICAL)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text = tk.Text(
            history_frame,
            height=7,
            wrap=tk.WORD,
            bg="#0b1120",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            relief=tk.FLAT,
            font=("Consolas", 10),
            padx=10,
            pady=8,
            yscrollcommand=history_scrollbar.set,
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.configure(command=self.history_text.yview)
        self.history_text.configure(state=tk.DISABLED)

        self.style_sheet()
        self.setup_bindings()

    def setup_bindings(self):
        self.sheet.enable_bindings(
            (
                "single_select",
                "row_select",
                "column_select",
                "column_width_resize",
                "double_click_column_resize",
                "drag_select",
                "copy",
                "arrowkeys",
                "rc_select",
                "rc_popup_menu",
                "column_drag_and_drop",
            )
        )

    def style_sheet(self):
        options = {
            "align": "center",
            "header_align": "center",
            "row_height": 24,
            "header_height": 28,
            "table_bg": "#2e2e2e",
            "table_fg": "#ffffff",
            "table_selected_cells_border_color": "#ffffff",
            "table_selected_cells_bg": "#4e4e4e",
            "table_selected_cells_fg": "#ffffff",
            "header_bg": "#3e3e3e",
            "header_fg": "#ffffff",
            "header_selected_cells_bg": "#5e5e5e",
            "header_selected_cells_fg": "#ffffff",
            "index_bg": "#3e3e3e",
            "index_fg": "#ffffff",
            "index_selected_cells_bg": "#5e5e5e",
            "index_selected_cells_fg": "#ffffff",
            "top_left_bg": "#3e3e3e",
            "top_left_fg": "#ffffff",
            "table_grid_fg": "#4e4e4e",
            "table_outline": "#4e4e4e",
        }

        try:
            self.sheet.set_options(**options)
        except Exception:
            for k, v in options.items():
                try:
                    setattr(self.sheet, k, v)
                except Exception:
                    pass

    def load_results(self, rows: List[dict]):
        headers, data = to_2d_for_table(rows)
        self.current_rows = rows

        # Apply column order from current config if present
        config = getattr(self.app, "cfg", None)
        column_order = None
        if config:
            column_order = getattr(config, "column_order", None)
            if column_order is None and isinstance(config, dict):
                column_order = config.get("column_order", None)
        if column_order:
            header_idx = {h: i for i, h in enumerate(headers)}
            new_indices = [header_idx[h] for h in column_order if h in header_idx]
            # Add any missing columns at the end in their original order
            missing_indices = [
                i for i, h in enumerate(headers) if h not in column_order
            ]
            ordered_indices = new_indices + missing_indices
            headers = [headers[i] for i in ordered_indices]
            data = [[row[i] for i in ordered_indices] for row in data]

        # First 5 columns are not currency, everything else is currency
        col_types = []
        for i, _ in enumerate(headers):
            if i < 5:
                col_types.append("default")
            else:
                col_types.append("currency")

        formatted_data = []
        for row in data:
            formatted_row = []
            for i, val in enumerate(row):
                if col_types[i] == "currency":
                    formatted_row.append(format_currency(val))
                else:
                    formatted_row.append(val)
            formatted_data.append(formatted_row)

        self.sheet.set_sheet_data(
            formatted_data,
            reset_col_positions=True,
            reset_row_positions=True,
            redraw=True,
        )
        self.sheet.headers(headers)
        self.apply_alternate_row_colors()
        self.autosize()
        self.update_summary(calculate_results_summary(rows))

    def format_summary_text(self, summary: dict[str, float]) -> str:
        summary = summary or {}
        return " | ".join(
            f"{label}: {format_currency(summary.get(key, 0))}"
            for label, key, _bg, _fg in SUMMARY_FIELDS
        )

    def update_summary(self, summary: dict[str, float]) -> None:
        summary = summary or {}
        text = self.format_summary_text(summary)
        self.summary_var.set(text)
        for label, key, _bg, _fg in SUMMARY_FIELDS:
            if key in self.summary_vars:
                self.summary_vars[key].set(
                    f"{label}: {format_currency(summary.get(key, 0))}"
                )

    def append_summary_history(self, cfg: Any, baseline_cfg: Any = None) -> None:
        entry = [
            format_input_changes(cfg, baseline_cfg),
            f"Status: {self.summary_var.get()}",
            "",
        ]
        self._history_lines.extend(entry)
        self._history_lines = self._history_lines[-60:]

        self.history_text.configure(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        self.history_text.insert(tk.END, "\n".join(self._history_lines).strip())
        self.history_text.configure(state=tk.DISABLED)
        self.history_text.see(tk.END)

    def apply_alternate_row_colors(self):
        try:
            bg = "#2e2e2e"
            alt = "#3e3e3e"
            fg = "#ffffff"
            self.sheet.dehighlight_all()
            total = self.sheet.total_rows()
            if total <= 0:
                return
            evens = tuple(range(0, total, 2))
            odds = tuple(range(1, total, 2))
            self.sheet.highlight_rows(evens, bg=bg, fg=fg, redraw=False)
            self.sheet.highlight_rows(odds, bg=alt, fg=fg, redraw=True)
        except Exception:
            pass

    def autosize(self):
        try:
            self.sheet.set_all_column_widths()
            root = self.winfo_toplevel()
            root.geometry(APP_GEOMETRY)
        except Exception as e:
            print(f"Error in autosize: {e}")
            root = self.winfo_toplevel()
            root.geometry(APP_GEOMETRY)

    def export_csv(self):
        if hasattr(self.app, "export_csv"):
            self.app.export_csv()

    def get_current_rows(self) -> List[dict]:
        return self.current_rows

    def get_current_column_order(self):
        return self.sheet.headers()
