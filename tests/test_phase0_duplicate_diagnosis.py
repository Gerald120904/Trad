import json
import zipfile

from scripts.diagnose_phase0_duplicates import scan_archive


def test_scanner_detects_replayed_block(tmp_path):
    archive = tmp_path / "BTCUSDT-aggTrades-2026-01-01.zip"
    rows = [
        "1,100,1,1,1,1767225600000,false,true",
        "2,101,1,2,2,1767225600001,false,true",
        "1,100,1,1,1,1767225600000,false,true",
    ]
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("BTCUSDT-aggTrades-2026-01-01.csv", "\n".join(rows))
    result = scan_archive(str(archive))
    assert result["raw_rows"] == 3
    assert result["anomalies"] == [
        {
            "source_row": 3,
            "previous_id": 2,
            "current_id": 1,
            "id_step": -1,
            "estimated_overlap": 2,
            "previous_timestamp_ms": 1767225600001,
            "current_timestamp_ms": 1767225600000,
            "time_regression": True,
        }
    ]
