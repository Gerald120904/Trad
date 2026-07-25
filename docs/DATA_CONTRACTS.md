# DATA_CONTRACTS.md — Contratos de datos y esquema de logging

## 1. Datos históricos disponibles vía Binance (y sus límites reales)

- **Klines (velas OHLCV)**: disponibles históricamente en profundidad para
  cualquier par y temporalidad. Incluyen `taker_buy_base_asset_volume`, que
  permite aproximar compra vs. venta a mercado por vela.
- **aggTrades (operaciones agregadas)**: precio, cantidad, y si el
  comprador fue "maker" (`isBuyerMaker`). Permite construir una
  aproximación de delta (compras vs. ventas a mercado) más fina que las
  klines, pero sigue siendo una aproximación, no el order flow exacto.
- **Order Book (libro de órdenes) vía REST**: el endpoint de profundidad
  (`/api/v3/depth`) entrega una **fotografía del momento actual**, no
  historial. **No existe forma de descargar 1-2 años de profundidad
  histórica de Binance vía REST.**

### Esquema Parquet de Fase 0

`klines` se particiona por `symbol` e `interval` y contiene:
`open_time`, `open`, `high`, `low`, `close`, `volume`, `close_time`,
`quote_asset_volume`, `number_of_trades`,
`taker_buy_base_asset_volume`, `taker_buy_quote_asset_volume`, `symbol` e
`interval`. Los tiempos son UTC y los valores monetarios se conservan como
decimales.

`agg_trades` se particiona por `symbol` y contiene: `aggregate_trade_id`,
`price`, `quantity`, `first_trade_id`, `last_trade_id`, `trade_time`,
`is_buyer_maker`, `is_best_match` y `symbol`. `is_buyer_maker=true` significa
que el comprador fue maker; por tanto, la agresión a mercado fue vendedora.

### Implicación obligatoria

**Prohibido** backtestear estrategias de "absorción de órdenes" o
"desequilibrio L2" usando solamente velas o aggTrades históricos —
sería una simulación inventada, no un backtest real. Para ese tipo de
estrategia, el proceso correcto es:

1. Grabar continuamente snapshots del order book (`orderbook_recorder.py`)
   + actualizaciones incrementales vía WebSocket.
2. Reconstruir el libro localmente a partir de esos eventos.
3. Guardar los eventos en Parquet con timestamp preciso.
4. Esperar a acumular una muestra suficiente (semanas/meses, según cuántas
   señales por semana genere el patrón que se quiera estudiar).
5. Recién entonces hacer backtesting basado en ese order book grabado.

Esto significa que cualquier estrategia basada en order book queda **fuera
de alcance** hasta acumular datos propios (ver `STRATEGY_SPEC.md`).

## 2. Esquema de logging obligatorio (JSON estructurado)

Cada evento relevante de decisión debe registrarse con, como mínimo:

```json
{
  "timestamp": "2026-07-25T14:32:10Z",
  "modo": "testnet",
  "estrategia": "volume_breakout_mvp",
  "par": "BTCUSDT",
  "evento": "entrada_evaluada",
  "resultado": "aceptada",
  "razon": "ruptura de resistencia en 61200 con volumen 1.8x promedio de 20 velas",
  "precio_entrada": 61234.50,
  "stop_loss": 60800.00,
  "take_profit": 62100.00,
  "tamano_posicion_usd": 0.50,
  "riesgo_pct_capital": 1.0,
  "capital_total_en_ese_momento": 50.00,
  "filtros_exchange_aplicados": {
    "lot_size_step": "0.00001",
    "min_notional": "10.0"
  }
}
```

Si `resultado` es `"rechazada"`, `razon` debe indicar exactamente en qué
paso de `STRATEGY_SPEC.md` se rechazó (ej. "tamaño de posición menor al
mínimo del exchange").

### Logs separados obligatorios

- `logs/decisiones.jsonl` — cada evaluación de señal, aceptada o rechazada.
- `logs/errores_tecnicos.jsonl` — excepciones, fallos de conexión, órdenes
  rechazadas por el exchange por motivos técnicos (no de estrategia).
- `logs/circuit_breaker.jsonl` — cada activación, con motivo exacto y
  estado del capital.
- `logs/reconciliacion.jsonl` — comparación periódica entre el estado que
  el bot cree tener (posiciones, balance) y lo que el exchange confirma.

## 3. Reconciliación (obligatoria, no opcional)

Cada N minutos (configurable), el bot debe consultar el estado real de la
cuenta en el exchange (posiciones abiertas, órdenes activas, balance) y
compararlo contra su propio estado interno. Cualquier discrepancia debe:
1. Registrarse en `logs/reconciliacion.jsonl`.
2. Generar una alerta inmediata.
3. Si la discrepancia involucra una posición sin stop-loss detectable en el
   exchange, activar el circuit breaker de inmediato.
