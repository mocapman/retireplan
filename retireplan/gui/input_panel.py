from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Callable, Optional

INPUT_FONT_FAMILY = "Arial"
INPUT_FONT_SIZE = 12
INPUT_FONT = (INPUT_FONT_FAMILY, INPUT_FONT_SIZE)


def format_currency(val):
    """Format as $#,### (no decimals)."""
    try:
        val = float(str(val).replace(",", "").replace("$", ""))
        return "${:,.0f}".format(val)
    except Exception:
        return val


def strip_currency(val):
    """Remove $ and commas for parsing."""
    return str(val).replace("$", "").replace(",", "").strip()


def format_percent(val):
    """Format as #.##% or #%. No decimals if not needed."""
    try:
        val = float(str(val).replace("%", ""))
        # Show up to 2 decimals if needed, but trim .00
        if val == int(val):
            return f"{int(val)}%"
        else:
            return f"{val:.2f}%"
    except Exception:
        return val


def strip_percent(val):
    """Remove % for parsing."""
    return str(val).replace("%", "").strip()


def percent_to_float(val):
    """Convert percent string (e.g. '4', '4%', '3.5%') to float (0.04, 0.035)."""
    try:
        return float(strip_percent(val)) / 100.0
    except Exception:
        return 0.0


def float_to_percent(val):
    """Convert float (0.04, 0.035) to percent string (4, 3.5)."""
    try:
        val = float(val)
        return val * 100
    except Exception:
        return val


class InputPanel(tb.Frame):
    def __init__(self, parent, app, on_change_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.app = app
        self.on_change_callback = on_change_callback
        self.variables = {}
        self.create_widgets()

    def create_widgets(self):
        button_frame = tb.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        tb.Button(
            button_frame, text="Load Config", command=self.load_config, bootstyle=INFO
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Save Config",
            command=self.save_config,
            bootstyle=PRIMARY,
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Apply Changes",
            command=self.apply_changes,
            bootstyle=SECONDARY,
        ).pack(side=tk.LEFT, padx=5)

        notebook = tb.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        personal_frame = tb.Frame(notebook)
        self.create_personal_section(personal_frame)
        notebook.add(personal_frame, text="Personal")

        accounts_frame = tb.Frame(notebook)
        self.create_accounts_section(accounts_frame)
        notebook.add(accounts_frame, text="Accounts")

        spending_frame = tb.Frame(notebook)
        self.create_spending_section(spending_frame)
        notebook.add(spending_frame, text="Spending")

        ss_frame = tb.Frame(notebook)
        self.create_ss_section(ss_frame)
        notebook.add(ss_frame, text="Social Security")

        rates_frame = tb.Frame(notebook)
        self.create_rates_section(rates_frame)
        notebook.add(rates_frame, text="Rates")

        tax_frame = tb.Frame(notebook)
        self.create_tax_section(tax_frame)
        notebook.add(tax_frame, text="Tax & Health")

        strategy_frame = tb.Frame(notebook)
        self.create_strategy_section(strategy_frame)
        notebook.add(strategy_frame, text="Strategy")

    # --- Enhanced input field creators ---

    def create_currency_field(self, parent, label, key, default, row, col=0):
        """Entry with $ formatting and no decimals."""
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        var = tk.StringVar(value=format_currency(default) if default else "")
        entry = tb.Entry(parent, textvariable=var, font=INPUT_FONT)
        entry.grid(row=row, column=col + 1, sticky=(tk.W, tk.E), padx=5, pady=2)
        parent.columnconfigure(col + 1, weight=1)

        def on_focus_in(event):
            v = var.get()
            var.set(strip_currency(v))

        def on_focus_out(event):
            v = var.get()
            # Only format if there is a value and input is a valid number
            try:
                n = int(float(strip_currency(v)))
                var.set(format_currency(n) if v.strip() else "")
            except Exception:
                var.set("")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        self.variables[key] = var
        return var

    def create_percent_field(self, parent, label, key, default, row, col=0):
        """Entry with % formatting, supports decimals."""
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        # Accept float or string for default, always display as percent
        if default not in ("", None):
            try:
                shown = format_percent(float(default))
            except Exception:
                shown = str(default)
        else:
            shown = ""
        var = tk.StringVar(value=shown)
        entry = tb.Entry(parent, textvariable=var, font=INPUT_FONT)
        entry.grid(row=row, column=col + 1, sticky=(tk.W, tk.E), padx=5, pady=2)
        parent.columnconfigure(col + 1, weight=1)

        def on_focus_in(event):
            v = var.get()
            var.set(strip_percent(v))

        def on_focus_out(event):
            v = var.get()
            try:
                f = float(strip_percent(v))
                var.set(format_percent(f) if v.strip() else "")
            except Exception:
                var.set("")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        self.variables[key] = var
        return var

    def create_input_field(self, parent, label, key, default, row, col=0):
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        var = tk.StringVar(value=str(default) if default is not None else "")
        entry = tb.Entry(parent, textvariable=var, font=INPUT_FONT)
        entry.grid(row=row, column=col + 1, sticky=(tk.W, tk.E), padx=5, pady=2)
        parent.columnconfigure(col + 1, weight=1)
        self.variables[key] = var
        return var

    def create_combobox(self, parent, label, key, values, default, row, col=0):
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        var = tk.StringVar(value=default)
        cb = tb.Combobox(parent, textvariable=var, values=values, state="readonly")
        cb.grid(row=row, column=col + 1, sticky=(tk.W, tk.E), padx=5, pady=2)
        parent.columnconfigure(col + 1, weight=1)
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
        self.create_currency_field(
            parent, "Brokerage Balance", "balances_brokerage", "", 0
        )
        self.create_currency_field(parent, "Roth Balance", "balances_roth", "", 1)
        self.create_currency_field(parent, "IRA Balance", "balances_ira", "", 2)

    def create_spending_section(self, parent):
        parent.columnconfigure(1, weight=1)
        self.create_currency_field(parent, "Target Spend (today's $)", "target_spend", "", 0)
        self.create_percent_field(parent, "GoGo Phase %", "gogo_percent", 100, 1)
        self.create_percent_field(parent, "SlowGo Phase %", "slow_percent", 80, 2) 
        self.create_percent_field(parent, "NoGo Phase %", "nogo_percent", 70, 3)
        self.create_input_field(parent, "GoGo Years", "gogo_years", "", 4)
        self.create_input_field(parent, "SlowGo Years", "slow_years", "", 5)
        self.create_percent_field(parent, "Survivor Spending %", "survivor_percent", "", 6)

    def create_ss_section(self, parent):
        parent.columnconfigure(1, weight=1)
        self.create_input_field(
            parent, "Person 1 Start Age", "ss_person1_start_age", "", 0
        )
        self.create_currency_field(
            parent, "Person 1 Annual", "ss_person1_annual_at_start", "", 1
        )
        self.create_input_field(
            parent, "Person 2 Start Age", "ss_person2_start_age", "", 2
        )
        self.create_currency_field(
            parent, "Person 2 Annual", "ss_person2_annual_at_start", "", 3
        )

    def create_rates_section(self, parent):
        parent.columnconfigure(1, weight=1)
        self.create_percent_field(parent, "Inflation", "inflation", "", 0)
        self.create_percent_field(parent, "Brokerage Growth", "brokerage_growth", "", 1)
        self.create_percent_field(parent, "Roth Growth", "roth_growth", "", 2)
        self.create_percent_field(parent, "IRA Growth", "ira_growth", "", 3)

    def create_tax_section(self, parent):
        parent.columnconfigure(1, weight=1)
        self.create_currency_field(parent, "MAGI Target", "magi_target_base", "", 0)
        self.create_currency_field(
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

    def load_config(self):
        if hasattr(self.app, "load_config"):
            self.app.load_config()

    def save_config(self):
        if hasattr(self.app, "save_config"):
            self.app.save_config()

    def get_config_dict(self):
        # Always parse to numbers for backend logic
        def safe_int(val):
            try:
                return int(float(val))
            except Exception:
                return 0

        def safe_float(val):
            try:
                return float(val)
            except Exception:
                return 0.0

        config = {
            "start_year": safe_int(self.variables["start_year"].get()),
            "birth_year_person1": safe_int(self.variables["birth_year_person1"].get()),
            "birth_year_person2": safe_int(self.variables["birth_year_person2"].get()),
            "final_age_person1": safe_int(self.variables["final_age_person1"].get()),
            "final_age_person2": safe_int(self.variables["final_age_person2"].get()),
            "filing_status": self.variables["filing_status"].get(),
            "balances": {
                "brokerage": safe_float(
                    strip_currency(self.variables["balances_brokerage"].get())
                ),
                "roth": safe_float(
                    strip_currency(self.variables["balances_roth"].get())
                ),
                "ira": safe_float(strip_currency(self.variables["balances_ira"].get())),
            },
            "spending": {
                "target_spend": safe_float(
                    strip_currency(self.variables["target_spend"].get())
                ),
                "gogo_percent": safe_float(
                    strip_percent(self.variables["gogo_percent"].get())
                ),
                "slow_percent": safe_float(
                    strip_percent(self.variables["slow_percent"].get())
                ),
                "nogo_percent": safe_float(
                    strip_percent(self.variables["nogo_percent"].get())
                ),
                "gogo_years": safe_int(self.variables["gogo_years"].get()),
                "slow_years": safe_int(self.variables["slow_years"].get()),
                "survivor_percent": safe_float(
                    strip_percent(self.variables["survivor_percent"].get())
                ),
            },
            "social_security": {
                "person1_start_age": safe_int(
                    self.variables["ss_person1_start_age"].get()
                ),
                "person1_annual_at_start": safe_float(
                    strip_currency(self.variables["ss_person1_annual_at_start"].get())
                ),
                "person2_start_age": safe_int(
                    self.variables["ss_person2_start_age"].get()
                ),
                "person2_annual_at_start": safe_float(
                    strip_currency(self.variables["ss_person2_annual_at_start"].get())
                ),
            },
            "rates": {
                "inflation": percent_to_float(self.variables["inflation"].get()),
                "brokerage_growth": percent_to_float(
                    self.variables["brokerage_growth"].get()
                ),
                "roth_growth": percent_to_float(self.variables["roth_growth"].get()),
                "ira_growth": percent_to_float(self.variables["ira_growth"].get()),
            },
            "tax_health": {
                "magi_target_base": safe_float(
                    strip_currency(self.variables["magi_target_base"].get())
                ),
                "standard_deduction_base": safe_float(
                    strip_currency(self.variables["standard_deduction_base"].get())
                ),
                "rmd_start_age": safe_int(self.variables["rmd_start_age"].get()),
                "aca_end_age": safe_int(self.variables["aca_end_age"].get()),
            },
            "draw_order": self.variables["draw_order"].get(),
        }
        return config

    def set_config(self, config):
        # Always display formatted for currency/percent fields
        mapping = {
            "start_year": config.get("start_year"),
            "birth_year_person1": config.get("birth_year_person1"),
            "birth_year_person2": config.get("birth_year_person2"),
            "final_age_person1": config.get("final_age_person1"),
            "final_age_person2": config.get("final_age_person2"),
            "filing_status": config.get("filing_status"),
            "balances_brokerage": format_currency(
                config.get("balances", {}).get("brokerage", "")
            ),
            "balances_roth": format_currency(
                config.get("balances", {}).get("roth", "")
            ),
            "balances_ira": format_currency(config.get("balances", {}).get("ira", "")),
            "target_spend": format_currency(
                config.get("spending", {}).get("target_spend", "")
            ),
            "gogo_percent": format_percent(
                config.get("spending", {}).get("gogo_percent", 100)
            ),
            "slow_percent": format_percent(
                config.get("spending", {}).get("slow_percent", 80)
            ),
            "nogo_percent": format_percent(
                config.get("spending", {}).get("nogo_percent", 70)
            ),
            "gogo_years": config.get("spending", {}).get("gogo_years"),
            "slow_years": config.get("spending", {}).get("slow_years"),
            "survivor_percent": format_percent(
                config.get("spending", {}).get("survivor_percent", "")
            ),
            "ss_person1_start_age": config.get("social_security", {}).get(
                "person1_start_age"
            ),
            "ss_person1_annual_at_start": format_currency(
                config.get("social_security", {}).get("person1_annual_at_start", "")
            ),
            "ss_person2_start_age": config.get("social_security", {}).get(
                "person2_start_age"
            ),
            "ss_person2_annual_at_start": format_currency(
                config.get("social_security", {}).get("person2_annual_at_start", "")
            ),
            "inflation": format_percent(
                float_to_percent(config.get("rates", {}).get("inflation", ""))
            ),
            "brokerage_growth": format_percent(
                float_to_percent(config.get("rates", {}).get("brokerage_growth", ""))
            ),
            "roth_growth": format_percent(
                float_to_percent(config.get("rates", {}).get("roth_growth", ""))
            ),
            "ira_growth": format_percent(
                float_to_percent(config.get("rates", {}).get("ira_growth", ""))
            ),
            "magi_target_base": format_currency(
                config.get("tax_health", {}).get("magi_target_base", "")
            ),
            "standard_deduction_base": format_currency(
                config.get("tax_health", {}).get("standard_deduction_base", "")
            ),
            "rmd_start_age": config.get("tax_health", {}).get("rmd_start_age"),
            "aca_end_age": config.get("tax_health", {}).get("aca_end_age"),
            "draw_order": config.get("draw_order"),
        }
        for key, value in mapping.items():
            if key in self.variables and value is not None:
                self.variables[key].set(str(value))
