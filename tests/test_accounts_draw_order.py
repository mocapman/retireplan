from decimal import Decimal

import pytest

from retireplan.engine.accounts import (
    calculate_brokerage_sale_tax_character,
    parse_draw_order,
    withdraw_with_order,
)


def test_parse_draw_order_accepts_known_accounts_in_any_order():
    assert parse_draw_order("Brokerage, Roth, IRA") == ("Brokerage", "Roth", "IRA")
    assert parse_draw_order("IRA, Brokerage, Roth") == ("IRA", "Brokerage", "Roth")


@pytest.mark.parametrize(
    ("draw_order", "message"),
    [
        ("Brokerage, Roth", "exactly three accounts"),
        ("Brokerage, Roth, IRA, Cash", "exactly three accounts"),
        ("Brokerage, , IRA", "empty account name"),
        ("Brokerage, Cash, IRA", "invalid account name"),
        ("Brokerage, Roth, Roth", "duplicate account name"),
    ],
)
def test_parse_draw_order_rejects_invalid_values(draw_order, message):
    with pytest.raises(ValueError, match=message):
        parse_draw_order(draw_order)


def test_withdraw_with_order_preserves_valid_drawdown_behavior():
    result = withdraw_with_order(
        Decimal("100"),
        Decimal("50"),
        Decimal("25"),
        Decimal("125"),
        ("Brokerage", "Roth", "IRA"),
    )

    assert result == (
        Decimal("100"),
        Decimal("25"),
        Decimal("0"),
        Decimal("0"),
        Decimal("25"),
        Decimal("25"),
        Decimal("0"),
    )


def test_brokerage_draw_within_cash_creates_zero_capital_gain():
    result = calculate_brokerage_sale_tax_character(
        Decimal("800"),
        Decimal("1000"),
        Decimal("7500"),
        Decimal("2000"),
    )

    assert result.cash_used == Decimal("800")
    assert result.holdings_sold == Decimal("0")
    assert result.capital_gain == Decimal("0")


def test_brokerage_draw_beyond_cash_uses_holdings_gain_ratio():
    result = calculate_brokerage_sale_tax_character(
        Decimal("800"),
        Decimal("500"),
        Decimal("7500"),
        Decimal("2000"),
    )

    assert result.cash_used == Decimal("500")
    assert result.holdings_sold == Decimal("300")
    assert float(result.gain_ratio) == pytest.approx(2000 / 9500)
    assert float(result.capital_gain) == pytest.approx(300 * (2000 / 9500))
    assert float(result.basis_used) == pytest.approx(300 - (300 * (2000 / 9500)))


def test_brokerage_draw_with_zero_holdings_value_creates_zero_capital_gain():
    result = calculate_brokerage_sale_tax_character(
        Decimal("800"),
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
    )

    assert result.cash_used == Decimal("0")
    assert result.holdings_sold == Decimal("800")
    assert result.gain_ratio == Decimal("0")
    assert result.capital_gain == Decimal("0")


@pytest.mark.parametrize(
    "order",
    [
        ("Brokerage", "Roth"),
        ("Brokerage", "", "IRA"),
        ("Brokerage", "Cash", "IRA"),
        ("Brokerage", "Roth", "Roth"),
    ],
)
def test_withdraw_with_order_rejects_invalid_order_tuples(order):
    with pytest.raises(ValueError):
        withdraw_with_order(
            Decimal("100"),
            Decimal("50"),
            Decimal("25"),
            Decimal("10"),
            order,
        )
