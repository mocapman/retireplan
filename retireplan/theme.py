from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

# External widgets are optional at import-time so unit tests don’t hard-depend
try:
    from ttkbootstrap import Style  # type: ignore
except Exception:  # pragma: no cover
    Style = object  # type: ignore

try:
    from tksheet import Sheet  # type: ignore
except Exception:  # pragma: no cover
    Sheet = object  # type: ignore


@dataclass(frozen=True)
class ThemeProfile:
    name: str  # "Light" | "Dark"
    ttk_theme: str  # ttkbootstrap theme key
    sheet_options: Dict[str, str]
    zebra_even_bg: str  # even-row background; odd rows use table_bg


_THEMES: Dict[str, ThemeProfile] = {
    "Light": ThemeProfile(
        name="Light",
        ttk_theme="yeti",
        sheet_options={
            "table_bg": "#ffffff",
            "table_fg": "#212529",
            "table_grid_fg": "#cfd4da",
            "table_selected_cells_bg": "#0d6efd",
            "table_selected_cells_fg": "#ffffff",
            "header_bg": "#e9ecef",
            "header_fg": "#212529",
            "index_bg": "#f8f9fa",
            "index_fg": "#212529",
            "top_left_bg": "#e9ecef",
            "frame_bg": "#ffffff",
        },
        zebra_even_bg="#f1f3f5",
    ),
    "Dark": ThemeProfile(
        name="Dark",
        ttk_theme="darkly",
        sheet_options={
            "table_bg": "#1f2327",
            "table_fg": "#e6e6e6",
            "table_grid_fg": "#343a40",
            "table_selected_cells_bg": "#375a7f",
            "table_selected_cells_fg": "#ffffff",
            "header_bg": "#2c2f33",
            "header_fg": "#e6e6e6",
            "index_bg": "#262a2e",
            "index_fg": "#e6e6e6",
            "top_left_bg": "#2c2f33",
            "frame_bg": "#1f2327",
        },
        # closer greys for subtle zebra
        zebra_even_bg="#24282c",
    ),
}

_current: str = "Dark"  # default you asked for


def current_name() -> str:
    return _current


def profile(name: Optional[str] = None) -> ThemeProfile:
    key = name or _current
    if key not in _THEMES:
        key = "Dark"
    return _THEMES[key]


def set_current(name: str) -> None:
    global _current
    _current = name if name in _THEMES else "Dark"


def apply_to_style(style: Style) -> None:
    """Apply ttkbootstrap theme."""
    style.theme_use(profile().ttk_theme)


def apply_to_sheet(sheet: Sheet) -> None:
    """Apply tksheet palette and zebra striping to an existing Sheet."""
    p = profile()
    try:
        sheet.set_options(**p.sheet_options)
    except Exception:
        pass
    _apply_zebra(sheet, even_bg=p.zebra_even_bg)


def _apply_zebra(sheet: Sheet, *, even_bg: str) -> None:
    """Even rows get even_bg; odd rows remain at table_bg defined in options."""
    try:
        data = sheet.get_sheet_data()
        n = len(data)
        sheet.dehighlight_all()
        even_rows = list(range(0, n, 2))
        if even_rows:
            sheet.highlight_rows(rows=even_rows, bg=even_bg, fg=None)
    except Exception:
        pass
