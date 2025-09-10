#!/usr/bin/env python3
"""
/home/runner/work/retireplan/retireplan/retireplan/utils.py

Utility functions for retirement planning application.

This module provides general utility functions including filename generation
with timestamps and configuration-based naming for output files.

Author: Retirement Planning Team
License: MIT  
Last Updated: 2024-01-10
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path


def generate_filename(prefix: str, cfg, extension: str = "csv") -> Path:
    """
    Generate a descriptive filename with timestamp and key configuration settings.
    
    Creates filenames that include key parameters from the retirement plan
    configuration, making it easier to identify and compare different
    plan scenarios in output files.
    
    Args:
        prefix: Base name for the file (e.g., "retirement_plan")
        cfg: Configuration object containing plan parameters
        extension: File extension without dot (e.g., "csv", "xlsx")
        
    Returns:
        Path object with generated filename
        
    Example:
        generate_filename("plan", cfg, "csv") might return:
        "plan_draw_Bro_target_75000_gogo_100pct_brokerage_500000_20240110_143052.csv"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a descriptive string from key configuration settings
    # These help identify different scenarios in output files
    settings_parts = [
        f"draw_{cfg.draw_order[:3]}",  # First 3 chars of draw order
        f"target_{cfg.target_spend}",
        f"gogo_{cfg.gogo_percent}pct",
        f"brokerage_{cfg.balances_brokerage}",
    ]

    settings_str = "_".join(settings_parts)
    
    # Clean the string for filename safety (remove special characters)
    settings_str = "".join(
        c for c in settings_str if c.isalnum() or c in ("_", "-")
    ).rstrip()

    return Path(f"{prefix}_{settings_str}_{timestamp}.{extension}")
