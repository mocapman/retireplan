from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, Any
import csv

from retireplan import schema


def export_rows_csv(rows: Iterable[Dict[str, Any]], path: str | Path) -> None:
    """
    Write rows in exact schema order with schema labels as headers.
    """
    keys = schema.keys()
    headers = schema.labels()

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        for r in rows:
            w.writerow([r.get(k, None) for k in keys])
