from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import ttkbootstrap as tb

THEME_MAP = {"Light": "yeti", "Dark": "darkly"}
DEFAULT_THEME = "Dark"


@dataclass(frozen=True)
class Palette:
    bg: str
    fg: str
    alt_bg: str
    grid: str
    header_bg: str
    header_fg: str
    select_bg: str
    select_fg: str


PALETTES: Dict[str, Palette] = {
    "Light": Palette(
        bg="#ffffff",
        fg="#212529",
        alt_bg="#f3f4f6",  # clearer stripe
        grid="#d0d7de",
        header_bg="#e9ecef",
        header_fg="#212529",
        select_bg="#d0ebff",
        select_fg="#0b1021",
    ),
    "Dark": Palette(
        bg="#1f2124",
        fg="#e6e6e6",
        alt_bg="#292b2f",  # clearer stripe
        grid="#3b4046",
        header_bg="#2a2d31",
        header_fg="#e6e6e6",
        select_bg="#2f6fed",
        select_fg="#ffffff",
    ),
}


def apply_theme(root, theme: str = DEFAULT_THEME) -> tb.Style:
    name = THEME_MAP.get(theme, THEME_MAP[DEFAULT_THEME])
    style = tb.Style(theme=name)
    root.option_add("*tearOff", False)
    return style


def sheet_options(theme: str = DEFAULT_THEME) -> Dict[str, Any]:
    p = PALETTES.get(theme, PALETTES[DEFAULT_THEME])
    return {
        # geometry
        "row_height": 24,
        "header_height": 28,
        # visuals
        "show_row_index": False,
        "show_top_left": False,
        "show_zebra_stripes": False,  # we apply explicit stripes via highlight_rows
        "table_bg": p.bg,
        "table_fg": p.fg,
        "table_alt_bg": p.alt_bg,
        "table_grid_fg": p.grid,
        "header_bg": p.header_bg,
        "header_fg": p.header_fg,
        "header_grid_fg": p.grid,
        "top_left_bg": p.header_bg,
        "index_bg": p.header_bg,
        "index_fg": p.header_fg,
        "table_selected_cells_bg": p.select_bg,
        "table_selected_cells_fg": p.select_fg,
        "table_selected_rows_bg": p.select_bg,
        "table_selected_columns_bg": p.select_bg,
    }
