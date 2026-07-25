from __future__ import annotations

from datetime import UTC, datetime

from .config import GateConfig
from .download import dates


def audit(con, config: GateConfig, files: list[dict], ingest_errors: list[dict]) -> dict:
    scope = "market='spot' AND symbol=? AND source_date BETWEEN ? AND ?"
    params = [config.symbol, config.start_date, config.end_date]
    scalar = lambda sql: int(con.execute(sql, params).fetchone()[0])
    tests = []

    def add(name, observed, expected=0):
        tests.append({"name": name, "passed": observed == expected,
                      "observed": observed, "expected": expected})

    expected_days = len(list(dates(config.start_date, config.end_date)))
    add("daily_file_coverage", sum(bool(x["ok"]) for x in files), expected_days)
    add("ingest_errors", len(ingest_errors))
    total = scalar(f"SELECT count(*) FROM aggtrades WHERE {scope}")
    tests.append({"name": "nonempty_dataset", "passed": total > 0,
                  "observed": total, "expected": ">0"})
    add("invalid_ids", scalar(f"""SELECT count(*) FROM aggtrades WHERE {scope}
      AND (agg_trade_id<0 OR first_trade_id<0 OR last_trade_id<first_trade_id)"""))
    add("duplicate_ids", scalar(f"""SELECT coalesce(sum(n-1),0) FROM
      (SELECT count(*) n FROM aggtrades WHERE {scope} GROUP BY agg_trade_id HAVING n>1)"""))
    add("duplicate_rows", scalar(f"""SELECT coalesce(sum(n-1),0) FROM
      (SELECT count(*) n FROM aggtrades WHERE {scope} GROUP BY
       agg_trade_id,price,quantity,first_trade_id,last_trade_id,raw_timestamp,
       is_buyer_maker,is_best_match HAVING count(*)>1)"""))
    add("agg_id_discontinuities", scalar(f"""WITH x AS (SELECT agg_trade_id,
      lag(agg_trade_id) OVER(ORDER BY source_date,source_row) p FROM aggtrades WHERE {scope})
      SELECT count(*) FROM x WHERE p IS NOT NULL AND agg_trade_id<>p+1"""))
    add("underlying_id_discontinuities", scalar(f"""WITH x AS (SELECT first_trade_id,
      lag(last_trade_id) OVER(ORDER BY source_date,source_row) p FROM aggtrades WHERE {scope})
      SELECT count(*) FROM x WHERE p IS NOT NULL AND first_trade_id<>p+1"""))
    add("timestamp_regressions", scalar(f"""WITH x AS (SELECT timestamp_ms,
      lag(timestamp_ms) OVER(ORDER BY source_date,source_row) p FROM aggtrades WHERE {scope})
      SELECT count(*) FROM x WHERE p IS NOT NULL AND timestamp_ms<p"""))
    add("invalid_prices_or_quantities", scalar(
        f"SELECT count(*) FROM aggtrades WHERE {scope} AND (price<=0 OR quantity<=0)"))
    add("timestamp_date_mismatch", scalar(
        f"SELECT count(*) FROM aggtrades WHERE {scope} AND event_time::DATE<>source_date"))
    missing = con.execute("""SELECT count(*) FROM generate_series(?::DATE,?::DATE,INTERVAL 1 DAY)d(day)
      LEFT JOIN (SELECT source_date,count(*) n FROM aggtrades WHERE market='spot' AND symbol=?
      GROUP BY source_date)a ON d.day::DATE=a.source_date WHERE coalesce(n,0)=0""",
      [config.start_date, config.end_date, config.symbol]).fetchone()[0]
    add("missing_ingested_days", int(missing))
    views = {r[0] for r in con.execute("SELECT view_name FROM duckdb_views()").fetchall()}
    add("required_views", len({"v_aggtrades_clean","v_aggtrades_daily_stats",
                              "v_aggtrades_quality"} - views))
    return {"schema_version": 1, "generated_at_utc": datetime.now(UTC).isoformat(),
            "status": "PASS" if all(t["passed"] for t in tests) else "FAIL",
            "market": "spot", "symbol": config.symbol,
            "start_date": str(config.start_date), "end_date": str(config.end_date),
            "total_rows": total, "tests": tests, "file_checks": files,
            "ingest_errors": ingest_errors}
