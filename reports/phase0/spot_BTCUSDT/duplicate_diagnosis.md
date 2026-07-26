# Diagnóstico de duplicados - Fase 0

**Clasificación:** `INTRA_FILE_DUPLICATION`

- Fecha candidata: `2026-02-11`
- Archivo: `BTCUSDT-aggTrades-2026-02-11.zip`
- SHA-256: `e546aac09d5cf0c26f1f7b82d38460564596800491752dfa9cb3b5bb34a96ed9`
- Filas crudas: `2102072`
- Filas cargadas: `2102072`
- IDs duplicados: `2000`
- Filas duplicadas excedentes: `3000`
- Rango duplicado: `3856672511` a `3856674510`
- IDs con valores conflictivos: `0`

El ZIP oficial contiene dos retrocesos internos en las filas 2,001 y 3,001.
DuckDB cargó exactamente el número de filas crudas, por lo que no duplicó la
carga. Las copias son idénticas y proceden del mismo CSV oficial. No se
modificó ni eliminó ninguna fila.

Corrección mínima propuesta: conservar una tabla raw inmutable y construir
una capa canónica determinista que mantenga la primera ocurrencia exacta por
`market`, `symbol` y `agg_trade_id`. La normalización debe rechazar cualquier
ID con valores conflictivos y reportar explícitamente los 3,000 duplicados
exactos eliminados.
