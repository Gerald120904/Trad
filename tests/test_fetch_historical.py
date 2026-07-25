from datetime import UTC, datetime

import pytest

from src.data.fetch_historical import (
    AggTradesRequest,
    HistoricalRequest,
    agg_trades_frame,
    iter_agg_trades,
    iter_klines,
    klines_frame,
    utc_ms,
)
from scripts.download_historical import _batches


class FakeClient:
    def __init__(self) -> None:
        self.kline_calls = 0
        self.trade_calls = 0

    def get_klines(self, **_: object) -> list[list[object]]:
        self.kline_calls += 1
        if self.kline_calls == 1:
            return [
                [1000, "1", "2", "0.5", "1.5", "10", 1999, "15", 3, "6", "9", "0"],
                [2000, "1.5", "2.5", "1", "2", "12", 2999, "24", 4, "7", "14", "0"],
            ]
        return []

    def get_aggregate_trades(self, **_: object) -> list[dict[str, object]]:
        self.trade_calls += 1
        if self.trade_calls == 1:
            return [
                {"a": 7, "p": "2", "q": "3", "f": 9, "l": 10, "T": 1500, "m": False, "M": True}
            ]
        return []


def test_kline_pagination_and_schema() -> None:
    rows = list(iter_klines(FakeClient(), HistoricalRequest(symbol="BTCUSDT", interval="15m", start_ms=1000, end_ms=3000)))
    frame = klines_frame(rows, "BTCUSDT", "15m")
    assert len(frame) == 2
    assert str(frame.loc[0, "open"]) == "1"
    assert frame.loc[0, "open_time"].tzinfo is not None
    assert "ignore" not in frame


def test_aggregate_trade_mapping() -> None:
    rows = list(iter_agg_trades(FakeClient(), AggTradesRequest(symbol="BTCUSDT", start_ms=1000, end_ms=2000)))
    frame = agg_trades_frame(rows, "BTCUSDT")
    assert frame.loc[0, "aggregate_trade_id"] == 7
    assert frame.loc[0, "is_buyer_maker"] == False  # noqa: E712


def test_aggregate_trade_resume_uses_next_id() -> None:
    client = FakeClient()
    rows = list(
        iter_agg_trades(
            client,
            AggTradesRequest(symbol="BTCUSDT", start_ms=1000, end_ms=2000),
            from_id=7,
        )
    )
    assert [row["a"] for row in rows] == [7]


def test_request_rejects_inverted_range() -> None:
    with pytest.raises(ValueError):
        HistoricalRequest(symbol="BTCUSDT", interval="15m", start_ms=2, end_ms=1)


def test_utc_ms_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError):
        utc_ms(datetime(2025, 1, 1))
    assert utc_ms(datetime(1970, 1, 1, tzinfo=UTC)) == 0


def test_batches_bound_memory_chunk_size() -> None:
    assert list(_batches(range(5), 2)) == [[0, 1], [2, 3], [4]]
