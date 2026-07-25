from decimal import Decimal

from src.execution.exchange_filters import (
    ExchangeFilterCache,
    ExchangeFilterConfig,
    validate_order_size,
)


SYMBOL_INFO = {
    "symbol": "BTCUSDT",
    "filters": [
        {"filterType": "PRICE_FILTER", "minPrice": "0.10", "maxPrice": "1000000", "tickSize": "0.10"},
        {"filterType": "LOT_SIZE", "minQty": "0.001", "maxQty": "100", "stepSize": "0.001"},
        {"filterType": "MARKET_LOT_SIZE", "minQty": "0.002", "maxQty": "50", "stepSize": "0.002"},
        {"filterType": "MIN_NOTIONAL", "minNotional": "10"},
        {"filterType": "MAX_NUM_ORDERS", "maxNumOrders": 5},
        {"filterType": "MAX_NUM_ALGO_ORDERS", "maxNumAlgoOrders": 2},
    ],
}


class FakeClient:
    calls = 0

    def get_symbol_info(self, symbol: str) -> dict[str, object]:
        self.calls += 1
        assert symbol == "BTCUSDT"
        return SYMBOL_INFO


def test_exact_minimum_is_valid() -> None:
    result = validate_order_size(SYMBOL_INFO, Decimal("0.001"), Decimal("10000.00"))
    assert result.accepted


def test_just_below_minimum_and_rounding_are_rejected() -> None:
    result = validate_order_size(SYMBOL_INFO, "0.0009", "10000.00")
    assert "quantity_below_minimum" in result.reasons
    assert "quantity_not_aligned_to_step_size" in result.reasons


def test_market_lot_size_is_used_for_market_order() -> None:
    result = validate_order_size(SYMBOL_INFO, "0.001", "10000.00", order_type="MARKET")
    assert "quantity_below_minimum" in result.reasons


def test_tick_notional_and_order_counts_are_checked() -> None:
    result = validate_order_size(
        SYMBOL_INFO, "0.001", "9999.95", open_orders=5, open_algo_orders=2
    )
    assert set(result.reasons) == {
        "price_not_aligned_to_tick_size",
        "notional_below_minimum",
        "max_open_orders_reached",
        "max_open_algo_orders_reached",
    }


def test_cache_expires(tmp_path) -> None:
    client = FakeClient()
    now = [100.0]
    cache = ExchangeFilterCache(
        client,
        ExchangeFilterConfig(cache_path=tmp_path / "exchange.json", cache_ttl_seconds=10),
        clock=lambda: now[0],
    )
    assert cache.get("btcusdt")["symbol"] == "BTCUSDT"
    cache.get("BTCUSDT")
    assert client.calls == 1
    now[0] = 111.0
    cache.get("BTCUSDT")
    assert client.calls == 2
