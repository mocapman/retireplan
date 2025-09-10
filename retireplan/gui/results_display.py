from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tksheet import Sheet
from typing import List

from tools.projections import to_2d_for_table


def format_currency(val):
    try:
        val = float(val)
        return "${:,.0f}".format(val)
    except Exception:
        return val


class ResultsDisplay(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_rows: List[dict] = []
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
            root.geometry("2525x950")
        except Exception as e:
            print(f"Error in autosize: {e}")
            root = self.winfo_toplevel()
            root.geometry("2525x950")

    def export_csv(self):
        if hasattr(self.app, "export_csv"):
            self.app.export_csv()

    def get_current_rows(self) -> List[dict]:
        return self.current_rows

    def get_current_column_order(self):
        return self.sheet.headers()
