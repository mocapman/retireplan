# input_panel.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any


class InputPanel(ttk.Frame):
    def __init__(self, parent, on_change_callback: Callable[[], None] = None):
        super().__init__(parent)
        self.on_change_callback = on_change_callback
        self.variables: Dict[str, tk.Variable] = {}
        self.create_widgets()

    def create_widgets(self):
        # Main container with scrollbar
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Create a canvas and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input fields
        self.create_input_section(
            scrollable_frame,
            "Spending",
            [
                ("gogo_annual", "GoGo Annual", "120000"),
                ("slow_annual", "Slow Annual", "100000"),
                ("nogo_annual", "NoGo Annual", "80000"),
                ("gogo_years", "GoGo Years", "10"),
                ("slow_years", "Slow Years", "6"),
                ("survivor_percent", "Survivor %", "70"),
            ],
        )

        self.create_input_section(
            scrollable_frame,
            "Accounts",
            [
                ("balances_brokerage", "Brokerage Balance", "495000"),
                ("balances_roth", "Roth Balance", "104000"),
                ("balances_ira", "IRA Balance", "1030000"),
            ],
        )

        self.create_input_section(
            scrollable_frame,
            "Growth Rates",
            [
                ("inflation", "Inflation", "0.035"),
                ("brokerage_growth", "Brokerage Growth", "0.04"),
                ("roth_growth", "Roth Growth", "0.07"),
                ("ira_growth", "IRA Growth", "0.07"),
            ],
        )

        self.create_input_section(
            scrollable_frame,
            "Strategy",
            [
                ("draw_order", "Draw Order", "Brokerage, Roth, IRA"),
                ("magi_target_base", "MAGI Target", "85000"),
                ("standard_deduction_base", "Standard Deduction", "31500"),
            ],
        )

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="Reset to Defaults", command=self.reset_defaults
        ).pack(side=tk.LEFT, padx=5)

    def create_input_section(self, parent, title, fields):
        section = ttk.LabelFrame(parent, text=title)
        section.pack(fill=tk.X, padx=5, pady=5)

        for i, (key, label, default) in enumerate(fields):
            ttk.Label(section, text=label).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2
            )

            if key == "draw_order":
                var = tk.StringVar(value=default)
                cb = ttk.Combobox(section, textvariable=var, state="readonly")
                cb["values"] = [
                    "IRA, Brokerage, Roth",
                    "Brokerage, Roth, IRA",
                    "Brokerage, IRA, Roth",
                    "Roth, Brokerage, IRA",
                ]
                cb.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
            else:
                var = tk.StringVar(value=default)
                entry = ttk.Entry(section, textvariable=var)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

            self.variables[key] = var

        section.columnconfigure(1, weight=1)

    def apply_changes(self):
        if self.on_change_callback:
            self.on_change_callback()

    def reset_defaults(self):
        defaults = {
            "gogo_annual": "120000",
            "slow_annual": "100000",
            "nogo_annual": "80000",
            "gogo_years": "10",
            "slow_years": "6",
            "survivor_percent": "70",
            "balances_brokerage": "1000000",
            "balances_roth": "200000",
            "balances_ira": "800000",
            "inflation": "0.025",
            "brokerage_growth": "0.07",
            "roth_growth": "0.07",
            "ira_growth": "0.07",
            "draw_order": "Brokerage, Roth, IRA",
            "magi_target_base": "85000",
            "standard_deduction_base": "31500",
        }

        for key, value in defaults.items():
            if key in self.variables:
                self.variables[key].set(value)

        self.apply_changes()

    def get_values(self) -> Dict[str, Any]:
        values = {}
        for key, var in self.variables.items():
            value = var.get()
            # Convert numeric values
            if key in [
                "gogo_annual",
                "slow_annual",
                "nogo_annual",
                "balances_brokerage",
                "balances_roth",
                "balances_ira",
                "magi_target_base",
                "standard_deduction_base",
            ]:
                values[key] = float(value) if "." in value else int(value)
            elif key in ["inflation", "brokerage_growth", "roth_growth", "ira_growth"]:
                values[key] = float(value)
            elif key in ["gogo_years", "slow_years"]:
                values[key] = int(value)
            elif key == "survivor_percent":
                values[key] = float(value)
            else:
                values[key] = value
        return values
