# gui/file_operations.py
from __future__ import annotations

import csv
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import ttkbootstrap as tb

from retireplan import schema
from retireplan.precision import round_row


class FileOperations:
    """Handles all file I/O operations for the GUI"""

    def __init__(self, app):
        self.app = app

    def load_config(self):
        """Load configuration from YAML file"""
        file_path = tb.filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    config = yaml.safe_load(f)
                self.app.input_panel.set_config(config)
                self.app.run_plan()
            except Exception as e:
                tb.messagebox.showerror("Error", f"Failed to load config: {e}")

    def save_config(self):
        """Save current configuration to YAML file"""
        file_path = tb.filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
        )
        if file_path:
            try:
                config = self.app.input_panel.get_config_dict()
                with open(file_path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
            except Exception as e:
                tb.messagebox.showerror("Error", f"Failed to save config: {e}")

    def export_csv(self):
        """Export current results to CSV with timestamp"""
        current_rows = self.app.results_display.get_current_rows()
        if not current_rows:
            tb.messagebox.showwarning("Warning", "No data to export")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cfg = self.app.cfg
            settings_str = f"{cfg.draw_order.replace(', ', '_')}_{cfg.gogo_annual}"

            out = Path(f"projections_{settings_str}_{timestamp}.csv")

            keys = schema.keys()
            headers = schema.labels()
            with out.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                w.writerow(headers)
                for r in current_rows:
                    rounded_row = round_row(r)
                    w.writerow([rounded_row.get(k, None) for k in keys])

            # Also save the config that generated this data
            config_out = Path(f"config_{settings_str}_{timestamp}.yaml")
            config = self.app.input_panel.get_config_dict()
            with config_out.open("w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False)

            tb.messagebox.showinfo(
                "Export Complete", f"Data exported to:\n{out}\n{config_out}"
            )

        except Exception as e:
            tb.messagebox.showerror("Error", f"Failed to export: {e}")
