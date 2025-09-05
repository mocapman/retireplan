from __future__ import annotations

# Edit these if you want to update policy values.
# Brackets are [(upper_limit, rate)] with upper_limit in TAXABLE INCOME dollars.
FED_BRACKETS = {
    "Single": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
    "MFJ": [
        (23200, 0.10),
        (94300, 0.12),
        (201050, 0.22),
        (383900, 0.24),
        (487450, 0.32),
        (731200, 0.35),
        (float("inf"), 0.37),
    ],
}

# Social Security provisional income thresholds (stable in law)
SS_THRESHOLDS = {
    "Single": (25000.0, 34000.0),  # 0%, up to 50%, up to 85%
    "MFJ": (32000.0, 44000.0),
}

# Default COLA assumption for SS compounding after start (engine uses inflation for now)
SS_COLA_DEFAULT = 0.0
