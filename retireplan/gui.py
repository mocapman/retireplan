# gui.py
from __future__ import annotations

import ctypes

try:
    # Enable DPI awareness for Windows
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass  # Fail silently if not on Windows or if function not available

import os
import csv
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tksheet import Sheet

from retireplan import inputs, schema
from retireplan.engine import run_plan
from retireplan.projections import to_2d_for_table
from retireplan.precision import round_row

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "default_config.yaml")

APP_TITLE = "My Retirement Plan"


class InputPanel(tb.Frame):
    def __init__(self, parent, on_change_callback=None):
        super().__init__(parent)
        self.on_change_callback = on_change_callback
        self.variables = {}
        self.create_widgets()

    def create_widgets(self):
        # Top button row
        button_frame = tb.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        tb.Button(
            button_frame, text="Load Config", command=self.load_config, bootstyle=INFO
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Save Config",
            command=self.save_config,
            bootstyle=SECONDARY,
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Apply Changes",
            command=self.apply_changes,
            bootstyle=PRIMARY,
        ).pack(side=tk.LEFT, padx=5)

        # Notebook
        notebook = tb.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Personal Info Tab
        personal_frame = tb.Frame(notebook)
        self.create_personal_section(personal_frame)
        notebook.add(personal_frame, text="Personal")

        # Accounts Tab
        accounts_frame = tb.Frame(notebook)
        self.create_accounts_section(accounts_frame)
        notebook.add(accounts_frame, text="Accounts")

        # Spending Tab
        spending_frame = tb.Frame(notebook)
        self.create_spending_section(spending_frame)
        notebook.add(spending_frame, text="Spending")

        # Social Security Tab
        ss_frame = tb.Frame(notebook)
        self.create_ss_section(ss_frame)
        notebook.add(ss_frame, text="Social Security")

        # Rates Tab
        rates_frame = tb.Frame(notebook)
        self.create_rates_section(rates_frame)
        notebook.add(rates_frame, text="Rates")

        # Tax & Health Tab
        tax_frame = tb.Frame(notebook)
        self.create_tax_section(tax_frame)
        notebook.add(tax_frame, text="Tax & Health")

        # Strategy Tab
        strategy_frame = tb.Frame(notebook)
        self.create_strategy_section(strategy_frame)
        notebook.add(strategy_frame, text="Strategy")

    def create_input_field(self, parent, label, key, default, row, col=0):
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        var = tk.StringVar(value=str(default))
        entry = tb.Entry(parent, textvariable=var)
        entry.grid(row=row, column=col + 1, sticky=(tk.W, tk.E), padx=5, pady=2)
        parent.columnconfigure(col + 1, weight=1)  # Make entry expand
        self.variables[key] = var
        return var

    def create_combobox(self, parent, label, key, values, default, row, col=0):
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        var = tk.StringVar(value=default)
        cb = tb.Combobox(parent, textvariable=var, values=values, state="readonly")
        cb.grid(row=row, column=col + 1, sticky=(tk.W, tk.E), padx=5, pady=2)
        parent.columnconfigure(col + 1, weight=1)  # Make combobox expand
        self.variables[key] = var
        return var

    def create_personal_section(self, parent):
        parent.columnconfigure(1, weight=1)

        self.create_input_field(parent, "Start Year", "start_year", "", 0)
        self.create_input_field(
            parent, "Person 1 Birth Year", "birth_year_person1", "", 1
        )
        self.create_input_field(
            parent, "Person 2 Birth Year", "birth_year_person2", "", 2
        )
        self.create_input_field(
            parent, "Person 1 Final Age", "final_age_person1", "", 3
        )
        self.create_input_field(
            parent, "Person 2 Final Age", "final_age_person2", "", 4
        )
        self.create_combobox(
            parent, "Filing Status", "filing_status", ["MFJ", "Single"], "MFJ", 5
        )

    def create_accounts_section(self, parent):
        parent.columnconfigure(1, weight=1)

        self.create_input_field(
            parent, "Brokerage Balance", "balances_brokerage", "", 0
        )
        self.create_input_field(parent, "Roth Balance", "balances_roth", "", 1)
        self.create_input_field(parent, "IRA Balance", "balances_ira", "", 2)

    def create_spending_section(self, parent):
        parent.columnconfigure(1, weight=1)

        self.create_input_field(parent, "GoGo Annual", "gogo_annual", "", 0)
        self.create_input_field(parent, "Slow Annual", "slow_annual", "", 1)
        self.create_input_field(parent, "NoGo Annual", "nogo_annual", "", 2)
        self.create_input_field(parent, "GoGo Years", "gogo_years", "", 3)
        self.create_input_field(parent, "Slow Years", "slow_years", "", 4)
        self.create_input_field(parent, "Survivor %", "survivor_percent", "", 5)

    def create_ss_section(self, parent):
        parent.columnconfigure(1, weight=1)

        self.create_input_field(
            parent, "Person 1 Start Age", "ss_person1_start_age", "", 0
        )
        self.create_input_field(
            parent, "Person 1 Annual", "ss_person1_annual_at_start", "", 1
        )
        self.create_input_field(
            parent, "Person 2 Start Age", "ss_person2_start_age", "", 2
        )
        self.create_input_field(
            parent, "Person 2 Annual", "ss_person2_annual_at_start", "", 3
        )

    def create_rates_section(self, parent):
        parent.columnconfigure(1, weight=1)

        self.create_input_field(parent, "Inflation", "inflation", "", 0)
        self.create_input_field(parent, "Brokerage Growth", "brokerage_growth", "", 1)
        self.create_input_field(parent, "Roth Growth", "roth_growth", "", 2)
        self.create_input_field(parent, "IRA Growth", "ira_growth", "", 3)

    def create_tax_section(self, parent):
        parent.columnconfigure(1, weight=1)

        self.create_input_field(parent, "MAGI Target", "magi_target_base", "", 0)
        self.create_input_field(
            parent, "Standard Deduction", "standard_deduction_base", "", 1
        )
        self.create_input_field(parent, "RMD Start Age", "rmd_start_age", "", 2)
        self.create_input_field(parent, "ACA End Age", "aca_end_age", "", 3)

    def create_strategy_section(self, parent):
        parent.columnconfigure(1, weight=1)

        draw_orders = [
            "IRA, Brokerage, Roth",
            "Brokerage, Roth, IRA",
            "Brokerage, IRA, Roth",
            "Roth, Brokerage, IRA",
        ]
        self.create_combobox(
            parent, "Draw Order", "draw_order", draw_orders, "Brokerage, Roth, IRA", 0
        )

    def apply_changes(self):
        if self.on_change_callback:
            self.on_change_callback()

    def save_config(self):
        file_path = tb.filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
        )
        if file_path:
            config = self.get_config_dict()
            with open(file_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

    def load_config(self):
        file_path = tb.filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)
            self.set_config(config)
            self.apply_changes()

    def get_config_dict(self):
        config = {
            "start_year": int(self.variables["start_year"].get()),
            "birth_year_person1": int(self.variables["birth_year_person1"].get()),
            "birth_year_person2": int(self.variables["birth_year_person2"].get()),
            "final_age_person1": int(self.variables["final_age_person1"].get()),
            "final_age_person2": int(self.variables["final_age_person2"].get()),
            "filing_status": self.variables["filing_status"].get(),
            "balances": {
                "brokerage": float(self.variables["balances_brokerage"].get()),
                "roth": float(self.variables["balances_roth"].get()),
                "ira": float(self.variables["balances_ira"].get()),
            },
            "spending": {
                "gogo_annual": float(self.variables["gogo_annual"].get()),
                "slow_annual": float(self.variables["slow_annual"].get()),
                "nogo_annual": float(self.variables["nogo_annual"].get()),
                "gogo_years": int(self.variables["gogo_years"].get()),
                "slow_years": int(self.variables["slow_years"].get()),
                "survivor_percent": float(self.variables["survivor_percent"].get()),
            },
            "social_security": {
                "person1_start_age": int(self.variables["ss_person1_start_age"].get()),
                "person1_annual_at_start": float(
                    self.variables["ss_person1_annual_at_start"].get()
                ),
                "person2_start_age": int(self.variables["ss_person2_start_age"].get()),
                "person2_annual_at_start": float(
                    self.variables["ss_person2_annual_at_start"].get()
                ),
            },
            "rates": {
                "inflation": float(self.variables["inflation"].get()),
                "brokerage_growth": float(self.variables["brokerage_growth"].get()),
                "roth_growth": float(self.variables["roth_growth"].get()),
                "ira_growth": float(self.variables["ira_growth"].get()),
            },
            "tax_health": {
                "magi_target_base": float(self.variables["magi_target_base"].get()),
                "standard_deduction_base": float(
                    self.variables["standard_deduction_base"].get()
                ),
                "rmd_start_age": int(self.variables["rmd_start_age"].get()),
                "aca_end_age": int(self.variables["aca_end_age"].get()),
            },
            "draw_order": self.variables["draw_order"].get(),
        }
        return config

    def set_config(self, config):
        mapping = {
            "start_year": config.get("start_year"),
            "birth_year_person1": config.get("birth_year_person1"),
            "birth_year_person2": config.get("birth_year_person2"),
            "final_age_person1": config.get("final_age_person1"),
            "final_age_person2": config.get("final_age_person2"),
            "filing_status": config.get("filing_status"),
            "balances_brokerage": config.get("balances", {}).get("brokerage"),
            "balances_roth": config.get("balances", {}).get("roth"),
            "balances_ira": config.get("balances", {}).get("ira"),
            "gogo_annual": config.get("spending", {}).get("gogo_annual"),
            "slow_annual": config.get("spending", {}).get("slow_annual"),
            "nogo_annual": config.get("spending", {}).get("nogo_annual"),
            "gogo_years": config.get("spending", {}).get("gogo_years"),
            "slow_years": config.get("spending", {}).get("slow_years"),
            "survivor_percent": config.get("spending", {}).get("survivor_percent"),
            "ss_person1_start_age": config.get("social_security", {}).get(
                "person1_start_age"
            ),
            "ss_person1_annual_at_start": config.get("social_security", {}).get(
                "person1_annual_at_start"
            ),
            "ss_person2_start_age": config.get("social_security", {}).get(
                "person2_start_age"
            ),
            "ss_person2_annual_at_start": config.get("social_security", {}).get(
                "person2_annual_at_start"
            ),
            "inflation": config.get("rates", {}).get("inflation"),
            "brokerage_growth": config.get("rates", {}).get("brokerage_growth"),
            "roth_growth": config.get("rates", {}).get("roth_growth"),
            "ira_growth": config.get("rates", {}).get("ira_growth"),
            "magi_target_base": config.get("tax_health", {}).get("magi_target_base"),
            "standard_deduction_base": config.get("tax_health", {}).get(
                "standard_deduction_base"
            ),
            "rmd_start_age": config.get("tax_health", {}).get("rmd_start_age"),
            "aca_end_age": config.get("tax_health", {}).get("aca_end_age"),
            "draw_order": config.get("draw_order"),
        }

        for key, value in mapping.items():
            if key in self.variables and value is not None:
                self.variables[key].set(str(value))


class App:
    def __init__(self) -> None:
        self.root = tb.Window(title=APP_TITLE, themename="darkly")
        self.cur_rows: List[dict] = []
        self.start_dt = datetime.now()
        self._row_h = 24
        self._hdr_h = 28

        # Load configuration from file
        self.cfg = self.load_config_from_file()

        self._build_ui()
        self._run_plan()

    def load_config_from_file(self):
        """Load configuration from file or raise error if not found"""
        try:
            return inputs.load_yaml(DEFAULT_CONFIG_PATH)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{DEFAULT_CONFIG_PATH}' not found. "
                f"Please create a default configuration file."
            )

    def _build_ui(self) -> None:
        # Set initial window size
        self.root.geometry("1800x800")

        # Create main paned window
        self.paned = tb.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Input panel on the left
        input_frame = tb.Frame(self.paned, width=600)
        self.paned.add(input_frame, weight=1)

        self.input_panel = InputPanel(input_frame, on_change_callback=self._run_plan)
        self.input_panel.pack(fill=tk.BOTH, expand=True)

        # Output area on the right
        output_frame = tb.Frame(self.paned)
        self.paned.add(output_frame, weight=2)

        # Sheet for results
        self.sheet = Sheet(output_frame, data=[], headers=[])
        self.sheet.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button panel at the very bottom
        button_frame = tb.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        tb.Button(
            button_frame, text="Auto Size", bootstyle=INFO, command=self._autosize
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Export CSV",
            bootstyle=SECONDARY,
            command=self._export_csv,
        ).pack(side=tk.LEFT, padx=5)

        # Set sheet style for dark theme
        self._style_sheet()
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

        # Set initial values from config
        self.input_panel.set_config(self.config_to_dict(self.cfg))

        # Set initial sash position
        self.root.after(100, lambda: self.paned.sashpos(0, 600))

    def config_to_dict(self, cfg):
        """Convert configuration object to dictionary for the input panel"""
        return {
            "start_year": cfg.start_year,
            "birth_year_person1": cfg.birth_year_person1,
            "birth_year_person2": cfg.birth_year_person2,
            "final_age_person1": cfg.final_age_person1,
            "final_age_person2": cfg.final_age_person2,
            "filing_status": cfg.filing_status,
            "balances": {
                "brokerage": cfg.balances_brokerage,
                "roth": cfg.balances_roth,
                "ira": cfg.balances_ira,
            },
            "spending": {
                "gogo_annual": cfg.gogo_annual,
                "slow_annual": cfg.slow_annual,
                "nogo_annual": cfg.nogo_annual,
                "gogo_years": cfg.gogo_years,
                "slow_years": cfg.slow_years,
                "survivor_percent": cfg.survivor_percent,
            },
            "social_security": {
                "person1_start_age": cfg.ss_person1_start_age,
                "person1_annual_at_start": cfg.ss_person1_annual_at_start,
                "person2_start_age": cfg.ss_person2_start_age,
                "person2_annual_at_start": cfg.ss_person2_annual_at_start,
            },
            "rates": {
                "inflation": cfg.inflation,
                "brokerage_growth": cfg.brokerage_growth,
                "roth_growth": cfg.roth_growth,
                "ira_growth": cfg.ira_growth,
            },
            "tax_health": {
                "magi_target_base": cfg.magi_target_base,
                "standard_deduction_base": cfg.standard_deduction_base,
                "rmd_start_age": cfg.rmd_start_age,
                "aca_end_age": cfg.aca_end_age,
            },
            "draw_order": cfg.draw_order,
        }

    def _update_config_from_dict(self, config_dict):
        """Update the configuration from a dictionary"""
        for key, value in config_dict.items():
            if key == "balances":
                self.cfg.balances_brokerage = value["brokerage"]
                self.cfg.balances_roth = value["roth"]
                self.cfg.balances_ira = value["ira"]
            elif key == "spending":
                for k, v in value.items():
                    if hasattr(self.cfg, k):
                        setattr(self.cfg, k, v)
            elif key == "social_security":
                for k, v in value.items():
                    if hasattr(self.cfg, k):
                        setattr(self.cfg, k, v)
            elif key == "rates":
                for k, v in value.items():
                    if hasattr(self.cfg, k):
                        setattr(self.cfg, k, v)
            elif key == "tax_health":
                for k, v in value.items():
                    if hasattr(self.cfg, k):
                        setattr(self.cfg, k, v)
            elif hasattr(self.cfg, key):
                setattr(self.cfg, key, value)

    def _run_plan(self) -> None:
        config_dict = self.input_panel.get_config_dict()
        self._update_config_from_dict(config_dict)

        rows = run_plan(self.cfg)
        self._load_rows(rows)

    def _export_csv(self) -> None:
        if not self.cur_rows:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        settings_str = (
            f"{self.cfg.draw_order.replace(', ', '_')}_{self.cfg.gogo_annual}"
        )

        out = Path(f"projections_{settings_str}_{timestamp}.csv")

        keys = schema.keys()
        headers = schema.labels()
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(headers)
            for r in self.cur_rows:
                rounded_row = round_row(r)
                w.writerow([rounded_row.get(k, None) for k in keys])

        config_out = Path(f"config_{settings_str}_{timestamp}.yaml")
        with config_out.open("w", encoding="utf-8") as f:
            yaml.dump(self.input_panel.get_config_dict(), f, default_flow_style=False)

    def _load_rows(self, rows: List[dict]) -> None:
        headers, data = to_2d_for_table(rows)
        self.sheet.set_sheet_data(
            data, reset_col_positions=True, reset_row_positions=True, redraw=True
        )
        self.sheet.headers(headers)
        self.cur_rows = rows
        self._apply_alternate_row_colors()

    def _apply_alternate_row_colors(self) -> None:
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

    def _autosize(self) -> None:
        """Resize the window to fit the content properly"""
        try:
            # Auto-size all columns first
            self.sheet.set_all_column_widths()

            # Calculate required width
            total_col_width = sum(
                (
                    int(self.sheet.column_width(c))
                    if self.sheet.column_width(c) is not None
                    else 110
                )
                for c in range(self.sheet.total_columns())
            )

            # Add padding for the table
            table_width = total_col_width + 50

            # Calculate required height
            rows = self.sheet.total_rows()
            table_height = self._hdr_h + (rows * self._row_h) + 100

            # Set the sash position to maintain the input panel width
            input_width = 600  # Fixed width for input panel
            total_width = input_width + table_width
            self.paned.sashpos(0, input_width)

            # Set the window size
            self.root.geometry(f"{total_width}x{table_height}")

        except Exception as e:
            print(f"Error in autosize: {e}")
            # Fallback to a reasonable size
            self.root.geometry("1800x800")

    def _style_sheet(self) -> None:
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


def main() -> None:
    try:
        App().root.mainloop()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
