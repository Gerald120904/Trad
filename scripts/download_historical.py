"""Download phase-0 Binance public data into partitioned Parquet files."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from itertools import islice
from pathlib import Path
from typing import Iterable, Iterator, TypeVar

import pandas as pd
from binance.client import Client

from src.data.fetch_historical import (
    AggTradesRequest,
    HistoricalRequest,
    agg_trades_frame,
    iter_agg_trades,
    iter_klines,
    klines_frame,
    utc_ms,
)
from src.data.storage import StorageConfig, refresh_duckdb_views, write_parquet_atomic

T = TypeVar("T")


def _date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)


def _batches(items: Iterable[T], size: int) -> Iterator[list[T]]:
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--start", type=_date, required=True)
    parser.add_argument("--end", type=_date, required=True)
    parser.add_argument("--intervals", nargs="+", default=["15m", "1h"])
    parser.add_argument("--agg-trades-days", type=int, default=30)
    parser.add_argument("--batch-rows", type=int, default=100_000)
    parser.add_argument(
        "--skip-klines",
        action="store_true",
        help="Keep existing kline files and download only aggregate trades.",
    )
    parser.add_argument(
        "--skip-agg-trades",
        action="store_true",
        help="Keep existing aggregate trades and download only klines.",
    )
    parser.add_argument("--parquet-dir", type=Path, default=Path("data/parquet"))
    parser.add_argument("--duckdb-path", type=Path, default=Path("data/market.duckdb"))
    args = parser.parse_args()

    if args.end <= args.start:
        parser.error("--end must be after --start")
    if args.agg_trades_days < 1:
        parser.error("--agg-trades-days must be at least 1")
    if args.batch_rows < 1:
        parser.error("--batch-rows must be at least 1")
    client = Client("", "")
    symbol = args.symbol.upper()
    if not args.skip_klines:
        for interval in args.intervals:
            request = HistoricalRequest(
                symbol=symbol,
                interval=interval,
                start_ms=utc_ms(args.start),
                end_ms=utc_ms(args.end),
            )
            frame = klines_frame(list(iter_klines(client, request)), symbol, interval)
            destination = args.parquet_dir / "klines" / f"symbol={symbol}" / f"interval={interval}" / "data.parquet"
            write_parquet_atomic(frame, destination)

    if not args.skip_agg_trades:
        trade_start = max(args.start, args.end - timedelta(days=args.agg_trades_days))
        trade_request = AggTradesRequest(
            symbol=symbol,
            start_ms=utc_ms(trade_start),
            end_ms=utc_ms(args.end),
        )
        trade_root = args.parquet_dir / "agg_trades" / f"symbol={symbol}"
        existing_parts = sorted(trade_root.glob("part-*.parquet"))
        first_part = len(existing_parts)
        resume_from_id = None
        if existing_parts:
            first = pd.read_parquet(
                existing_parts[0], columns=["trade_time", "aggregate_trade_id"]
            )
            last = pd.read_parquet(
                existing_parts[-1], columns=["trade_time", "aggregate_trade_id"]
            )
            first_time = first["trade_time"].min()
            last_time = last["trade_time"].max()
            if first_time < pd.Timestamp(trade_start) or last_time >= pd.Timestamp(args.end):
                raise RuntimeError(
                    "Existing aggTrades do not belong to the requested time window; "
                    "use a different --parquet-dir instead of overwriting them"
                )
            resume_from_id = int(last["aggregate_trade_id"].max()) + 1
        batches = _batches(
            iter_agg_trades(client, trade_request, from_id=resume_from_id),
            args.batch_rows,
        )
        for part, batch in enumerate(batches, start=first_part):
            trades = agg_trades_frame(batch, symbol)
            write_parquet_atomic(trades, trade_root / f"part-{part:06d}.parquet")
            print(
                f"aggTrades part={part:06d} rows={len(trades)} "
                f"last_id={trades['aggregate_trade_id'].iloc[-1]}",
                flush=True,
            )
    refresh_duckdb_views(StorageConfig(parquet_dir=args.parquet_dir, duckdb_path=args.duckdb_path))


if __name__ == "__main__":
    main()
