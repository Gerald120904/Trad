# PHASE_01_BACKTEST.md — Backtest de la estrategia MVP

## Objetivo

Implementar `volume_breakout_mvp` (ver `STRATEGY_SPEC.md`) y validarla
completamente con `VALIDATION_PROTOCOL.md`, sin tocar todavía ningún broker
en vivo (ni siquiera testnet).

## Tareas

1. Implementar los indicadores necesarios en `src/indicators/`:
   `volume_profile.py`, `delta.py` (basado en aggTrades/klines), `atr.py`.
   - Todos deben poder calcularse usando SOLO datos hasta la vela actual
     (sin look-ahead). Escribir un test específico que verifique esto
     (ej. cambiar una vela futura y confirmar que el indicador en el
     presente no cambia).
2. Implementar `src/strategy/volume_breakout_mvp.py` siguiendo exactamente
   las reglas de `STRATEGY_SPEC.md`.
3. Implementar `src/risk/position_sizing.py` y `src/risk/risk_engine.py`,
   integrando `exchange_filters.py` de la Fase 0 y `config/risk-policy.yaml`.
4. Implementar `src/backtest/engine.py` (vectorbt o backtrader, a elección
   de Codex, documentando la elección y el porqué).
5. Implementar `src/backtest/walk_forward.py` con al menos 4-5 ventanas.
6. Implementar `src/backtest/report.py` generando TODAS las métricas de
   `VALIDATION_PROTOCOL.md` sección 2, en un reporte legible (markdown o
   HTML simple) guardado en `reports/`.
7. Correr el backtest completo y generar el reporte.

## Checklist de salida de esta fase

- [ ] Reporte de backtest generado con todas las métricas obligatorias
- [ ] Walk-forward validation documentado, ventana por ventana
- [ ] Prueba de sensibilidad a slippage (x1 y x2) incluida en el reporte
- [ ] Resultado evaluado explícitamente contra los criterios de rechazo de
      `VALIDATION_PROTOCOL.md` sección 5 (decir claramente si la estrategia
      pasa o no, y por qué)
- [ ] Si la estrategia NO pasa: documentar qué se probó y detenerse aquí a
      esperar instrucciones del usuario (ajustar parámetros, probar otra
      hipótesis, o cerrar el proyecto) — Codex no debe seguir a la Fase 2
      con una estrategia que no pasó la validación
- [ ] Ningún código de esta fase coloca órdenes reales, de demo o de testnet
