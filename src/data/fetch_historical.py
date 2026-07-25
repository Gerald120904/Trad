"""Historical Binance Spot market-data downloader.

This module only reads public endpoints. It never creates orders.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator, Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator


class HistoricalRequest(BaseModel):
    """Validated request for a bounded historical download."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^[A-Z0-9]{5,20}$")
    interval: str = Field(pattern=r"^[1-9][0-9]*[mhdwM]$")
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    page_limit: int = Field(default=1000, ge=1, le=1000)

    @field_validator("end_ms")
    @classmethod
    def end_must_follow_start(cls, value: int, info: Any) -> int:
        start = info.data.get("start_ms")
        if start is not None and value <= start:
            raise ValueError("end_ms must be greater than start_ms")
        return value


class AggTradesRequest(BaseModel):
    """Validated request for aggregate trades."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^[A-Z0-9]{5,20}$")
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    page_limit: int = Field(default=1000, ge=1, le=1000)

    @field_validator("end_ms")
    @classmethod
    def end_must_follow_start(cls, value: int, info: Any) -> int:
        start = info.data.get("start_ms")
        if start is not None and value <= start:
            raise ValueError("end_ms must be greater than start_ms")
        return value


KLINE_COLUMNS = (
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
    "ignore",
)


def _retry(
    call: Callable[..., Sequence[Any]],
    *,
    attempts: int,
    pause_seconds: float,
    **kwargs: Any,
) -> Sequence[Any]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return call(**kwargs)
        except Exception as exc:  # API clients expose different error classes.
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(pause_seconds * (2**attempt))
    assert last_error is not None
    raise last_error


def iter_klines(
    client: Any,
    request: HistoricalRequest,
    *,
    attempts: int = 3,
    pause_seconds: float = 0.25,
) -> Iterator[list[Any]]:
    """Yield klines without duplicates, using closed time bounds."""

    cursor = request.start_ms
    last_open_time = -1
    while cursor < request.end_ms:
        rows = _retry(
            client.get_klines,
            attempts=attempts,
            pause_seconds=pause_seconds,
            symbol=request.symbol,
            interval=request.interval,
            startTime=cursor,
            endTime=request.end_ms - 1,
            limit=request.page_limit,
        )
        if not rows:
            break
        for raw in rows:
            row = list(raw)
            open_time = int(row[0])
            if open_time >= request.end_ms:
                return
            if open_time > last_open_time:
                yield row
                last_open_time = open_time
        next_cursor = int(rows[-1][0]) + 1
        if next_cursor <= cursor:
            raise RuntimeError("Binance kline pagination did not advance")
        cursor = next_cursor


def klines_frame(rows: Sequence[Sequence[Any]], symbol: str, interval: str) -> pd.DataFrame:
    """Convert raw Binance klines to the documented, typed schema."""

    frame = pd.DataFrame(rows, columns=KLINE_COLUMNS)
    if frame.empty:
        return frame.assign(symbol=pd.Series(dtype="string"), interval=pd.Series(dtype="string"))
    numeric = (
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
    )
    for column in numeric:
        frame[column] = frame[column].map(Decimal)
    frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True)
    frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms", utc=True)
    frame["number_of_trades"] = frame["number_of_trades"].astype("int64")
    frame["symbol"] = symbol
    frame["interval"] = interval
    return frame.drop(columns=["ignore"])


def iter_agg_trades(
    client: Any,
    request: AggTradesRequest,
    *,
    from_id: int | None = None,
    attempts: int = 3,
    pause_seconds: float = 0.25,
) -> Iterator[dict[str, Any]]:
    """Yield aggregate trades in ascending ID order without duplicates."""

    cursor = request.start_ms
    last_id = from_id - 1 if from_id is not None else -1
    while cursor < request.end_ms:
        kwargs: dict[str, Any] = {
            "symbol": request.symbol,
            "limit": request.page_limit,
        }
        if from_id is None:
            kwargs.update(startTime=cursor, endTime=request.end_ms - 1)
        else:
            kwargs["fromId"] = from_id
        rows = _retry(
            client.get_aggregate_trades,
            attempts=attempts,
            pause_seconds=pause_seconds,
            **kwargs,
        )
        if not rows:
            break
        emitted = False
        for raw in rows:
            trade = dict(raw)
            trade_id = int(trade["a"])
            trade_time = int(trade["T"])
            if trade_time >= request.end_ms:
                return
            if trade_id > last_id:
                yield trade
                last_id = trade_id
                cursor = trade_time + 1
                emitted = True
        if not emitted:
            raise RuntimeError("Binance aggregate-trade pagination did not advance")
        from_id = last_id + 1


def agg_trades_frame(rows: Sequence[dict[str, Any]], symbol: str) -> pd.DataFrame:
    """Convert Binance aggTrades keys to stable, explicit field names."""

    records = [
        {
            "symbol": symbol,
            "aggregate_trade_id": int(row["a"]),
            "price": Decimal(str(row["p"])),
            "quantity": Decimal(str(row["q"])),
            "first_trade_id": int(row["f"]),
            "last_trade_id": int(row["l"]),
            "trade_time": pd.to_datetime(int(row["T"]), unit="ms", utc=True),
            "is_buyer_maker": bool(row["m"]),
            "is_best_match": bool(row.get("M", True)),
        }
        for row in rows
    ]
    return pd.DataFrame.from_records(records)


def utc_ms(value: datetime) -> int:
    """Convert an aware datetime to Unix milliseconds."""

    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return int(value.astimezone(UTC).timestamp() * 1000)
