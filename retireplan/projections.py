from __future__ import annotations

from typing import List, Dict, Any, Iterable
import pandas as pd

from retireplan import schema


def to_dataframe(rows: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    """
    Build a DataFrame strictly in schema order. No aliasing or renaming.
    Missing keys become None.
    """
    keys = schema.keys()
    recs: List[Dict[str, Any]] = []
    for r in rows:
        recs.append({k: r.get(k, None) for k in keys})
    df = pd.DataFrame.from_records(recs, columns=keys)
    return df


def to_2d_for_table(
    rows: Iterable[Dict[str, Any]],
) -> tuple[list[str], list[list[Any]]]:
    """
    Return (headers, data) strictly from schema, filtering out default-hidden columns.
    """
    all_keys = schema.keys()
    all_labels = schema.labels()
    visible_mask = [k in schema.visible_keys() for k in all_keys]

    headers = [lbl for lbl, vis in zip(all_labels, visible_mask) if vis]
    keys = [k for k, vis in zip(all_keys, visible_mask) if vis]

    data: List[List[Any]] = []
    for r in rows:
        data.append([r.get(k, None) for k in keys])

    return headers, data
