import PySimpleGUI as sg

from retireplan import theme


def main():
    theme.apply()  # apply app-wide colors
    theme.apply_matplotlib()  # charts match the GUI

    layout = [
        [sg.Text("RetirePlan")],
        [sg.Button("Recalculate"), sg.Button("Exit")],
        [sg.Table(values=[], headings=["Year"], key="-TABLE-", **theme.table_kwargs())],
    ]
    window = sg.Window("RetirePlan", layout, finalize=True)
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break
    window.close()


if __name__ == "__main__":
    main()
