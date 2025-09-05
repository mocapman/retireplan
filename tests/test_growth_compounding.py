from copy import deepcopy

from retireplan import inputs
from retireplan.engine import run_plan


def _assert_growth_identities(cfg, rows):
    for t in range(1, len(rows)):
        prev, cur = rows[t - 1], rows[t]

        b0 = prev["End_Bal_Brokerage"]
        r0 = prev["End_Bal_Roth"]
        i0 = prev["End_Bal_IRA"]

        rmd = cur["RMD"]
        total_need = max(0, cur["Total_Spend"] - cur["SS_Income"])
        rmd_surplus = max(0, rmd - total_need)

        b_exp = round(
            (b0 - cur["Draw_Brokerage"] + rmd_surplus) * (1 + cfg.brokerage_growth)
        )
        r_exp = round(
            (r0 - cur["Draw_Roth"] + cur["Roth_Conversion"]) * (1 + cfg.roth_growth)
        )
        i_exp = round(
            (i0 - rmd - cur["Draw_IRA"] - cur["Roth_Conversion"]) * (1 + cfg.ira_growth)
        )

        assert abs(b_exp - cur["End_Bal_Brokerage"]) <= 2
        assert abs(r_exp - cur["End_Bal_Roth"]) <= 2
        assert abs(i_exp - cur["End_Bal_IRA"]) <= 2


def test_growth_baseline():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    rows = run_plan(cfg)
    _assert_growth_identities(cfg, rows)


def test_growth_with_conversions_and_rmd():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")

    # Ensure conversions pre-Medicare
    cfg2 = deepcopy(cfg)
    cfg2.draw_order = "Brokerage, Roth, IRA"
    cfg2.gogo_annual = cfg2.slow_annual = cfg2.nogo_annual = 30000
    cfg2.balances_brokerage = max(cfg2.balances_brokerage, 200_000)
    cfg2.balances_ira = max(cfg2.balances_ira, 50_000)
    rows2 = run_plan(cfg2)
    _assert_growth_identities(cfg2, rows2)

    # Ensure an RMD year early
    cfg3 = deepcopy(cfg)
    bump_to_rmd = (cfg.rmd_start_age + 1) - (cfg.start_year - cfg.birth_year_you)
    cfg3.start_year += max(0, bump_to_rmd)
    rows3 = run_plan(cfg3)
    _assert_growth_identities(cfg3, rows3)
