from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from retireplan import inputs, projections
from retireplan.engine import run_plan

KEYS = [
    "Year",
    "Age_You",
    "Age_Spouse",
    "Phase",
    "Living",
    "Spend_Target",
    "Taxes",
    "SS_Income",
    "Draw_IRA",
    "Draw_Brokerage",
    "Draw_Roth",
    "Roth_Conversion",
    "RMD",
    "MAGI",
    "Shortfall",
    "End_Bal_IRA",
    "End_Bal_Brokerage",
    "End_Bal_Roth",
    "Total_Assets",
]


@dataclass
class Pick:
    name: str
    predicate: callable


def first(rows):
    return rows[0] if rows else None


def first_pre_medicare(rows, aca_age):
    for r in rows:
        if r["Age_You"] < aca_age:
            return r
    return None


def first_post_medicare(rows, aca_age):
    for r in rows:
        if r["Age_You"] >= aca_age:
            return r
    return None


def first_rmd(rows):
    for r in rows:
        if r["RMD"] > 0:
            return r
    return None


def summarize_rows(rows, picks: list[Pick]) -> pd.DataFrame:
    out = []
    for p in picks:
        row = p.predicate(rows)
        if row is None:
            out.append({"View": p.name, "Note": "N/A"})
        else:
            d = {k: row.get(k, None) for k in KEYS}
            d["View"] = p.name
            out.append(d)
    return pd.DataFrame(out)


def run_scenario(name: str, cfg, outdir: Path, picks: list[Pick]) -> pd.DataFrame:
    rows = run_plan(cfg)
    df = projections.to_dataframe(rows)
    (outdir / f"{name}.csv").write_text(df.to_csv(index=False), encoding="utf-8")

    summary = summarize_rows(
        rows,
        picks,
    )
    (outdir / f"{name}__summary.csv").write_text(
        summary.to_csv(index=False), encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run RetirePlan scenario sweep.")
    ap.add_argument("--cfg", default="examples/sample_inputs.yaml", help="Inputs YAML.")
    ap.add_argument("--out", default="out", help="Output directory.")
    ap.add_argument("--verbose", action="store_true", help="Print summaries.")
    args = ap.parse_args(argv)

    cfg_base = inputs.load_yaml(args.cfg)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    picks = [
        Pick("Start", first),
        Pick(
            "PreMedicare", lambda rows: first_pre_medicare(rows, cfg_base.aca_end_age)
        ),
        Pick(
            "PostMedicare", lambda rows: first_post_medicare(rows, cfg_base.aca_end_age)
        ),
        Pick("FirstRMD", first_rmd),
    ]

    summaries: list[tuple[str, pd.DataFrame]] = []

    # 1) Baseline: IRA -> Brokerage -> Roth
    cfg1 = deepcopy(cfg_base)
    cfg1.draw_order = "IRA, Brokerage, Roth"
    summaries.append(
        ("baseline_ira_first", run_scenario("baseline_ira_first", cfg1, outdir, picks))
    )

    # 2) Alternate draw order
    cfg2 = deepcopy(cfg_base)
    cfg2.draw_order = "Brokerage, Roth, IRA"
    summaries.append(
        (
            "alt_brokerage_first",
            run_scenario("alt_brokerage_first", cfg2, outdir, picks),
        )
    )

    # 3) Headroom for conversions (lower spends + more brokerage)
    cfg3 = deepcopy(cfg_base)
    cfg3.draw_order = "Brokerage, Roth, IRA"
    cfg3.gogo_annual = 30000
    cfg3.slow_annual = 30000
    cfg3.nogo_annual = 30000
    cfg3.balances_brokerage = max(cfg3.balances_brokerage, 200_000)
    cfg3.balances_ira = max(50_000, cfg3.balances_ira)
    summaries.append(
        (
            "pre_medicare_magi_fill",
            run_scenario("pre_medicare_magi_fill", cfg3, outdir, picks),
        )
    )

    # 4) Post-Medicare scenario (no conversions)
    cfg4 = deepcopy(cfg_base)
    years_to_bump = (cfg_base.aca_end_age + 1) - (
        cfg_base.start_year - cfg_base.birth_year_you
    )
    cfg4.start_year += max(0, years_to_bump)
    summaries.append(
        ("post_medicare", run_scenario("post_medicare", cfg4, outdir, picks))
    )

    # 5) Force RMD early
    cfg5 = deepcopy(cfg_base)
    years_to_rmd = (cfg_base.rmd_start_age + 1) - (
        cfg_base.start_year - cfg_base.birth_year_you
    )
    cfg5.start_year += max(0, years_to_rmd)
    cfg5.gogo_annual = 20000
    cfg5.slow_annual = 20000
    cfg5.nogo_annual = 20000
    summaries.append(("rmd_forced", run_scenario("rmd_forced", cfg5, outdir, picks)))

    # 6) Large event expense to test cash logic
    cfg6 = deepcopy(cfg_base)
    # Engine currently treats events via API; here we emulate by bumping spend target using inputs:
    cfg6.gogo_annual = cfg6.gogo_annual + 50_000
    summaries.append(("large_event", run_scenario("large_event", cfg6, outdir, picks)))

    # Print combined summary
    if args.verbose:
        for name, df in summaries:
            print(f"=== {name} ===")
            print(df.to_string(index=False))
            print()

    # Also write a combined CSV
    combined = pd.concat(
        [df.assign(Scenario=name) for name, df in summaries], ignore_index=True
    )
    (outdir / "combined_summary.csv").write_text(
        combined.to_csv(index=False), encoding="utf-8"
    )

    print(f"Wrote scenario CSVs and summaries to: {outdir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
