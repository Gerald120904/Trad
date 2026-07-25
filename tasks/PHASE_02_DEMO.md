# PHASE_02_DEMO.md — Paper broker, Testnet y Binance Demo Mode

## Precondición

Esta fase solo empieza si `PHASE_01_BACKTEST.md` fue aprobada según su
checklist. Si no lo fue, no continuar.

## Tareas

1. Implementar `src/execution/paper_broker.py`: simulación determinista
   (misma lógica de la estrategia, datos en vivo, ejecución simulada sin
   red real, para probar el bucle completo "dato -> señal -> riesgo -> orden
   -> gestión" sin ningún riesgo).
2. Implementar `src/execution/testnet_broker.py` usando
   `BINANCE_TESTNET_API_KEY`. Usar esto para validar la integración técnica
   con la API real de Binance (autenticación, envío de órdenes, manejo de
   errores de la API) — recordando que los precios de Testnet son
   independientes del mercado real.
3. Implementar `src/execution/demo_broker.py` usando
   `BINANCE_DEMO_API_KEY` (Binance Demo Mode) para evaluar comportamiento
   con datos de mercado realistas y los mismos filtros que producción.
4. Implementar `src/monitor/logger.py` con el esquema exacto de
   `DATA_CONTRACTS.md`, y `src/monitor/alerts_telegram.py`.
5. Implementar la reconciliación periódica (`DATA_CONTRACTS.md` sección 3).
6. Implementar el circuit breaker (`src/risk/circuit_breaker.py`) y
   escribir un test que fuerce una racha de pérdidas simulada y confirme
   que el bot se detiene y alerta correctamente.
7. Implementar "shadow mode": el bot evalúa señales en tiempo real contra
   datos de Demo Mode pero NO coloca ninguna orden, solo registra qué
   habría hecho — para comparar contra el comportamiento real antes de
   arriesgar ni siquiera fondos virtuales.
8. Correr el sistema completo en Demo Mode durante el periodo mínimo
   definido en `LIVE_PROMOTION_CHECKLIST.md`.

## Checklist de salida de esta fase

- Usar exactamente el checklist de `LIVE_PROMOTION_CHECKLIST.md`, secciones
  "Testnet/Paper → Binance Demo Mode" y "Demo Mode → Shadow Mode".
- [ ] Ninguna línea de código de esta fase activa `BINANCE_LIVE_API_KEY`
      ni el modo `live`.
