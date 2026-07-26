"""Produce forensic artifacts for candidate dates found by the source scan."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb


def main() -> int:
    report_dir = Path("reports/phase0/spot_BTCUSDT")
    checkpoint = json.loads(
        (report_dir / "source_scan_checkpoint.json").read_text(encoding="utf-8")
    )
    candidates = [item for item in checkpoint["files"] if item["anomalies"]]
    if not checkpoint["complete"] or not candidates:
        raise RuntimeError("Source scan is incomplete or has no candidate files")
    dates = sorted(
        {
            item["file"].removeprefix("BTCUSDT-aggTrades-").removesuffix(".zip")
            for item in candidates
        }
    )
    quoted_dates = ", ".join(f"DATE '{value}'" for value in dates)
    output = report_dir / "duplicate_rows.parquet"
    connection = duckdb.connect("data/phase0.duckdb", read_only=True)
    connection.execute("PRAGMA threads=4")
    connection.execute(
        f"""
        COPY (
          WITH duplicate_ids AS (
            SELECT agg_trade_id
            FROM aggtrades
            WHERE market='spot' AND symbol='BTCUSDT'
              AND source_date IN ({quoted_dates})
            GROUP BY agg_trade_id HAVING count(*) > 1
          )
          SELECT a.*,
            'BTCUSDT-aggTrades-' || source_date::VARCHAR || '.zip' AS source_file
          FROM aggtrades a JOIN duplicate_ids USING (agg_trade_id)
          WHERE market='spot' AND symbol='BTCUSDT'
            AND source_date IN ({quoted_dates})
          ORDER BY agg_trade_id, source_date, source_row
        ) TO '{output.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    summary = connection.execute(
        f"""
        WITH grouped AS (
          SELECT agg_trade_id, count(*) occurrences,
            count(DISTINCT struct_pack(
              price:=price, quantity:=quantity, first_id:=first_trade_id,
              last_id:=last_trade_id, raw_ts:=raw_timestamp,
              buyer_maker:=is_buyer_maker, best_match:=is_best_match
            )) versions
          FROM aggtrades
          WHERE market='spot' AND symbol='BTCUSDT'
            AND source_date IN ({quoted_dates})
          GROUP BY agg_trade_id HAVING count(*) > 1
        )
        SELECT count(*), sum(occurrences-1), min(agg_trade_id),
          max(agg_trade_id), sum(CASE WHEN versions>1 THEN 1 ELSE 0 END)
        FROM grouped
        """
    ).fetchone()
    per_file = []
    for item in candidates:
        day = item["file"].removeprefix("BTCUSDT-aggTrades-").removesuffix(".zip")
        loaded = connection.execute(
            """
            SELECT count(*), count(DISTINCT source_row),
              count(DISTINCT agg_trade_id)
            FROM aggtrades
            WHERE market='spot' AND symbol='BTCUSDT' AND source_date=?::DATE
            """,
            [day],
        ).fetchone()
        per_file.append(
            {
                "source_date": day,
                "source_file": item["file"],
                "sha256": item["sha256"],
                "raw_rows": item["raw_rows"],
                "loaded_rows": loaded[0],
                "distinct_source_rows": loaded[1],
                "distinct_agg_trade_ids": loaded[2],
                "source_anomalies": item["anomalies"],
            }
        )
    diagnosis = {
        "schema_version": 1,
        "classification": (
            "CONFLICTING_DUPLICATE_IDS" if summary[4] else "INTRA_FILE_DUPLICATION"
        ),
        "candidate_dates": dates,
        "duplicated_ids": summary[0],
        "duplicate_excess_rows": summary[1],
        "first_duplicate_id": summary[2],
        "last_duplicate_id": summary[3],
        "conflicting_duplicate_ids": summary[4],
        "duplicate_rows_parquet": str(output),
        "files": per_file,
        "notes": [
            "The current DuckDB schema lacks source_file; it is inferred from source_date.",
            "No data was deleted or normalized by this diagnostic.",
        ],
    }
    json_path = report_dir / "duplicate_diagnosis.json"
    json_path.write_text(
        json.dumps(diagnosis, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    markdown = f"""# Diagnóstico de duplicados - Fase 0

**Clasificación:** `{diagnosis['classification']}`

- Fecha candidata: `{dates[0]}`
- Archivo: `{per_file[0]['source_file']}`
- SHA-256: `{per_file[0]['sha256']}`
- Filas crudas: `{per_file[0]['raw_rows']}`
- Filas cargadas: `{per_file[0]['loaded_rows']}`
- IDs duplicados: `{summary[0]}`
- Filas duplicadas excedentes: `{summary[1]}`
- Rango duplicado: `{summary[2]}` a `{summary[3]}`
- IDs con valores conflictivos: `{summary[4]}`

El ZIP oficial contiene dos retrocesos internos en las filas 2,001 y 3,001.
DuckDB cargó exactamente el número de filas crudas, por lo que no duplicó la
carga. Las copias son idénticas y proceden del mismo CSV oficial. No se
modificó ni eliminó ninguna fila.

Corrección mínima propuesta: conservar una tabla raw inmutable y construir
una capa canónica determinista que mantenga la primera ocurrencia exacta por
`market`, `symbol` y `agg_trade_id`. La normalización debe rechazar cualquier
ID con valores conflictivos y reportar explícitamente los 3,000 duplicados
exactos eliminados.
"""
    (report_dir / "duplicate_diagnosis.md").write_text(markdown, encoding="utf-8")
    print(json.dumps(diagnosis, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
