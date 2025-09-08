from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tksheet import Sheet
from typing import List, Dict, Any

from retireplan.projections import to_2d_for_table
from retireplan.schema import keys as schema_keys

# Define which columns are money columns by key
MONEY_COLUMNS = {
    "Total_Spend",
    "Taxes_Due",
    "Base_Spend",
    "IRA_Draw",
    "Brokerage_Draw",
    "Roth_Draw",
    "Roth_Conversion",
    "IRA_Balance",
    "Brokerage_Balance",
    "Roth_Balance",
    "Total_Assets",
    "Shortfall",
    "Social_Security",
    "RMD",
    # Add more keys as needed
}


def format_currency(val) -> str:
    try:
        num = float(val)
        return f"${num:,.0f}"
    except (ValueError, TypeError):
        return str(val)


class ResultsDisplay(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_rows: List[dict] = []
        self._row_h = 24
        self._hdr_h = 28
        self.create_widgets()

    def create_widgets(self):
        # Sheet for results
        self.sheet = Sheet(self, data=[], headers=[])
        self.sheet.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button panel at the bottom
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

        # Configure sheet styling and bindings
        self.style_sheet()
        self.setup_bindings()

    def setup_bindings(self):
        """Configure sheet interactions"""
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
            )
        )

    def style_sheet(self):
        """Apply dark theme styling to the sheet"""
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
            # Fallback: set options individually
            for k, v in options.items():
                try:
                    setattr(self.sheet, k, v)
                except Exception:
                    pass

    def load_results(self, rows: List[dict]):
        """Load and display results data with currency formatting"""
        headers, data = to_2d_for_table(rows)
        col_keys = schema_keys()

        # Format currency columns
        formatted_data = []
        for row in data:
            formatted_row = []
            for idx, val in enumerate(row):
                key = col_keys[idx] if idx < len(col_keys) else None
                if key in MONEY_COLUMNS and val not in (None, ""):
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
        self.current_rows = rows
        self.apply_alternate_row_colors()
        self.autosize()  # Ensures window resizes after new data

    def apply_alternate_row_colors(self):
        """Apply alternate row coloring for readability"""
        try:
            for idx in range(self.sheet.get_total_rows()):
                color = "#23272b" if idx % 2 else "#2e2e2e"
                self.sheet.row_colors(rows=[idx], clr=color)
        except Exception:
            pass

    def autosize(self):
        """Auto-size columns and adjust window size to fit the sheet, including currency formatting."""
        try:
            self.sheet.set_all_column_widths()
            total_width = sum(
                self.sheet.column_width(col)
                for col in range(self.sheet.total_columns())
            )
            # Add some padding for scrollbars and window borders
            window_width = min(
                max(total_width + 680, 800), 4000
            )  # min/max limits to avoid crazy sizes
            window_height = (
                self.sheet.get_total_rows() * self._row_h + 220
            )  # tweak as needed

            root = self.winfo_toplevel()
            root.geometry(f"{window_width}x{window_height}")
        except Exception as e:
            print(f"Error in autosize: {e}")

    def export_csv(self):
        """Export the currently shown data as CSV (calls parent app method if available)"""
        if hasattr(self.master, "export_csv"):
            self.master.export_csv()
        elif hasattr(self.master.master, "export_csv"):
            self.master.master.export_csv()

    def get_current_rows(self) -> List[dict]:
        """Return the current raw data rows (for export)"""
        return self.current_rows
