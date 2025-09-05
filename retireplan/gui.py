from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import List

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tksheet import Sheet

from retireplan import inputs, schema
from retireplan.engine import run_plan
from retireplan.theme import apply_theme, sheet_options, DEFAULT_THEME
from retireplan.projections import to_2d_for_table

APP_TITLE = "RetirePlan"


class App:
    def __init__(self) -> None:
        self.root = tb.Window(title=APP_TITLE)
        self.theme_name = DEFAULT_THEME
        self.style = apply_theme(self.root, self.theme_name)

        self.cur_rows: List[dict] = []
        self.start_dt = date.today()
        self._row_h = 24
        self._hdr_h = 28

        self._build_ui()
        self._populate_table_initial()

    def _build_ui(self) -> None:
        top = tb.Frame(self.root, padding=(8, 8, 8, 4))
        top.pack(side=TOP, fill=X)

        tb.Label(top, text="Theme").pack(side=LEFT)
        self.theme_sel = tb.Combobox(
            top, values=["Light", "Dark"], state="readonly", width=8
        )
        self.theme_sel.set(self.theme_name)
        self.theme_sel.pack(side=LEFT, padx=(6, 16))
        self.theme_sel.bind("<<ComboboxSelected>>", self._on_change_theme)

        tb.Label(top, text="Start Date").pack(side=LEFT)
        self.start_date = DateEntry(
            master=top,
            startdate=self.start_dt,
            firstweekday=6,
            bootstyle=PRIMARY,
            width=12,
        )
        self.start_date.pack(side=LEFT, padx=(6, 16))

        self.btn_run = tb.Button(
            top, text="Run Plan", bootstyle=SUCCESS, command=self._run_plan
        )
        self.btn_run.pack(side=LEFT, padx=4)

        self.btn_export = tb.Button(
            top, text="Export CSV", bootstyle=SECONDARY, command=self._export_csv
        )
        self.btn_export.pack(side=LEFT, padx=4)

        self.btn_autosize = tb.Button(
            top, text="Auto Size", bootstyle=INFO, command=self._autosize
        )
        self.btn_autosize.pack(side=LEFT, padx=4)

        mid = tb.Frame(self.root, padding=(8, 4, 8, 8))
        mid.pack(side=TOP, fill=BOTH, expand=YES)

        self.sheet = Sheet(mid, data=[], headers=[], height=500, width=1100)
        self.sheet.pack(fill=BOTH, expand=YES)

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

        # Apply autoresize at first paint
        self.root.after(75, self._autosize)

    def _style_sheet(self) -> None:
        opts = sheet_options(self.theme_name)
        self._row_h = int(opts.get("row_height", 24))
        self._hdr_h = int(opts.get("header_height", 28))
        try:
            self.sheet.set_options(**opts)
        except Exception:
            for k, v in opts.items():
                try:
                    setattr(self.sheet, k, v)
                except Exception:
                    pass

    # ---------- actions ----------

    def _run_plan(self) -> None:
        cfg = inputs.load_yaml("examples/sample_inputs.yaml")
        try:
            sd = self.start_date.entry.get()
            y, m, d = self._parse_date_string(sd)
            self.start_dt = date(y, m, d)
        except Exception:
            self.start_dt = date.today()

        if hasattr(cfg, "start_year"):
            cfg.start_year = self.start_dt.year

        rows = run_plan(cfg)
        self._load_rows(rows)

    def _export_csv(self) -> None:
        if not self.cur_rows:
            return
        out = Path("projections.csv")
        keys = schema.keys()
        headers = schema.labels()
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(headers)
            for r in self.cur_rows:
                w.writerow([r.get(k, None) for k in keys])

    def _populate_table_initial(self) -> None:
        cfg = inputs.load_yaml("examples/sample_inputs.yaml")
        if hasattr(cfg, "start_year"):
            cfg.start_year = self.start_dt.year
        rows = run_plan(cfg)
        self._load_rows(rows)

    def _load_rows(self, rows: List[dict]) -> None:
        headers, data = to_2d_for_table(rows)
        self.sheet.set_sheet_data(
            data, reset_col_positions=True, reset_row_positions=True, redraw=True
        )
        self.sheet.headers(headers)
        self.cur_rows = rows
        self._apply_zebra()
        self._autosize()

    def _apply_zebra(self) -> None:
        try:
            opts = sheet_options(self.theme_name)
            bg = opts["table_bg"]
            alt = opts["table_alt_bg"]
            fg = opts["table_fg"]

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
        try:
            self.sheet.set_all_column_widths()
        except Exception:
            for c in range(self.sheet.total_columns()):
                self.sheet.column_width(column=c, width=110)

        try:
            cols = self.sheet.total_columns()
            rows = self.sheet.total_rows()
            col_sum = 0
            for c in range(cols):
                try:
                    col_sum += int(self.sheet.column_width(c))
                except Exception:
                    col_sum += 110

            vertical_scrollbar = 18
            horizontal_padding = 24
            header_pad = 12

            w = col_sum + vertical_scrollbar + horizontal_padding
            h = (self._hdr_h + header_pad) + rows * self._row_h + 90

            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w = min(w, max(700, int(sw * 0.9)))
            h = min(h, max(480, int(sh * 0.85)))
            self.root.geometry(f"{w}x{h}")
        except Exception:
            pass

    def _on_change_theme(self, _evt=None) -> None:
        sel = self.theme_sel.get()
        if sel not in ("Light", "Dark"):
            return
        self.theme_name = sel
        apply_theme(self.root, self.theme_name)
        self._style_sheet()
        self._apply_zebra()
        self._autosize()

    @staticmethod
    def _parse_date_string(s: str) -> tuple[int, int, int]:
        s = s.strip()
        if "-" in s:
            y, m, d = s.split("-", 2)
            return int(y), int(m), int(d)
        if "/" in s:
            m, d, y = s.split("/", 2)
            return int(y), int(m), int(d)
        t = date.today()
        return t.year, t.month, t.day


def main() -> None:
    App().root.mainloop()


if __name__ == "__main__":
    main()
