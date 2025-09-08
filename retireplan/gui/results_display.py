from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tksheet import Sheet
from typing import List, Dict, Any

from retireplan.projections import to_2d_for_table


def format_currency(val):
    """Format as $#,### (no decimals)."""
    try:
        val = float(val)
        return "${:,.0f}".format(val)
    except Exception:
        return val


def format_percent(val):
    """Format as #.##% or #%. No decimals if not needed."""
    try:
        val = float(val)
        if val == int(val):
            return f"{int(val)}%"
        else:
            return f"{val:.2f}%"
    except Exception:
        return val


# List of headers/column names that should display as currency
CURRENCY_HEADERS = {
    "Brokerage",
    "Roth",
    "IRA",
    "Total",
    "Spending",
    "Taxable",
    "MAGI",
    "Tax Owed",
    "Balance",
    "Net Worth",
    "SS",
    "Tax",
    "RMD",
    "Withdrawal",
    "Medical",
    "Income",
    "Standard Deduction",
}
# Add more terms as your CSV/data files require.

PERCENT_HEADERS = {
    "Inflation",
    "Growth",
    "Rate",
    "Return",
    "Survivor %",
}  # Add/adjust as needed


class ResultsDisplay(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
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
            for k, v in options.items():
                try:
                    setattr(self.sheet, k, v)
                except Exception:
                    pass

    def load_results(self, rows: List[dict]):
        """Load and display results data"""
        headers, data = to_2d_for_table(rows)
        self.current_rows = rows

        # Determine columns to format as currency or percent
        col_types = []
        for hdr in headers:
            if any(hdr.lower().startswith(h.lower()) for h in CURRENCY_HEADERS) or any(
                h.lower() in hdr.lower() for h in CURRENCY_HEADERS
            ):
                col_types.append("currency")
            elif any(hdr.lower().endswith(h.lower()) for h in PERCENT_HEADERS) or any(
                h.lower() in hdr.lower() for h in PERCENT_HEADERS
            ):
                col_types.append("percent")
            else:
                col_types.append("default")

        # Format the data
        formatted_data = []
        for row in data:
            formatted_row = []
            for i, val in enumerate(row):
                if col_types[i] == "currency":
                    formatted_row.append(format_currency(val))
                elif col_types[i] == "percent":
                    formatted_row.append(format_percent(val))
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
        """Apply alternating row colors for better readability"""
        try:
            # Dark theme colors
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
        """Force window to fixed size, skipping all calculations."""
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
        """Get the currently displayed rows"""
        return self.current_rows
