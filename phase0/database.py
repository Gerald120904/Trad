from __future__ import annotations

import tempfile
import zipfile
from datetime import date
from pathlib import Path

import duckdb

from .config import GateConfig


def connect(config: GateConfig):
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(config.db_path))
    con.execute("""CREATE TABLE IF NOT EXISTS aggtrades(
      market VARCHAR, symbol VARCHAR, source_date DATE, source_row BIGINT,
      agg_trade_id BIGINT, price DECIMAL(38,18), quantity DECIMAL(38,18),
      first_trade_id BIGINT, last_trade_id BIGINT, raw_timestamp BIGINT,
      timestamp_ms BIGINT, event_time TIMESTAMP, is_buyer_maker BOOLEAN,
      is_best_match BOOLEAN)""")
    return con


def clear(con, config: GateConfig):
    con.execute("DELETE FROM aggtrades WHERE market='spot' AND symbol=? AND source_date BETWEEN ? AND ?",
                [config.symbol, config.start_date, config.end_date])


def ingest(con, config: GateConfig, archive: Path, day: date) -> int:
    with tempfile.TemporaryDirectory(prefix="phase0_") as temporary:
        with zipfile.ZipFile(archive) as zf:
            members = [m for m in zf.infolist() if not m.is_dir() and m.filename.endswith(".csv")]
            csv_path = Path(zf.extract(members[0], temporary))
        escaped = str(csv_path).replace("'", "''")
        first = csv_path.open(encoding="utf-8").readline().split(",", 1)[0].strip()
        header = "false" if first.isdigit() else "true"
        before = con.execute("SELECT count(*) FROM aggtrades").fetchone()[0]
        con.execute(f"""INSERT INTO aggtrades
        SELECT 'spot', ?, ?::DATE, row_number() OVER (),
          column0::BIGINT, column1::DECIMAL(38,18), column2::DECIMAL(38,18),
          column3::BIGINT, column4::BIGINT, column5::BIGINT,
          CASE WHEN abs(column5::BIGINT)>=100000000000000 THEN column5::BIGINT//1000 ELSE column5::BIGINT END,
          epoch_ms(CASE WHEN abs(column5::BIGINT)>=100000000000000 THEN column5::BIGINT//1000 ELSE column5::BIGINT END),
          column6::BOOLEAN, column7::BOOLEAN
        FROM read_csv('{escaped}', header={header}, auto_detect=false,
          columns={{'column0':'VARCHAR','column1':'VARCHAR','column2':'VARCHAR',
          'column3':'VARCHAR','column4':'VARCHAR','column5':'VARCHAR',
          'column6':'VARCHAR','column7':'VARCHAR'}}, strict_mode=true)""",
          [config.symbol, day])
        return con.execute("SELECT count(*) FROM aggtrades").fetchone()[0] - before


def views(con):
    con.execute("""CREATE OR REPLACE VIEW v_aggtrades_clean AS SELECT *,
      NOT is_buyer_maker AS buyer_is_taker, price*quantity AS quote_quantity
      FROM aggtrades WHERE price>0 AND quantity>0""")
    con.execute("""CREATE OR REPLACE VIEW v_aggtrades_daily_stats AS SELECT
      market,symbol,source_date,count(*) row_count,min(event_time) first_event_time,
      max(event_time) last_event_time,min(agg_trade_id) min_id,max(agg_trade_id) max_id
      FROM v_aggtrades_clean GROUP BY market,symbol,source_date""")
    con.execute("""CREATE OR REPLACE VIEW v_aggtrades_quality AS SELECT market,symbol,
      count(*) row_count,count(*) FILTER(WHERE price<=0) invalid_prices,
      count(*) FILTER(WHERE quantity<=0) invalid_quantities
      FROM aggtrades GROUP BY market,symbol""")
