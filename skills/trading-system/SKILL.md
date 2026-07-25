---
name: trading-system
description: "Usar este skill al trabajar en cualquier parte de este repositorio de trading algorítmico (estrategia, riesgo, backtesting, ejecución en Binance Spot). Contiene vocabulario de dominio, referencias de exchange y recordatorios de las reglas no negociables del proyecto. Consultar antes de implementar indicadores de volumen/order flow, lógica de riesgo, o integraciones con la API de Binance."
---

# Skill: trading-system (dominio de trading algorítmico de este proyecto)

## Cuándo usar este skill

Al implementar cualquier archivo en `src/data/`, `src/indicators/`,
`src/strategy/`, `src/risk/`, `src/execution/`, `src/backtest/` de este
repositorio.

## Recordatorios rápidos (el detalle completo vive en `docs/`)

- Este proyecto es **Binance Spot únicamente**, long-only.
- El order book vía REST es una foto del momento, no historial — ver
  `docs/DATA_CONTRACTS.md` antes de asumir que se puede backtestear con
  order book sin haberlo grabado antes.
- Los filtros de exchange (`LOT_SIZE`, `MIN_NOTIONAL`, etc.) se consultan
  dinámicamente vía `exchangeInfo`, nunca hardcodeados — ver
  `references/binance_filters.md`.
- Ninguna orden se coloca sin pasar por `risk/risk_engine.py`.
- Las reglas de estrategia activas son las de `docs/STRATEGY_SPEC.md`
  — no inventar variantes sin documentarlas ahí primero.
- Testnet ≠ Demo Mode: Testnet tiene precios independientes del mercado
  real; Demo Mode tiene datos similares al mercado real con los mismos
  filtros — ver `references/binance_environments.md`.

## Referencias

- `references/binance_filters.md` — resumen de los filtros de symbol
  relevantes (LOT_SIZE, MIN_NOTIONAL, etc.) y cómo consultarlos.
- `references/binance_environments.md` — diferencias entre Testnet, Demo
  Mode y producción.
- `references/glossary.md` — vocabulario del dominio (volumen, volume
  profile, delta, order flow, drawdown, profit factor, walk-forward, etc.)
  usado consistentemente en todo el repositorio.
