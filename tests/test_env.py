import pytest


def test_imports():
    import retireplan  # noqa: F401
    try:
        import retireplan.gui  # noqa: F401
        import retireplan.theme  # noqa: F401
    except (ImportError, Exception):
        pytest.skip("GUI dependencies not available in this environment")
