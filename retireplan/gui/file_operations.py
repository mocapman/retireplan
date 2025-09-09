import csv
import yaml
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from retireplan import schema
from retireplan.precision import round_row


class FileOperations:
    """Handles all file I/O operations for the GUI"""

    def __init__(self, app):
        self.app = app

    def load_config(self):
        """Load configuration from YAML file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    config = yaml.safe_load(f)
                # Set config in input panel
                self.app.input_panel.set_config(config)
                # Set column order in cfg for later use (for ResultsDisplay)
                if "column_order" in config:
                    if hasattr(self.app, "cfg"):
                        self.app.cfg.column_order = config["column_order"]
                self.app.run_plan()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")

    def save_config(self):
        """Save current configuration to YAML file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
        )
        if file_path:
            try:
                config = self.app.input_panel.get_config_dict()
                # Add current column order to config
                if hasattr(self.app, "results_display"):
                    column_order = self.app.results_display.get_current_column_order()
                    config["column_order"] = column_order
                with open(file_path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")

    def export_csv(self):
        """Export current results to CSV with config appended"""
        current_rows = self.app.results_display.get_current_rows()
        if not current_rows:
            messagebox.showwarning("Warning", "No data to export")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cfg = self.app.cfg
            settings_str = f"{cfg.draw_order.replace(', ', '_')}_{cfg.target_spend}"

            out = Path(f"Projections_{settings_str}_{timestamp}.csv")

            keys = schema.keys()
            headers = schema.labels()
            with out.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                w.writerow(headers)
                for r in current_rows:
                    rounded_row = round_row(r)
                    w.writerow([rounded_row.get(k, None) for k in keys])

                # Blank line
                w.writerow([])
                # Write a header for config section (optional, helpful for humans)
                w.writerow(["# Config Settings"])
                # Flatten config and write as key,value pairs
                config = self.app.input_panel.get_config_dict()

                def flatten(d, parent_key="", sep="."):
                    items = []
                    for k, v in d.items():
                        new_key = f"{parent_key}{sep}{k}" if parent_key else k
                        if isinstance(v, dict):
                            items.extend(flatten(v, new_key, sep=sep))
                        else:
                            items.append((new_key, v))
                    return items

                flat = flatten(config)
                for k, v in flat:
                    w.writerow([k, v])

            messagebox.showinfo(
                "Export Complete", f"Data and config exported to:\n{out}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
