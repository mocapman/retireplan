from __future__ import annotations

from matplotlib import pyplot as plt
from ttkbootstrap import Style

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


def apply_styles(root) -> Style:
    style = Style()  # uses system theme as base
    # Global
    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"])
    # Frames and labels
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    # Buttons
    style.configure(
        "TButton",
        background=COLORS["button_bg"],
        foreground=COLORS["button_text"],
        padding=6,
    )
    style.map(
        "TButton",
        background=[("active", COLORS["button_bg"])],
        foreground=[("active", COLORS["button_text"])],
    )
    # Treeview (table)
    style.configure(
        "Treeview",
        background=COLORS["bg"],
        fieldbackground=COLORS["bg"],
        foreground=COLORS["text"],
        rowheight=22,
        bordercolor=COLORS["bg"],
        lightcolor=COLORS["bg"],
        darkcolor=COLORS["bg"],
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["header_bg"],
        foreground=COLORS["header_text"],
    )
    return style


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
