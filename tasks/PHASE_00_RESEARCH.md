# PHASE_00_RESEARCH.md — Investigación y contratos de datos

## Objetivo de esta fase

Preparar el terreno de datos antes de escribir cualquier lógica de
estrategia o riesgo. Esta fase NO coloca órdenes, ni siquiera simuladas.

## Tareas

1. Setup del repositorio: `pyproject.toml`, entorno virtual, estructura de
   carpetas de `SYSTEM_SPEC.md` sección 3 (vacías con `__init__.py` donde
   corresponda).
2. Implementar `src/data/fetch_historical.py`:
   - Descargar klines históricos (BTCUSDT, 15m y 1h) de Binance para el
     rango de tiempo más largo disponible razonable (empezar con 1-2 años).
   - Descargar aggTrades para el mismo par (al menos un periodo reciente
     representativo, ya que el volumen de datos es grande).
   - Guardar todo en Parquet vía DuckDB, con esquema documentado en
     `DATA_CONTRACTS.md` (actualizar ese archivo si el esquema real difiere).
3. Implementar `src/execution/exchange_filters.py`:
   - Consultar `exchangeInfo` para BTCUSDT.
   - Cachear localmente con expiración configurable.
   - Exponer una función `validate_order_size(symbol, qty, price)` que
     aplique `LOT_SIZE`, `MIN_NOTIONAL`, `PRICE_FILTER`, etc.
4. Escribir tests (`tests/`) para:
   - La descarga de datos (con datos de ejemplo mockeados, no llamando a la
     API real en cada test).
   - `validate_order_size` con casos límite (justo en el mínimo, justo
     debajo, redondeos de `LOT_SIZE`).
5. NO implementar todavía `orderbook_recorder.py` en profundidad — solo
   dejar el archivo con la interfaz definida y un comentario explicando que
   se activará cuando se decida estudiar estrategias de order book (ver
   `DATA_CONTRACTS.md` sección 1).

## Checklist de salida de esta fase

- [x] Datos históricos de klines y aggTrades descargados y guardados en
      DuckDB/Parquet, con un script reproducible (`scripts/`)
- [x] `exchange_filters.py` funcional y testeado, sin valores hardcodeados
- [x] Tests pasando (`pytest`)
- [x] Ningún código de este momento coloca órdenes de ningún tipo
- [x] `README.md` actualizado marcando esta fase como completa

Resultado: **PASS**, 2026-07-25. La compuerta automática auditó 5,245,524
`aggTrades` Spot oficiales de BTCUSDT entre 2026-07-18 y 2026-07-24, con
checksums oficiales, carga estricta y cero fallos de integridad.

## Decisiones documentadas

- **2026-07-25 — Ventana de `aggTrades`:** el usuario eligió explícitamente
  una ventana reciente de 7 días. Se conservará la muestra completa en
  Parquet y se validarán rango temporal, IDs, duplicados, precios y
  cantidades antes de cerrar la fase.
