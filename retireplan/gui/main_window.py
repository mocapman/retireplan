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

# Find default config - should be in parent directory of gui
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "default_config.yaml")

APP_TITLE = "My Retirement Plan"


class RetirePlanApp:
    def __init__(self) -> None:
        self.root = tb.Window(title=APP_TITLE, themename="darkly")
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
        self.root.geometry("2525x950")
        self.paned = tb.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        input_frame = tb.Frame(self.paned, width=600)
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

        self.root.after(100, lambda: self.paned.sashpos(0, 600))

    def run_plan(self) -> None:
        try:
            config_dict = self.input_panel.get_config_dict()
            self.config_manager.update_config_from_dict(self.cfg, config_dict)
            rows = run_plan(self.cfg)
            self.results_display.load_results(rows)
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
