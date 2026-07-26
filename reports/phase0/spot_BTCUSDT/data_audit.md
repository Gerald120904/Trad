# Auditoría de datos - Fase 0

**Estado:** `FAIL`

- Mercado: `spot`
- Símbolo: `BTCUSDT`
- Periodo: `2026-01-26` a `2026-07-24` UTC
- Filas: `199487794`

## Pruebas

| Prueba | Estado | Observado | Esperado |
|---|---|---:|---:|
| `daily_file_coverage` | PASS | `180` | `180` |
| `ingest_errors` | PASS | `0` | `0` |
| `nonempty_dataset` | PASS | `199487794` | `>0` |
| `invalid_ids` | PASS | `0` | `0` |
| `duplicate_ids` | FAIL | `3000` | `0` |
| `duplicate_rows` | FAIL | `3000` | `0` |
| `agg_id_discontinuities` | FAIL | `2` | `0` |
| `underlying_id_discontinuities` | FAIL | `2` | `0` |
| `timestamp_regressions` | FAIL | `2` | `0` |
| `invalid_prices_or_quantities` | PASS | `0` | `0` |
| `timestamp_date_mismatch` | PASS | `0` | `0` |
| `missing_ingested_days` | PASS | `0` | `0` |
| `required_views` | PASS | `0` | `0` |
