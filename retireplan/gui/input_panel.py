from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Callable, Optional

INPUT_FONT_FAMILY = "Arial"
INPUT_FONT_SIZE = 12
INPUT_FONT = (INPUT_FONT_FAMILY, INPUT_FONT_SIZE)


def format_currency(val):
    try:
        val = float(str(val).replace(",", "").replace("$", ""))
        return "${:,.0f}".format(val)
    except Exception:
        return val


def strip_currency(val):
    return str(val).replace("$", "").replace(",", "").strip()


def format_percent(val):
    try:
        val = float(str(val).replace("%", ""))
        if val == int(val):
            return f"{int(val)}%"
        else:
            return f"{val:.2f}%"
    except Exception:
        return val


def strip_percent(val):
    return str(val).replace("%", "").strip()


def percent_to_float(val):
    try:
        return float(strip_percent(val)) / 100.0
    except Exception:
        return 0.0


def float_to_percent(val):
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

        body_frame = tb.Frame(self)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        nav_frame = tb.Frame(body_frame, width=160)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        content_frame = tb.Frame(body_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        sections = (
            ("Personal", self.create_personal_section),
            ("Accounts", self.create_accounts_section),
            ("Spending", self.create_spending_section),
            ("MAGI Planning", self.create_magi_planning_section),
            ("Social Security", self.create_ss_section),
            ("Rates", self.create_rates_section),
            ("Tax & Health", self.create_tax_section),
            ("Strategy", self.create_strategy_section),
        )

        self.section_frames = {}
        self.nav_buttons = {}
        for row, (label, builder) in enumerate(sections):
            frame = tb.Frame(content_frame)
            frame.grid(row=0, column=0, sticky="nsew")
            builder(frame)
            self.section_frames[label] = frame

            button = tb.Button(
                nav_frame,
                text=label,
                command=lambda name=label: self.show_section(name),
                bootstyle=SECONDARY,
            )
            button.grid(row=row, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
            self.nav_buttons[label] = button
        nav_frame.columnconfigure(0, weight=1)
        self.show_section("Personal")

    def show_section(self, name):
        self.section_frames[name].tkraise()

    def create_currency_field(self, parent, label, key, default, row, col=0):
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
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
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

    def create_display_field(self, parent, label, key, default, row, col=0):
        tb.Label(parent, text=label).grid(
            row=row, column=col, sticky=tk.W, padx=5, pady=2
        )
        var = tk.StringVar(value=str(default) if default is not None else "")
        entry = tb.Entry(parent, textvariable=var, font=INPUT_FONT, state="readonly")
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
        self.create_input_field(
            parent, "Person 1 Birth Year", "birth_year_person1", "", 0
        )
        self.create_input_field(
            parent, "Person 2 Birth Year", "birth_year_person2", "", 1
        )
        self.create_input_field(
            parent, "Person 1 Final Age", "final_age_person1", "", 2
        )
        self.create_input_field(
            parent, "Person 2 Final Age", "final_age_person2", "", 3
        )
        self.create_combobox(
            parent, "Filing Status", "filing_status", ["MFJ", "Single"], "MFJ", 4
        )

    def create_accounts_section(self, parent):
        parent.columnconfigure(1, weight=1)
        tb.Label(
            parent,
            text="Taxable Brokerage",
            font=(INPUT_FONT_FAMILY, INPUT_FONT_SIZE, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 4))
        self.create_currency_field(parent, "Cash", "brokerage_cash", "", 1)
        self.create_currency_field(
            parent, "Holdings Cost Basis", "brokerage_cost_basis", "", 2
        )
        self.create_currency_field(
            parent, "Unrealized Gains", "brokerage_unrealized_gain", "", 3
        )
        self.create_display_field(
            parent, "Total Balance", "balances_brokerage", "", 4
        )
        for key in (
            "brokerage_cash",
            "brokerage_cost_basis",
            "brokerage_unrealized_gain",
        ):
            self.variables[key].trace_add(
                "write", lambda *_: self.update_brokerage_balance_display()
            )

        tb.Label(
            parent,
            text="Retirement Accounts",
            font=(INPUT_FONT_FAMILY, INPUT_FONT_SIZE, "bold"),
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(16, 4))
        self.create_currency_field(parent, "Roth Balance", "balances_roth", "", 6)
        self.create_currency_field(parent, "IRA Balance", "balances_ira", "", 7)
        self.update_brokerage_balance_display()

    def brokerage_detail_total(self):
        total = 0.0
        for key in (
            "brokerage_cash",
            "brokerage_cost_basis",
            "brokerage_unrealized_gain",
        ):
            try:
                total += float(strip_currency(self.variables[key].get()))
            except Exception:
                pass
        return total

    def update_brokerage_balance_display(self):
        if "balances_brokerage" in self.variables:
            self.variables["balances_brokerage"].set(
                format_currency(self.brokerage_detail_total())
            )

    def magi_planning_amount(self, key):
        try:
            return float(strip_currency(self.variables[key].get()))
        except Exception:
            return 0.0

    def update_magi_planning_display(self):
        if not all(
            key in self.variables
            for key in (
                "magi_income_annual",
                "magi_gains_annual",
                "magi_losses_annual",
                "magi_conversions_annual",
            )
        ):
            return

        annuals = {
            "magi_income_annual": (
                self.magi_planning_amount("magi_income_ytd")
                + self.magi_planning_amount("magi_income_projected")
            ),
            "magi_gains_annual": (
                self.magi_planning_amount("magi_gains_ytd")
                + self.magi_planning_amount("magi_gains_projected")
            ),
            "magi_losses_annual": (
                self.magi_planning_amount("magi_losses_ytd")
                + self.magi_planning_amount("magi_losses_projected")
            ),
            "magi_conversions_annual": (
                self.magi_planning_amount("magi_conversions_ytd")
                + self.magi_planning_amount("magi_conversions_projected")
            ),
        }
        for key, value in annuals.items():
            self.variables[key].set(format_currency(value))

        projected_magi = (
            annuals["magi_income_annual"]
            + annuals["magi_gains_annual"]
            + annuals["magi_conversions_annual"]
            - annuals["magi_losses_annual"]
        )
        magi_remaining = (
            self.magi_planning_amount("magi_target_base") - projected_magi
        )
        if hasattr(self, "magi_summary_projected"):
            self.magi_summary_projected.set(format_currency(projected_magi))
            self.magi_summary_remaining.set(format_currency(magi_remaining))

    def create_spending_section(self, parent):
        parent.columnconfigure(1, weight=1)
        self.create_input_field(parent, "Start Year", "start_year", "", 0)
        self.create_currency_field(
            parent,
            "Year 1 Remaining Spend",
            "year1_spend",
            "",
            1,
        )
        self.variables["year1_cash_events"] = tk.StringVar(value="0")
        self.create_currency_field(
            parent, "Year 1 Brokerage Draw", "year1_brokerage_draw", "", 2
        )
        self.create_currency_field(parent, "Year 1 IRA Draw", "year1_ira_draw", "", 3)
        self.create_currency_field(parent, "Year 1 Roth Draw", "year1_roth_draw", "", 4)
        self.create_currency_field(
            parent, "Target Spend (today's $)", "target_spend", "", 5
        )
        self.create_percent_field(parent, "GoGo Phase %", "gogo_percent", 100, 6)
        self.create_percent_field(parent, "SlowGo Phase %", "slow_percent", 80, 7)
        self.create_percent_field(parent, "NoGo Phase %", "nogo_percent", 70, 8)
        self.create_input_field(parent, "GoGo Years", "gogo_years", "", 9)
        self.create_input_field(parent, "SlowGo Years", "slow_years", "", 10)
        self.create_percent_field(
            parent, "Survivor Spending %", "survivor_percent", "", 11
        )

    def create_magi_planning_section(self, parent):
        parent.columnconfigure(0, weight=1)

        for key in (
            "year1_magi_income",
            "year1_magi_losses",
            "year1_roth_conversion",
            "year1_income_to_date",
            "year1_projected_income",
            "year1_capital_gains_to_date",
            "year1_projected_capital_gains",
            "year1_capital_losses_to_date",
            "year1_projected_capital_losses",
        ):
            self.variables[key] = tk.StringVar(value="")

        grid_frame = tb.Frame(parent)
        grid_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=5, pady=2)
        for col in range(1, 5):
            grid_frame.columnconfigure(col, weight=1, minsize=115)

        summary_frame = tb.Frame(parent)
        summary_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E), padx=5, pady=(16, 2))
        summary_frame.columnconfigure(1, weight=1, minsize=180)

        guardrails_frame = tb.Frame(parent)
        guardrails_frame.grid(
            row=2, column=0, sticky=(tk.N, tk.W, tk.E), padx=5, pady=(16, 2)
        )
        guardrails_frame.columnconfigure(1, weight=1, minsize=180)

        tb.Label(grid_frame, text="").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        for col, label in enumerate(("YTD", "Projected", "Annual", "Years"), start=1):
            tb.Label(grid_frame, text=label).grid(
                row=0, column=col, sticky=tk.W, padx=5, pady=2
            )

        grid = (
            (
                "Income",
                "magi_income_ytd",
                "magi_income_projected",
                "magi_income_annual",
                "magi_income_years",
            ),
            (
                "Gains",
                "magi_gains_ytd",
                "magi_gains_projected",
                "magi_gains_annual",
                "magi_gains_years",
            ),
            (
                "Losses",
                "magi_losses_ytd",
                "magi_losses_projected",
                "magi_losses_annual",
                "magi_losses_years",
            ),
            (
                "Conversions",
                "magi_conversions_ytd",
                "magi_conversions_projected",
                "magi_conversions_annual",
                "magi_conversions_years",
            ),
        )

        for row, cells in enumerate(grid, start=1):
            label, *keys = cells
            tb.Label(grid_frame, text=label).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=2
            )
            for col, key in enumerate(keys, start=1):
                var = tk.StringVar(value="")
                entry_state = "readonly" if key.endswith("_annual") else "normal"
                entry = tb.Entry(
                    grid_frame,
                    textvariable=var,
                    font=INPUT_FONT,
                    width=14,
                    state=entry_state,
                )
                entry.grid(row=row, column=col, sticky=(tk.W, tk.E), padx=5, pady=2)
                self.variables[key] = var

        for key in (
            "magi_income_ytd",
            "magi_income_projected",
            "magi_gains_ytd",
            "magi_gains_projected",
            "magi_losses_ytd",
            "magi_losses_projected",
            "magi_conversions_ytd",
            "magi_conversions_projected",
        ):
            self.variables[key].trace_add(
                "write", lambda *_: self.update_magi_planning_display()
            )

        summary_row = 0
        tb.Label(
            summary_frame,
            text="MAGI Summary",
            font=(INPUT_FONT_FAMILY, INPUT_FONT_SIZE, "bold"),
        ).grid(row=summary_row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 4))

        self.create_currency_field(
            summary_frame, "MAGI Target", "magi_target_base", "", summary_row + 1
        )
        self.variables["magi_target_base"].trace_add(
            "write", lambda *_: self.update_magi_planning_display()
        )
        self.magi_summary_projected = tk.StringVar(value="$0")
        self.magi_summary_remaining = tk.StringVar(value="$0")
        self.magi_summary_status = tk.StringVar(value="")
        summary_rows = (
            ("Projected MAGI", self.magi_summary_projected),
            ("MAGI Remaining", self.magi_summary_remaining),
            ("MAGI Status", self.magi_summary_status),
        )
        for offset, (label, var) in enumerate(summary_rows, start=2):
            tb.Label(summary_frame, text=label).grid(
                row=summary_row + offset, column=0, sticky=tk.W, padx=5, pady=2
            )
            tb.Label(summary_frame, textvariable=var).grid(
                row=summary_row + offset,
                column=1,
                sticky=tk.W,
                padx=5,
                pady=2,
            )

        guardrails_row = 0
        tb.Label(
            guardrails_frame,
            text="ACA Guardrails",
            font=(INPUT_FONT_FAMILY, INPUT_FONT_SIZE, "bold"),
        ).grid(
            row=guardrails_row,
            column=0,
            columnspan=2,
            sticky=tk.W,
            padx=5,
            pady=(16, 4),
        )
        self.create_currency_field(
            guardrails_frame,
            "ACA Full Premium Monthly",
            "aca_full_premium_monthly",
            "",
            guardrails_row + 1,
        )
        self.create_currency_field(
            guardrails_frame,
            "ACA Max Subsidy Monthly",
            "aca_expected_subsidy_monthly",
            "",
            guardrails_row + 2,
        )
        self.create_currency_field(
            guardrails_frame, "ACA MAGI Floor", "aca_magi_floor", "", guardrails_row + 3
        )
        self.create_currency_field(
            guardrails_frame,
            "ACA MAGI Ceiling",
            "aca_magi_ceiling",
            "",
            guardrails_row + 4,
        )

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
        tb.Label(
            parent,
            text="Tax Assumptions",
            font=(INPUT_FONT_FAMILY, INPUT_FONT_SIZE, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 4))
        self.create_currency_field(
            parent, "Estimated State Deduction", "estimated_state_deduction", "", 1
        )
        self.create_percent_field(
            parent, "Estimated State Tax Rate", "estimated_state_tax_rate", "", 2
        )
        self.create_currency_field(
            parent, "Standard Deduction", "standard_deduction_base", "", 3
        )
        self.create_input_field(parent, "RMD Start Age", "rmd_start_age", "", 4)
        self.create_input_field(parent, "ACA End Age", "aca_end_age", "", 5)

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
            "birth_year_person1": safe_int(self.variables["birth_year_person1"].get()),
            "birth_year_person2": safe_int(self.variables["birth_year_person2"].get()),
            "final_age_person1": safe_int(self.variables["final_age_person1"].get()),
            "final_age_person2": safe_int(self.variables["final_age_person2"].get()),
            "filing_status": self.variables["filing_status"].get(),
            "balances": {
                "brokerage_cash": safe_float(
                    strip_currency(self.variables["brokerage_cash"].get())
                ),
                "brokerage_cost_basis": safe_float(
                    strip_currency(self.variables["brokerage_cost_basis"].get())
                ),
                "brokerage_unrealized_gain": safe_float(
                    strip_currency(self.variables["brokerage_unrealized_gain"].get())
                ),
                "roth": safe_float(
                    strip_currency(self.variables["balances_roth"].get())
                ),
                "ira": safe_float(strip_currency(self.variables["balances_ira"].get())),
            },
            "spending": {
                "start_year": safe_int(self.variables["start_year"].get()),
                "year1_spend": safe_float(
                    strip_currency(self.variables["year1_spend"].get())
                ),
                "year1_cash_events": 0.0,
                "year1_brokerage_draw": safe_float(
                    strip_currency(self.variables["year1_brokerage_draw"].get())
                ),
                "year1_ira_draw": safe_float(
                    strip_currency(self.variables["year1_ira_draw"].get())
                ),
                "year1_roth_draw": safe_float(
                    strip_currency(self.variables["year1_roth_draw"].get())
                ),
                "year1_magi_income": safe_float(
                    strip_currency(self.variables["year1_magi_income"].get())
                ),
                "year1_magi_losses": safe_float(
                    strip_currency(self.variables["year1_magi_losses"].get())
                ),
                "year1_roth_conversion": safe_float(
                    strip_currency(self.variables["year1_roth_conversion"].get())
                ),
                "year1_income_to_date": safe_float(
                    strip_currency(self.variables["year1_income_to_date"].get())
                ),
                "year1_projected_income": safe_float(
                    strip_currency(self.variables["year1_projected_income"].get())
                ),
                "year1_capital_gains_to_date": safe_float(
                    strip_currency(
                        self.variables["year1_capital_gains_to_date"].get()
                    )
                ),
                "year1_projected_capital_gains": safe_float(
                    strip_currency(
                        self.variables["year1_projected_capital_gains"].get()
                    )
                ),
                "year1_capital_losses_to_date": safe_float(
                    strip_currency(
                        self.variables["year1_capital_losses_to_date"].get()
                    )
                ),
                "year1_projected_capital_losses": safe_float(
                    strip_currency(
                        self.variables["year1_projected_capital_losses"].get()
                    )
                ),
                "magi_income_ytd": safe_float(
                    strip_currency(self.variables["magi_income_ytd"].get())
                ),
                "magi_income_projected": safe_float(
                    strip_currency(self.variables["magi_income_projected"].get())
                ),
                "magi_income_years": safe_float(
                    self.variables["magi_income_years"].get()
                ),
                "magi_gains_ytd": safe_float(
                    strip_currency(self.variables["magi_gains_ytd"].get())
                ),
                "magi_gains_projected": safe_float(
                    strip_currency(self.variables["magi_gains_projected"].get())
                ),
                "magi_gains_years": safe_float(
                    self.variables["magi_gains_years"].get()
                ),
                "magi_losses_ytd": safe_float(
                    strip_currency(self.variables["magi_losses_ytd"].get())
                ),
                "magi_losses_projected": safe_float(
                    strip_currency(self.variables["magi_losses_projected"].get())
                ),
                "magi_losses_years": safe_float(
                    self.variables["magi_losses_years"].get()
                ),
                "magi_conversions_ytd": safe_float(
                    strip_currency(self.variables["magi_conversions_ytd"].get())
                ),
                "magi_conversions_projected": safe_float(
                    strip_currency(self.variables["magi_conversions_projected"].get())
                ),
                "magi_conversions_years": safe_float(
                    self.variables["magi_conversions_years"].get()
                ),
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
                    strip_currency(
                        self.variables["ss_person1_annual_at_start"].get()
                    )
                ),
                "person2_start_age": safe_int(
                    self.variables["ss_person2_start_age"].get()
                ),
                "person2_annual_at_start": safe_float(
                    strip_currency(
                        self.variables["ss_person2_annual_at_start"].get()
                    )
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
                "estimated_state_deduction": safe_float(
                    strip_currency(self.variables["estimated_state_deduction"].get())
                ),
                "estimated_state_tax_rate": percent_to_float(
                    self.variables["estimated_state_tax_rate"].get()
                ),
                "rmd_start_age": safe_int(self.variables["rmd_start_age"].get()),
                "aca_end_age": safe_int(self.variables["aca_end_age"].get()),
                "aca_expected_subsidy_monthly": safe_float(
                    strip_currency(self.variables["aca_expected_subsidy_monthly"].get())
                ),
                "aca_full_premium_monthly": safe_float(
                    strip_currency(self.variables["aca_full_premium_monthly"].get())
                ),
                "aca_magi_floor": safe_float(
                    strip_currency(self.variables["aca_magi_floor"].get())
                ),
                "aca_magi_ceiling": safe_float(
                    strip_currency(self.variables["aca_magi_ceiling"].get())
                ),
            },
            "draw_order": self.variables["draw_order"].get(),
        }
        return config

    def set_config(self, config):
        s = config.get("spending", {})
        balances = config.get("balances", {})
        if (
            "brokerage_cash" not in balances
            and "brokerage_cost_basis" not in balances
            and "brokerage_unrealized_gain" not in balances
        ):
            brokerage_cash = balances.get("brokerage", "")
            brokerage_cost_basis = 0
            brokerage_unrealized_gain = 0
        else:
            brokerage_cash = balances.get("brokerage_cash", 0)
            brokerage_cost_basis = balances.get("brokerage_cost_basis", 0)
            brokerage_unrealized_gain = balances.get("brokerage_unrealized_gain", 0)
        mapping = {
            "start_year": s.get("start_year"),
            "birth_year_person1": config.get("birth_year_person1"),
            "birth_year_person2": config.get("birth_year_person2"),
            "final_age_person1": config.get("final_age_person1"),
            "final_age_person2": config.get("final_age_person2"),
            "filing_status": config.get("filing_status"),
            "brokerage_cash": format_currency(brokerage_cash),
            "brokerage_cost_basis": format_currency(brokerage_cost_basis),
            "brokerage_unrealized_gain": format_currency(
                brokerage_unrealized_gain
            ),
            "balances_roth": format_currency(
                config.get("balances", {}).get("roth", "")
            ),
            "balances_ira": format_currency(config.get("balances", {}).get("ira", "")),
            "year1_spend": format_currency(s.get("year1_spend", "")),
            "year1_cash_events": 0,
            "year1_brokerage_draw": format_currency(s.get("year1_brokerage_draw", "")),
            "year1_ira_draw": format_currency(s.get("year1_ira_draw", "")),
            "year1_roth_draw": format_currency(s.get("year1_roth_draw", "")),
            "year1_magi_income": format_currency(s.get("year1_magi_income", "")),
            "year1_magi_losses": format_currency(s.get("year1_magi_losses", "")),
            "year1_roth_conversion": format_currency(
                s.get("year1_roth_conversion", "")
            ),
            "year1_income_to_date": format_currency(s.get("year1_income_to_date", "")),
            "year1_projected_income": format_currency(
                s.get("year1_projected_income", "")
            ),
            "year1_capital_gains_to_date": format_currency(
                s.get("year1_capital_gains_to_date", "")
            ),
            "year1_projected_capital_gains": format_currency(
                s.get("year1_projected_capital_gains", "")
            ),
            "year1_capital_losses_to_date": format_currency(
                s.get("year1_capital_losses_to_date", "")
            ),
            "year1_projected_capital_losses": format_currency(
                s.get("year1_projected_capital_losses", "")
            ),
            "magi_income_ytd": format_currency(s.get("magi_income_ytd", "")),
            "magi_income_projected": format_currency(
                s.get("magi_income_projected", "")
            ),
            "magi_income_years": s.get("magi_income_years", ""),
            "magi_gains_ytd": format_currency(s.get("magi_gains_ytd", "")),
            "magi_gains_projected": format_currency(
                s.get("magi_gains_projected", "")
            ),
            "magi_gains_years": s.get("magi_gains_years", ""),
            "magi_losses_ytd": format_currency(s.get("magi_losses_ytd", "")),
            "magi_losses_projected": format_currency(
                s.get("magi_losses_projected", "")
            ),
            "magi_losses_years": s.get("magi_losses_years", ""),
            "magi_conversions_ytd": format_currency(
                s.get("magi_conversions_ytd", "")
            ),
            "magi_conversions_projected": format_currency(
                s.get("magi_conversions_projected", "")
            ),
            "magi_conversions_years": s.get("magi_conversions_years", ""),
            "target_spend": format_currency(s.get("target_spend", "")),
            "gogo_percent": format_percent(s.get("gogo_percent", 100)),
            "slow_percent": format_percent(s.get("slow_percent", 80)),
            "nogo_percent": format_percent(s.get("nogo_percent", 70)),
            "gogo_years": s.get("gogo_years"),
            "slow_years": s.get("slow_years"),
            "survivor_percent": format_percent(s.get("survivor_percent", "")),
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
                float_to_percent(
                    config.get("rates", {}).get("brokerage_growth", "")
                )
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
            "estimated_state_deduction": format_currency(
                config.get("tax_health", {}).get("estimated_state_deduction", "")
            ),
            "estimated_state_tax_rate": format_percent(
                float_to_percent(
                    config.get("tax_health", {}).get("estimated_state_tax_rate", "")
                )
            ),
            "rmd_start_age": config.get("tax_health", {}).get("rmd_start_age"),
            "aca_end_age": config.get("tax_health", {}).get("aca_end_age"),
            "aca_expected_subsidy_monthly": format_currency(
                config.get("tax_health", {}).get("aca_expected_subsidy_monthly", "")
            ),
            "aca_full_premium_monthly": format_currency(
                config.get("tax_health", {}).get("aca_full_premium_monthly", "")
            ),
            "aca_magi_floor": format_currency(
                config.get("tax_health", {}).get("aca_magi_floor", "")
            ),
            "aca_magi_ceiling": format_currency(
                config.get("tax_health", {}).get("aca_magi_ceiling", "")
            ),
            "draw_order": config.get("draw_order"),
        }
        for key, value in mapping.items():
            if key in self.variables and value is not None:
                self.variables[key].set(str(value))
        self.update_brokerage_balance_display()
        self.update_magi_planning_display()
