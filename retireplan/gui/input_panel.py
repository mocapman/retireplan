# gui/input_panel.py
from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Callable, Optional


class InputPanel(tb.Frame):
    def __init__(self, parent, on_change_callback: Optional[Callable] = None):
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
            bootstyle=PRIMARY,
        ).pack(side=tk.LEFT, padx=5)
        tb.Button(
            button_frame,
            text="Apply Changes",
            command=self.apply_changes,
            bootstyle=SECONDARY,
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

    def load_config(self):
        # This will be handled by the file operations module
        if hasattr(self.master, "load_config"):
            self.master.load_config()

    def save_config(self):
        # This will be handled by the file operations module
        if hasattr(self.master, "save_config"):
            self.master.save_config()

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
