from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from retireplan import theme, inputs, projections
from retireplan.engine import run_plan


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("RetirePlan")
        self.root.geometry("1200x700")
        theme.apply_styles(self.root)
        theme.apply_matplotlib()
        self.cfg = inputs.load_yaml("examples/sample_inputs.yaml")
        self._build_ui()
        self._recalc()

    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        ttk.Label(top, text="RetirePlan").pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(top, text="Recalculate", command=self._recalc).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(top, text="Export CSV", command=self._export_csv).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(top, text="Exit", command=self.root.destroy).pack(
            side=tk.LEFT, padx=4
        )

        # Table
        columns = projections.COLUMNS
        table_frame = ttk.Frame(self.root)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Alternate row color via tags
        self.tree.tag_configure("oddrow", background=theme.COLORS["alt_row"])

    def _recalc(self):
        rows = run_plan(self.cfg)
        self._populate(rows)

    def _populate(self, rows):
        # Clear
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert
        for idx, row in enumerate(rows):
            vals = [row[col] for col in projections.COLUMNS]
            tag = ("oddrow",) if idx % 2 else ()
            self.tree.insert("", "end", values=vals, tags=tag)

    def _export_csv(self):

        rows = run_plan(self.cfg)
        df = projections.to_dataframe(rows)
        df.to_csv("projections.csv", index=False)
        messagebox.showinfo("RetirePlan", "Saved projections.csv")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
