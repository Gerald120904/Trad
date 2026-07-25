"""Atomic Parquet persistence and DuckDB views for market data."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
from pydantic import BaseModel, ConfigDict


class StorageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    parquet_dir: Path
    duckdb_path: Path


def write_parquet_atomic(frame: pd.DataFrame, destination: Path) -> None:
    """Write a parquet file using an adjacent temporary file and atomic replace."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    frame.to_parquet(temporary, index=False)
    os.replace(temporary, destination)


def refresh_duckdb_views(config: StorageConfig) -> None:
    """Expose stored Parquet datasets through read-only-style DuckDB views."""

    config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_root = config.parquet_dir.resolve().as_posix().replace("'", "''")
    with duckdb.connect(str(config.duckdb_path)) as connection:
        connection.execute(
            f"""
            CREATE OR REPLACE VIEW klines AS
            SELECT * FROM read_parquet('{parquet_root}/klines/**/*.parquet',
                                      union_by_name = true)
            """
        )
        connection.execute(
            f"""
            CREATE OR REPLACE VIEW agg_trades AS
            SELECT * FROM read_parquet('{parquet_root}/agg_trades/**/*.parquet',
                                      union_by_name = true)
            """
        )
