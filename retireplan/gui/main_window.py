# gui/main_window.py
from __future__ import annotations

import ctypes
import os
import tkinter as tk
import ttkbootstrap as tb
from datetime import datetime
from pathlib import Path
from typing import List

# DPI awareness for Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

from retireplan import inputs
from retireplan.engine import run_plan
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
        """Load configuration from default file"""
        try:
            self.cfg = inputs.load_yaml(DEFAULT_CONFIG_PATH)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{DEFAULT_CONFIG_PATH}' not found. "
                f"Please create a default configuration file."
            )

    def build_ui(self) -> None:
        """Build the main user interface"""
        # Set initial window size
        self.root.geometry("1800x800")

        # Create main paned window
        self.paned = tb.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Input panel on the left
        input_frame = tb.Frame(self.paned, width=600)
        self.paned.add(input_frame, weight=1)

        self.input_panel = InputPanel(input_frame, on_change_callback=self.run_plan)
        self.input_panel.pack(fill=tk.BOTH, expand=True)

        # Results display on the right
        output_frame = tb.Frame(self.paned)
        self.paned.add(output_frame, weight=2)

        self.results_display = ResultsDisplay(output_frame)
        self.results_display.pack(fill=tk.BOTH, expand=True)

        # Set initial values from config
        config_dict = self.config_manager.config_to_dict(self.cfg)
        self.input_panel.set_config(config_dict)

        # Set initial sash position
        self.root.after(100, lambda: self.paned.sashpos(0, 600))

    def run_plan(self) -> None:
        """Run the retirement plan calculation with current inputs"""
        try:
            config_dict = self.input_panel.get_config_dict()
            self.config_manager.update_config_from_dict(self.cfg, config_dict)

            rows = run_plan(self.cfg)
            self.results_display.load_results(rows)
        except Exception as e:
            tb.messagebox.showerror("Calculation Error", f"Error running plan: {e}")

    def load_config(self):
        """Load configuration from file"""
        self.file_ops.load_config()

    def save_config(self):
        """Save current configuration to file"""
        self.file_ops.save_config()

    def export_csv(self):
        """Export current results to CSV"""
        self.file_ops.export_csv()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main() -> None:
    """Main entry point for the GUI application"""
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
