from __future__ import annotations

import hashlib
import re
import time
import zipfile
from datetime import date, timedelta
from pathlib import Path

import requests

from .config import GateConfig

BASE_URL = "https://data.binance.vision/data/spot/daily/aggTrades"


def dates(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _get(session: requests.Session, url: str, path: Path) -> bool:
    if path.exists():
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    for attempt in range(3):
        try:
            with session.get(url, stream=True, timeout=(15, 120)) as response:
                if response.status_code == 404:
                    return False
                response.raise_for_status()
                with temporary.open("wb") as output:
                    for chunk in response.iter_content(1024 * 1024):
                        if chunk:
                            output.write(chunk)
            temporary.replace(path)
            return True
        except requests.RequestException:
            temporary.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))
    return False


def download(config: GateConfig) -> list[dict]:
    session = requests.Session()
    session.headers["User-Agent"] = "Gerald-Phase0-Gate/1.0"
    checks = []
    for day in dates(config.start_date, config.end_date):
        stem = f"{config.symbol}-aggTrades-{day.isoformat()}.zip"
        archive = config.raw_dir / stem
        checksum = config.raw_dir / f"{stem}.CHECKSUM"
        item = {"date": day.isoformat(), "archive": str(archive), "ok": False, "error": None}
        try:
            if not _get(session, f"{BASE_URL}/{config.symbol}/{stem}", archive):
                raise FileNotFoundError(f"ZIP no publicado: {day}")
            if not _get(session, f"{BASE_URL}/{config.symbol}/{stem}.CHECKSUM", checksum):
                raise FileNotFoundError(f"CHECKSUM no publicado: {day}")
            match = re.search(r"\b[a-fA-F0-9]{64}\b", checksum.read_text("utf-8"))
            if not match or sha256(archive) != match.group(0).lower():
                raise ValueError("SHA-256 no coincide")
            with zipfile.ZipFile(archive) as zf:
                members = [m for m in zf.infolist() if not m.is_dir() and m.filename.endswith(".csv")]
                if zf.testzip() is not None or len(members) != 1 or members[0].file_size == 0:
                    raise ValueError("ZIP/CSV inválido")
            item["ok"] = True
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        checks.append(item)
    return checks
