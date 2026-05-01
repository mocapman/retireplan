import tempfile
from pathlib import Path

import pandas as pd

from retireplan import inputs
from retireplan.engine.core import run_plan

COLUMNS_CHECK = [
    "Year",
    "Taxes_Due",
    "MAGI",
    "IRA_Balance",
    "Brokerage_Balance",
    "Roth_Balance",
    "Total_Assets",
]


def test_engine_equals_csv_roundtrip():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    df = pd.DataFrame(rows)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "proj.csv"
        df.to_csv(p, index=False)
        df2 = pd.read_csv(p)

    for a, b in zip(df.to_dict("records"), df2.to_dict("records")):
        for k in COLUMNS_CHECK:
            assert int(a[k]) == int(b[k])
