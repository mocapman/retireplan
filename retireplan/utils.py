# utils.py
from __future__ import annotations
from datetime import datetime
from pathlib import Path


def generate_filename(prefix: str, cfg, extension: str = "csv") -> Path:
    """
    Generate a filename with timestamp and key settings
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a descriptive string from key settings
    settings_parts = [
        f"draw_{cfg.draw_order[:3]}",
        f"gogo_{cfg.gogo_annual}",
        f"slow_{cfg.slow_annual}",
        f"brokerage_{cfg.balances_brokerage}",
    ]

    settings_str = "_".join(settings_parts)
    # Clean the string for filename safety
    settings_str = "".join(
        c for c in settings_str if c.isalnum() or c in ("_", "-")
    ).rstrip()

    return Path(f"{prefix}_{settings_str}_{timestamp}.{extension}")
