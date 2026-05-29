from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tksheet import Sheet
from typing import Any, List

from retireplan import schema
from retireplan.projections import to_2d_for_table


APP_GEOMETRY = "2525x1150"
MONEY_COLUMN_WIDTH = 104
NON_MONEY_TABLE_KEYS = {"Year", "Person1_Age", "Person2_Age", "Filing", "Lifestyle"}

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

    return "Inputs:\n" + "\n".join(
        f"{section}: "
        + " | ".join(f"{label}: {value}" for label, value in items)
        for section, items in _input_snapshot_sections(cfg)
    )


def format_input_changes(cfg: Any, baseline_cfg: Any) -> str:
    """Return only scenario inputs that differ from the startup config."""
    if cfg is None or baseline_cfg is None:
        return format_input_snapshot(cfg)

    baseline = {
        (section, label): value
        for section, items in _input_snapshot_sections(baseline_cfg)
        for label, value in items
    }
    section_changes = []
    for section, items in _input_snapshot_sections(cfg):
        changes = [
            f"{label}: {baseline.get((section, label), 'n/a')} -> {value}"
            for label, value in items
            if baseline.get((section, label)) != value
        ]
        if changes:
            section_changes.append(f"{section}: " + " | ".join(changes))

    if not section_changes:
        return "Inputs: No changes from default config"
    return "Inputs changed:\n" + "\n".join(section_changes)


def _input_snapshot_sections(
    cfg: Any,
) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    """Return display-ready status inputs grouped by GUI section."""
    return (
        (
            "Personal",
            (
                (
                    "Person 1 Birth Year",
                    _format_number(getattr(cfg, "birth_year_person1", 0)),
                ),
                (
                    "Person 2 Birth Year",
                    _format_number(getattr(cfg, "birth_year_person2", 0)),
                ),
                (
                    "Person 1 Final Age",
                    _format_number(getattr(cfg, "final_age_person1", 0)),
                ),
                (
                    "Person 2 Final Age",
                    _format_number(getattr(cfg, "final_age_person2", 0)),
                ),
                ("Filing Status", str(getattr(cfg, "filing_status", ""))),
                (
                    "SS Age 1",
                    _format_number(getattr(cfg, "ss_person1_start_age", 0)),
                ),
                (
                    "SS Age 2",
                    _format_number(getattr(cfg, "ss_person2_start_age", 0)),
                ),
                (
                    "SS Annual 1",
                    format_currency(getattr(cfg, "ss_person1_annual_at_start", 0)),
                ),
                (
                    "SS Annual 2",
                    format_currency(getattr(cfg, "ss_person2_annual_at_start", 0)),
                ),
            ),
        ),
        (
            "Accounts",
            (
                ("Brkg Cash", format_currency(getattr(cfg, "brokerage_cash", 0))),
                (
                    "Brkg Basis",
                    format_currency(getattr(cfg, "brokerage_cost_basis", 0)),
                ),
                (
                    "Brkg Gain",
                    format_currency(getattr(cfg, "brokerage_unrealized_gain", 0)),
                ),
                ("IRA", format_currency(getattr(cfg, "balances_ira", 0))),
                ("Roth", format_currency(getattr(cfg, "balances_roth", 0))),
            ),
        ),
        (
            "Spending",
            (
                ("Draw Order", str(getattr(cfg, "draw_order", ""))),
                ("Start Year", _format_number(getattr(cfg, "start_year", 0))),
                ("Year 1 Spend", format_currency(getattr(cfg, "year1_spend", 0))),
                (
                    "Year 1 Brkg Draw",
                    format_currency(getattr(cfg, "year1_brokerage_draw", 0)),
                ),
                (
                    "Year 1 IRA Draw",
                    format_currency(getattr(cfg, "year1_ira_draw", 0)),
                ),
                (
                    "Year 1 Roth Draw",
                    format_currency(getattr(cfg, "year1_roth_draw", 0)),
                ),
                ("Target Spend", format_currency(getattr(cfg, "target_spend", 0))),
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
                (
                    "NoGo %",
                    _format_percent(getattr(cfg, "nogo_percent", 0), scale=False),
                ),
                (
                    "Survivor %",
                    _format_percent(getattr(cfg, "survivor_percent", 0), scale=False),
                ),
            ),
        ),
        (
            "Rates",
            (
                ("Inflation", _format_percent(getattr(cfg, "inflation", 0))),
                (
                    "Brkg Growth",
                    _format_percent(getattr(cfg, "brokerage_growth", 0)),
                ),
                ("Roth Growth", _format_percent(getattr(cfg, "roth_growth", 0))),
                ("IRA Growth", _format_percent(getattr(cfg, "ira_growth", 0))),
            ),
        ),
        (
            "Tax",
            (
                (
                    "State Deduction",
                    format_currency(getattr(cfg, "estimated_state_deduction", 0)),
                ),
                (
                    "State Rate",
                    _format_percent(getattr(cfg, "estimated_state_tax_rate", 0)),
                ),
                (
                    "Standard Deduction",
                    format_currency(getattr(cfg, "standard_deduction_base", 0)),
                ),
                (
                    "RMD Start Age",
                    _format_number(getattr(cfg, "rmd_start_age", 0)),
                ),
                ("Medicare Age", _format_number(getattr(cfg, "aca_end_age", 0))),
            ),
        ),
        ("Roth Planning", _roth_planning_snapshot_items(cfg)),
    )


def _input_snapshot_items(cfg: Any) -> tuple[tuple[str, str], ...]:
    """Return display-ready status inputs in a stable flat order."""
    return tuple(
        item for _section, items in _input_snapshot_sections(cfg) for item in items
    )


def _roth_planning_snapshot_items(cfg: Any) -> tuple[tuple[str, str], ...]:
    """Return Roth Planning inputs in a stable order."""
    return (
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
    )


def _format_percent(value: Any, scale: bool = True) -> str:
    try:
        value = float(value)
        if scale:
            value *= 100
        rounded = round(value)
        if abs(value - rounded) < 0.000001:
            return f"{rounded}%"
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
        self.current_column_keys: List[str] = []
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
        keys = schema.visible_keys()
        self.current_rows = rows

        # Apply column order from current config if present
        config = getattr(self.app, "cfg", None)
        column_order = None
        if config:
            column_order = getattr(config, "column_order", None)
            if column_order is None and isinstance(config, dict):
                column_order = config.get("column_order", None)
        if column_order:
            ordered_indices = self._resolve_column_order(column_order, headers, keys)
            headers = [headers[i] for i in ordered_indices]
            data = [[row[i] for i in ordered_indices] for row in data]
            keys = [keys[i] for i in ordered_indices]

        self.current_column_keys = keys

        formatted_data = []
        for row in data:
            formatted_row = []
            for i, val in enumerate(row):
                if self._is_money_column(keys[i]):
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

    def _resolve_column_order(self, column_order, headers, keys):
        header_to_index = {h: i for i, h in enumerate(headers)}
        key_to_index = {k: i for i, k in enumerate(keys)}
        ordered_indices = []
        seen_indices = set()

        for item in column_order:
            idx = key_to_index.get(item)
            if idx is None:
                idx = header_to_index.get(item)
            if idx is not None and idx not in seen_indices:
                ordered_indices.append(idx)
                seen_indices.add(idx)

        ordered_indices.extend(i for i in range(len(keys)) if i not in seen_indices)
        return ordered_indices

    def _is_money_column(self, key: str) -> bool:
        return key not in NON_MONEY_TABLE_KEYS

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
            f"Result: {self.summary_var.get()}",
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
            for idx, key in enumerate(self.current_column_keys):
                if self._is_money_column(key):
                    self.sheet.column_width(idx, width=MONEY_COLUMN_WIDTH, redraw=False)
            self.sheet.redraw()
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
        header_to_key = {schema.gui_label(k): k for k in schema.visible_keys()}
        header_to_key.update({k: k for k in schema.visible_keys()})
        ordered_keys = []
        seen = set()
        for header in self.sheet.headers():
            key = header_to_key.get(header)
            if key is not None and key not in seen:
                ordered_keys.append(key)
                seen.add(key)
        return ordered_keys
