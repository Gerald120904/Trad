"""Resumable forensic scan of official Binance aggTrades ZIP files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def scan_archive(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    anomalies: list[dict[str, Any]] = []
    first_id = last_id = previous_id = None
    first_timestamp = last_timestamp = previous_timestamp = None
    rows = 0
    with zipfile.ZipFile(path) as archive:
        members = [
            member
            for member in archive.infolist()
            if not member.is_dir() and member.filename.lower().endswith(".csv")
        ]
        if len(members) != 1:
            raise ValueError(f"{path.name}: expected exactly one CSV")
        with archive.open(members[0]) as stream:
            for raw_line in stream:
                fields = raw_line.split(b",")
                if not fields[0].lstrip(b"-").isdigit():
                    continue
                rows += 1
                aggregate_id = int(fields[0])
                raw_timestamp = int(fields[5])
                timestamp_ms = (
                    raw_timestamp // 1000
                    if abs(raw_timestamp) >= 100_000_000_000_000
                    else raw_timestamp
                )
                if first_id is None:
                    first_id = aggregate_id
                    first_timestamp = timestamp_ms
                if previous_id is not None and (
                    aggregate_id != previous_id + 1
                    or timestamp_ms < previous_timestamp
                ):
                    anomalies.append(
                        {
                            "source_row": rows,
                            "previous_id": previous_id,
                            "current_id": aggregate_id,
                            "id_step": aggregate_id - previous_id,
                            "estimated_overlap": max(0, previous_id - aggregate_id + 1),
                            "previous_timestamp_ms": previous_timestamp,
                            "current_timestamp_ms": timestamp_ms,
                            "time_regression": timestamp_ms < previous_timestamp,
                        }
                    )
                previous_id = last_id = aggregate_id
                previous_timestamp = last_timestamp = timestamp_ms
    return {
        "file": path.name,
        "sha256": digest,
        "raw_rows": rows,
        "first_id": first_id,
        "last_id": last_id,
        "first_timestamp_ms": first_timestamp,
        "last_timestamp_ms": last_timestamp,
        "anomalies": anomalies,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/raw/spot/BTCUSDT"))
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("reports/phase0/spot_BTCUSDT/source_scan_checkpoint.json"),
    )
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    completed: dict[str, dict[str, Any]] = {}
    if args.checkpoint.exists():
        payload = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        completed = {item["file"]: item for item in payload.get("files", [])}

    archives = sorted(args.root.glob("*.zip"))
    pending = [path for path in archives if path.name not in completed]
    print(
        f"archives={len(archives)} completed={len(completed)} pending={len(pending)}",
        flush=True,
    )
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(scan_archive, str(path)): path.name for path in pending
        }
        for future in as_completed(futures):
            result = future.result()
            completed[result["file"]] = result
            ordered = [completed[name] for name in sorted(completed)]
            atomic_json(
                args.checkpoint,
                {
                    "schema_version": 1,
                    "complete": len(completed) == len(archives),
                    "archive_count": len(archives),
                    "files": ordered,
                },
            )
            print(
                f"completed={len(completed)}/{len(archives)} "
                f"file={result['file']} anomalies={len(result['anomalies'])}",
                flush=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
