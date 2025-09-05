import tempfile
from pathlib import Path

from retireplan import inputs, projections
from retireplan.engine import run_plan

COLUMNS_CHECK = [
    "Year",
    "Taxes",
    "MAGI",
    "End_Bal_IRA",
    "End_Bal_Brokerage",
    "End_Bal_Roth",
    "Total_Assets",
]


def test_engine_equals_csv_roundtrip():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    df = projections.to_dataframe(rows)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "proj.csv"
        df.to_csv(p, index=False)
        df2 = projections.pd.read_csv(p)

    for a, b in zip(df.to_dict("records"), df2.to_dict("records")):
        for k in COLUMNS_CHECK:
            assert int(a[k]) == int(b[k])
