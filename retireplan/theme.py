# retireplan/theme.py
from __future__ import annotations

import PySimpleGUI as sg
from matplotlib import pyplot as plt

COLORS = {
    "bg": "#1E1E1E",
    "text": "#D4D4D4",
    "input_bg": "#252526",
    "input_text": "#D4D4D4",
    "scroll": "#3C3C3C",
    "button_bg": "#3C3C3C",
    "button_text": "#FFFFFF",
    "header_bg": "#3C3C3C",
    "header_text": "#FFFFFF",
    "alt_row": "#252526",
    "accent_blue": "#569CD6",
    "accent_teal": "#4EC9B0",
    "accent_lightblue": "#9CDCFE",
    "accent_orange": "#CE9178",
}

PALETTE = [
    COLORS["accent_blue"],
    COLORS["accent_teal"],
    COLORS["accent_lightblue"],
    COLORS["accent_orange"],
]


def apply():
    theme = {
        "BACKGROUND": COLORS["bg"],
        "TEXT": COLORS["text"],
        "INPUT": COLORS["input_bg"],
        "TEXT_INPUT": COLORS["input_text"],
        "SCROLL": COLORS["scroll"],
        "BUTTON": (COLORS["button_text"], COLORS["button_bg"]),
        "PROGRESS": (COLORS["bg"], COLORS["accent_blue"]),
        "BORDER": 1,
        "SLIDER_DEPTH": 0,
        "PROGRESS_DEPTH": 0,
        "INPUT_ELEMENTS_BACKGROUND": COLORS["input_bg"],
        "ELEMENT_BACKGROUND": COLORS["bg"],
        "COLOR_LIST": PALETTE,
        "HEADING": (COLORS["header_text"], COLORS["header_bg"]),
    }
    # Use custom theme if API exists; else fall back to a built-in dark theme
    if hasattr(sg, "theme_add_new"):
        sg.theme_add_new("RetirePlanDark", theme)
        sg.theme("RetirePlanDark")
    else:
        sg.theme("DarkGrey13")

    sg.set_options(
        font=("Segoe UI", 11),
        input_elements_background_color=COLORS["input_bg"],
        input_text_color=COLORS["input_text"],
        text_color=COLORS["text"],
        background_color=COLORS["bg"],
        button_color=(COLORS["button_text"], COLORS["button_bg"]),
        element_padding=(6, 6),
        slider_border_width=0,
        border_width=1,
    )


def table_kwargs():
    return dict(
        background_color=COLORS["bg"],
        text_color=COLORS["text"],
        header_background_color=COLORS["header_bg"],
        header_text_color=COLORS["header_text"],
        alternating_row_color=COLORS["alt_row"],
        num_rows=18,
        auto_size_columns=True,
        justification="left",
        enable_events=True,
    )


def apply_matplotlib():
    plt.rcParams.update(
        {
            "figure.facecolor": COLORS["bg"],
            "axes.facecolor": COLORS["bg"],
            "axes.edgecolor": COLORS["text"],
            "axes.labelcolor": COLORS["text"],
            "xtick.color": COLORS["text"],
            "ytick.color": COLORS["text"],
            "text.color": COLORS["text"],
            "grid.color": COLORS["scroll"],
            "savefig.facecolor": COLORS["bg"],
            "savefig.edgecolor": COLORS["bg"],
        }
    )
