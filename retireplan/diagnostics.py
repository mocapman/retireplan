from __future__ import annotations

import argparse

from retireplan import inputs
from retireplan.engine import run_plan
from retireplan.timeline import make_years

ALLOWED_FILING = {"Single", "MFJ"}


def _infl(rate: float, idx: int) -> float:
    return (1.0 + rate) ** idx


def _effective_filing(cfg, living: str) -> str:
    return "MFJ" if (cfg.filing_status == "MFJ" and living == "Joint") else "Single"


def diagnose(cfg_path: str, years_to_show: int = 15) -> int:
    cfg = inputs.load_yaml(cfg_path)

    # Config checks
    print("=== Config checks ===")
    if cfg.filing_status not in ALLOWED_FILING:
        print(
            f"WARNING: filing_status='{cfg.filing_status}' not in {sorted(ALLOWED_FILING)}. "
            f"Engine will use 'Single' every year."
        )
    else:
        print(f"filing_status={cfg.filing_status} OK")

    # Derive years to compare filing/MAGI target expectations
    years = make_years(
        cfg.start_year,
        cfg.birth_year_you,
        cfg.birth_year_spouse,
        cfg.final_age_you,
        cfg.final_age_spouse,
        cfg.gogo_years,
        cfg.slow_years,
    )

    rows = run_plan(cfg)

    print("\n=== Early-year budget breakdown ===")
    print(
        "Year  Living   Filing  Spend  Taxes  SS  Draw_IRA  Draw_Brk  Draw_Roth  Conv  "
        "NeedTot  Provided  Shortfall  MAGI  TargetMAGI"
    )
    for idx, yc in enumerate(years[:years_to_show]):
        r = rows[idx]
        filing = _effective_filing(cfg, r["Living"])
        target_magi = (
            cfg.magi_target_base * _infl(cfg.inflation, idx)
            if (r["Age_You"] < cfg.aca_end_age)
            else 0.0
        )
        need_total = r["Spend_Target"] + r["Taxes"] + r.get("Events_Cash", 0)
        provided = (
            r["SS_Income"]
            + r["RMD"]
            + r["Draw_IRA"]
            + r["Draw_Brokerage"]
            + r["Draw_Roth"]
        )

        print(
            f"{int(r['Year']):4d}  {r['Living']:<7}  {filing:<5}  "
            f"{int(r['Spend_Target']):5d}  {int(r['Taxes']):5d}  {int(r['SS_Income']):5d}  "
            f"{int(r['Draw_IRA']):8d}  {int(r['Draw_Brokerage']):8d}  {int(r['Draw_Roth']):9d}  "
            f"{int(r['Roth_Conversion']):4d}  "
            f"{int(need_total):7d}  {int(provided):8d}  {int(r['Shortfall']):9d}  "
            f"{int(r['MAGI']):5d}  {int(target_magi):10d}"
        )

    print(
        "\nHint: if Filing shows Single during Joint years, fix filing_status to 'MFJ'."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Diagnose config-driven shortfalls and MAGI behavior."
    )
    ap.add_argument("--cfg", default="examples/sample_inputs.yaml")
    ap.add_argument("--years", type=int, default=15)
    args = ap.parse_args(argv)
    return diagnose(args.cfg, args.years)


if __name__ == "__main__":
    raise SystemExit(main())
