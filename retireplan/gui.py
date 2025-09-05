from __future__ import annotations

import PySimpleGUI as sg

from retireplan import theme, inputs, projections
from retireplan.engine import run_plan


def main():
    theme.apply()
    theme.apply_matplotlib()
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")

    headings = projections.COLUMNS
    table = sg.Table(values=[], headings=headings, key="-TABLE-", **theme.table_kwargs())
    layout = [
        [
            sg.Text("RetirePlan"),
            sg.Button("Recalculate"),
            sg.Button("Export CSV"),
            sg.Button("Exit"),
        ],
        [table],
    ]
    win = sg.Window("RetirePlan", layout, finalize=True, resizable=True)

    def recalc():
        rows = run_plan(cfg)
        df = projections.to_dataframe(rows)
        win["-TABLE-"].update(values=df.values.tolist())

    recalc()
    while True:
        ev, _ = win.read()
        if ev in (sg.WIN_CLOSED, "Exit"):
            break
        if ev == "Recalculate":
            recalc()
        if ev == "Export CSV":
            rows = run_plan(cfg)
            df = projections.to_dataframe(rows)
            df.to_csv("projections.csv", index=False)
            sg.popup_quick_message(
                "Saved projections.csv",
                auto_close=True,
                background_color=theme.COLORS["bg"],
                text_color=theme.COLORS["text"],
            )
    win.close()


if __name__ == "__main__":
    main()
