from retireplan import inputs


def test_load_and_validate_sample():
    cfg = inputs.load_yaml("examples/sample_inputs.yaml")
    assert cfg.filing_status == "MFJ"
    assert cfg.gogo_years >= 0
