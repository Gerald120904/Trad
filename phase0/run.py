import argparse
from datetime import date
from pathlib import Path

from .audit import audit
from .config import GateConfig
from .database import clear, connect, ingest, views
from .download import download
from .report import write


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", required=True, choices=["spot"])
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--start-date", required=True, type=date.fromisoformat)
    parser.add_argument("--end-date", required=True, type=date.fromisoformat)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    config = GateConfig(market=args.market, symbol=args.symbol.upper(),
                        start_date=args.start_date, end_date=args.end_date,
                        project_root=args.project_root.resolve())
    files = download(config)
    con = connect(config)
    clear(con, config)
    errors = []
    for item in files:
        if not item["ok"]:
            continue
        try:
            count = ingest(con, config, Path(item["archive"]), date.fromisoformat(item["date"]))
            print(f"{item['date']}: {count:,} filas", flush=True)
        except Exception as exc:
            errors.append({"date": item["date"], "error": f"{type(exc).__name__}: {exc}"})
    views(con)
    result = audit(con, config, files, errors)
    con.close()
    write(config, result)
    print(f"Estado: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
