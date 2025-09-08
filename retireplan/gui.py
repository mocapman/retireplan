# gui.py (Updated - Simple Entry Point)
"""
Simplified GUI entry point that delegates to the new modular GUI structure.
This maintains backward compatibility while using the new organized code.
"""
from __future__ import annotations

from retireplan.gui.main_window import main

# For backward compatibility - existing code can still call gui.main()
__all__ = ["main"]

if __name__ == "__main__":
    main()
