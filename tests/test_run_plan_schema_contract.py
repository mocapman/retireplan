from retireplan import schema
from retireplan.engine.core import run_plan
from retireplan.inputs import load_yaml
from tests.test_run_plan_baseline import minimal_two_person_config


def assert_all_rows_contain_schema_keys(rows):
    expected_keys = set(schema.keys())

    assert rows
    for row in rows:
        missing_keys = expected_keys - set(row.keys())
        assert missing_keys == set()


def test_minimal_run_plan_rows_contain_all_schema_keys():
    rows = run_plan(minimal_two_person_config())

    assert_all_rows_contain_schema_keys(rows)


def test_default_config_run_plan_rows_contain_all_schema_keys():
    cfg = load_yaml("retireplan/default_config.yaml")
    rows = run_plan(cfg)

    assert_all_rows_contain_schema_keys(rows)
