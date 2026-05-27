import yaml

from retireplan.inputs import load_yaml


def test_load_yaml_derives_brokerage_balance_from_taxable_detail(tmp_path):
    config = yaml.safe_load(open("retireplan/default_config.yaml", encoding="utf-8"))

    cfg = load_yaml("retireplan/default_config.yaml")

    expected = (
        config["balances"]["brokerage_cash"]
        + config["balances"]["brokerage_cost_basis"]
        + config["balances"]["brokerage_unrealized_gain"]
    )
    assert cfg.balances_brokerage == expected


def test_load_yaml_uses_old_brokerage_balance_as_cash_fallback(tmp_path):
    config = yaml.safe_load(open("retireplan/default_config.yaml", encoding="utf-8"))
    config["balances"] = {
        "brokerage": 12345.0,
        "roth": config["balances"]["roth"],
        "ira": config["balances"]["ira"],
    }
    config_path = tmp_path / "old_config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    cfg = load_yaml(str(config_path))

    assert cfg.balances_brokerage == 12345.0
    assert cfg.brokerage_cash == 12345.0
    assert cfg.brokerage_cost_basis == 0
    assert cfg.brokerage_unrealized_gain == 0
