from __future__ import annotations

import os
import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox
from datetime import datetime
import yaml

from retireplan import inputs
from retireplan.engine.core import run_plan
from .input_panel import InputPanel
from .results_display import ResultsDisplay
from .file_operations import FileOperations
from .config_manager import ConfigManager
from . import palette

# Find default config - should be in parent directory of gui
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "default_config.yaml")

APP_TITLE = "My Retirement Plan"
APP_GEOMETRY = "2525x1150"


class RetirePlanApp:
    def __init__(self) -> None:
        self.root = tb.Window(title=APP_TITLE, themename=palette.APP_BOOTSTRAP_THEME)
        self.cfg = None
        self.start_dt = datetime.now()

        # Load initial configuration
        self.load_initial_config()

        # Initialize managers
        self.file_ops = FileOperations(self)
        self.config_manager = ConfigManager()

        # Build UI and run initial plan
        self.build_ui()
        self.run_plan()

    def load_initial_config(self):
        try:
            # print(f"Loading config from: {DEFAULT_CONFIG_PATH}")
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)
            if "column_order" not in config_dict:
                raise ValueError(
                    "Config missing 'column_order' key at top level! Please check your default_config.yaml."
                )
            self.input_panel_config_dict = config_dict.copy()
            self.cfg = inputs.load_yaml(DEFAULT_CONFIG_PATH)
            self.baseline_cfg = inputs.load_yaml(DEFAULT_CONFIG_PATH)
            self.cfg.column_order = config_dict["column_order"]
            # print("Loaded config keys:", list(config_dict.keys()))
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{DEFAULT_CONFIG_PATH}' not found. "
                f"Please create a default configuration file."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default config: {e}")
            raise

    def build_ui(self) -> None:
        self.root.geometry(APP_GEOMETRY)
        self.configure_styles()
        self.paned = tb.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        input_frame = tb.Frame(self.paned, width=610)
        self.paned.add(input_frame, weight=1)

        self.input_panel = InputPanel(
            input_frame, app=self, on_change_callback=self.run_plan
        )
        self.input_panel.pack(fill=tk.BOTH, expand=True)

        output_frame = tb.Frame(self.paned)
        self.paned.add(output_frame, weight=2)

        self.results_display = ResultsDisplay(output_frame, app=self)
        self.results_display.pack(fill=tk.BOTH, expand=True)

        if hasattr(self, "input_panel_config_dict"):
            self.input_panel.set_config(self.input_panel_config_dict)
        else:
            config_dict = self.config_manager.config_to_dict(self.cfg)
            self.input_panel.set_config(config_dict)

        self.root.after(100, lambda: self.paned.sashpos(0, 610))

    def configure_styles(self) -> None:
        style = self.root.style
        self.root.configure(background=palette.MAIN_BG)
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=palette.MAIN_BG)
        style.configure("TLabel", background=palette.MAIN_BG, foreground=palette.TEXT_PRIMARY)
        style.configure(
            "TEntry",
            fieldbackground=palette.INPUT_BG,
            foreground=palette.TEXT_PRIMARY,
            bordercolor=palette.BORDER,
            lightcolor=palette.BORDER,
            darkcolor=palette.BORDER,
        )
        style.map(
            "TEntry",
            fieldbackground=[("readonly", palette.READONLY_BG)],
            foreground=[("readonly", palette.TEXT_PRIMARY)],
            selectbackground=[("readonly", palette.READONLY_BG)],
            selectforeground=[("readonly", palette.TEXT_PRIMARY)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=palette.INPUT_BG,
            foreground=palette.TEXT_PRIMARY,
            bordercolor=palette.BORDER,
            lightcolor=palette.BORDER,
            darkcolor=palette.BORDER,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", palette.INPUT_BG)],
            foreground=[("readonly", palette.TEXT_PRIMARY)],
            selectbackground=[("readonly", palette.INPUT_BG)],
            selectforeground=[("readonly", palette.TEXT_PRIMARY)],
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(12, 7),
            borderwidth=0,
        )
        style.configure(
            "secondary.TButton",
            background=palette.BUTTON_NEUTRAL,
            foreground=palette.TEXT_PRIMARY,
        )
        style.map(
            "secondary.TButton",
            background=[
                ("active", palette.BUTTON_NEUTRAL_ACTIVE),
                ("pressed", palette.BUTTON_NEUTRAL_ACTIVE),
            ],
            foreground=[("active", palette.TEXT_PRIMARY), ("pressed", palette.TEXT_PRIMARY)],
        )
        style.configure(
            "success.TButton",
            background=palette.BUTTON_PRIMARY,
            foreground=palette.DARK_TEXT,
        )
        style.map(
            "success.TButton",
            background=[
                ("active", palette.BUTTON_PRIMARY_ACTIVE),
                ("pressed", palette.BUTTON_PRIMARY_ACTIVE),
            ],
            foreground=[("active", palette.DARK_TEXT), ("pressed", palette.DARK_TEXT)],
        )
        style.configure(
            "primary.TButton",
            background=palette.BUTTON_ACCENT,
            foreground="#FFFFFF",
        )
        style.map(
            "primary.TButton",
            background=[
                ("active", palette.BUTTON_ACCENT_ACTIVE),
                ("pressed", palette.BUTTON_ACCENT_ACTIVE),
            ],
            foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF")],
        )

    def run_plan(self) -> None:
        try:
            config_dict = self.input_panel.get_config_dict()
            self.config_manager.update_config_from_dict(self.cfg, config_dict)
            rows = run_plan(self.cfg)
            self.results_display.load_results(rows)
            self.results_display.append_summary_history(
                self.cfg, getattr(self, "baseline_cfg", None)
            )
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error running plan: {e}")

    def load_config(self):
        self.file_ops.load_config()

    def save_config(self):
        self.file_ops.save_config()

    def export_csv(self):
        self.file_ops.export_csv()

    def run(self):
        self.root.mainloop()


def main() -> None:
    try:
        app = RetirePlanApp()
        app.run()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
