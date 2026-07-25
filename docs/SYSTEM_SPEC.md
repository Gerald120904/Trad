# SYSTEM_SPEC.md — Especificación de arquitectura

## 1. Alcance de esta versión

- Binance **Spot** únicamente. Sin margen, sin futuros, sin apalancamiento.
- Un solo par activo a la vez (BTCUSDT por defecto).
- Dirección: solo compras (long-only). Al salir, el capital queda en USDT.
- Un modelo mecánico (reglas explícitas), sin machine learning en esta
  primera versión (ver `STRATEGY_SPEC.md` sección "Fuera de alcance").

## 2. Estados del bot (máquina de estados obligatoria)

```
INICIALIZANDO
    -> Carga config, valida risk-policy.yaml, consulta exchangeInfo,
       verifica conexión al modo activo (testnet/demo/paper/live)

ESPERANDO_SEÑAL
    -> Escucha datos de mercado, evalúa reglas de estrategia
    -> Si no hay señal válida: permanece en este estado
    -> Si hay señal Y pasa el módulo de riesgo: -> ABRIENDO_POSICION
    -> Si hay señal pero NO pasa el módulo de riesgo: registra el rechazo
       y permanece en ESPERANDO_SEÑAL

ABRIENDO_POSICION
    -> Calcula tamaño de posición (riesgo, filtros de exchange, slippage estimado)
    -> Si el tamaño calculado < mínimo del exchange: rechaza, log, vuelve a
       ESPERANDO_SEÑAL (NUNCA aumenta el riesgo para alcanzar el mínimo)
    -> Coloca orden de entrada + orden de protección (stop-loss) de forma
       atómica: si el stop-loss no se puede colocar, se cancela/cierra la
       entrada inmediatamente. Nunca queda una posición sin protección.
    -> -> GESTIONANDO_POSICION

GESTIONANDO_POSICION
    -> Verifica condiciones de salida (TP, stop, breakeven, tiempo máximo)
    -> Verifica continuamente los límites de risk-policy.yaml
    -> Si se activa un límite: -> CIRCUIT_BREAKER
    -> Si se cierra la posición (TP o SL): registra resultado -> ESPERANDO_SEÑAL

CIRCUIT_BREAKER
    -> Cierra posiciones abiertas de forma segura (o las deja gestionarse
       solo por su stop-loss ya colocado, según se defina en risk-policy)
    -> Deja de evaluar nuevas señales
    -> Emite alerta con el motivo exacto
    -> Requiere reset manual explícito para volver a ESPERANDO_SEÑAL

DETENIDO
    -> Estado manual. Ninguna operación nueva. Usado para mantenimiento.
```

## 3. Componentes (mapeo a `src/`)

```
src/
├── data/
│   ├── fetch_historical.py     # klines + aggTrades históricos -> Parquet/DuckDB
│   ├── fetch_realtime.py       # WebSocket klines + trades en vivo
│   ├── orderbook_recorder.py   # Graba snapshots + updates del order book
│   │                            # (necesario ANTES de poder backtestear
│   │                            #  estrategias basadas en order book — ver
│   │                            #  DATA_CONTRACTS.md)
│   └── storage.py              # Interfaz DuckDB/Parquet
│
├── indicators/
│   ├── volume_profile.py
│   ├── delta.py                 # Aproximado con aggTrades (isBuyerMaker)
│   ├── order_book_features.py   # Solo utilizable una vez exista histórico grabado
│   └── atr.py
│
├── strategy/
│   ├── base_strategy.py         # Interfaz: generate_signal(), required_data()
│   ├── volume_breakout_mvp.py   # Primera estrategia (ver STRATEGY_SPEC.md)
│   └── registry.py
│
├── risk/
│   ├── risk_engine.py           # Punto único de paso obligatorio antes de
│   │                              # cualquier orden (ver AGENTS.md 1.3)
│   ├── position_sizing.py       # Usa exchangeInfo dinámico, nunca hardcodeado
│   └── circuit_breaker.py
│
├── execution/
│   ├── exchange_filters.py      # Consulta y cachea exchangeInfo
│   ├── paper_broker.py          # Simulación determinista (sin red)
│   ├── demo_broker.py           # Binance Demo Mode
│   ├── testnet_broker.py        # Binance Spot Testnet
│   ├── live_broker.py           # Binance real — requiere flag explícito
│   └── order_manager.py         # Coloca entrada + stop de forma atómica
│
├── backtest/
│   ├── engine.py                # vectorbt/backtrader wrapper
│   ├── walk_forward.py
│   └── report.py                # Métricas de VALIDATION_PROTOCOL.md
│
├── monitor/
│   ├── logger.py                 # JSON estructurado (ver DATA_CONTRACTS.md)
│   ├── alerts_telegram.py
│   └── weekly_report.py
│
└── main.py                       # Orquestador: máquina de estados de la sección 2
```

## 4. Reconexión y continuidad (WebSocket)

- Las conexiones WebSocket de Binance tienen duración máxima de 24 horas.
  El sistema debe reconectar de forma proactiva antes del corte, sin
  duplicar ni perder eventos (usar un `lastEventId`/timestamp de control y
  resincronizar el estado local contra un REST snapshot al reconectar).
- Ante cualquier desconexión inesperada, el bot NO asume que el mercado
  siguió igual: debe re-sincronizar antes de volver a `ESPERANDO_SEÑAL`.

## 5. Criterios de aceptación de esta fase de arquitectura

- [ ] Existe un único punto de entrada de órdenes (`risk_engine.py`) y se
      puede demostrar con un test que ninguna otra ruta del código llama al
      broker directamente.
- [ ] La máquina de estados está implementada literalmente (un enum o
      similar), no como lógica implícita dispersa en el código.
- [ ] `exchange_filters.py` consulta `exchangeInfo` en vivo y cachea con
      expiración — no hay valores de LOT_SIZE/MIN_NOTIONAL hardcodeados en
      ningún otro archivo.
