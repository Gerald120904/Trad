# STRATEGY_SPEC.md — Especificación de estrategias

## Nota de atribución (importante)

Las reglas descritas abajo son **hipótesis propias de este proyecto**,
inspiradas en conceptos generales de análisis de volumen y flujo de órdenes
(volumen, volume profile, delta, libro de órdenes) presentes en la
literatura de trading. **No son estrategias copiadas ni validadas
académicamente de ningún documento específico.** Deben tratarse como
hipótesis a probar, no como hechos. El paper "151 Estrategias de Trading"
(Kakushadze & Serur) es una referencia de dominio general y de vocabulario,
no la fuente literal de estas reglas.

## Estrategia MVP: `volume_breakout_mvp`

**Objetivo:** tener una referencia mecánica, simple y verificable antes de
considerar cualquier estrategia más compleja o con machine learning.

### Datos permitidos (y solo estos)

- Velas OHLCV (open, high, low, close, volumen) del par y temporalidad activa.
- Número de operaciones por vela (`number_of_trades`).
- Volumen comprador taker aproximado (`taker_buy_base_asset_volume` de
  klines, o agregación de `aggTrades` con `isBuyerMaker`).
- ATR (Average True Range), calculado únicamente para normalizar volatilidad
  al definir el stop, no como señal de entrada.
- Niveles de soporte/resistencia calculados usando SOLO datos anteriores a
  la vela evaluada (prohibido usar datos futuros, incluso sin querer, al
  vectorizar el backtest).

### Reglas de entrada (todas deben cumplirse)

1. Identificar un nivel de precio confirmado (máximo o mínimo local
   significativo) usando únicamente velas anteriores a la actual.
2. Exigir que el cierre de la vela actual quede claramente fuera de ese
   nivel (no una mecha, un cierre).
3. Exigir que el volumen de esa vela sea mayor a
   `umbral_volumen_relativo × volumen_promedio_de_N_velas` (parámetro en
   `settings.yaml`).
4. Exigir que el volumen comprador taker domine sobre el vendedor de forma
   coherente con la dirección de la ruptura (para una ruptura alcista,
   debe dominar el volumen comprador).
5. Calcular el stop-loss ANTES de enviar la orden de entrada, usando
   ATR × `atr_multiplo_stop`.
6. Calcular el take-profit target en el siguiente nivel relevante de
   volumen/precio.
7. Rechazar la entrada si la relación beneficio/riesgo resultante es menor
   a `relacion_beneficio_riesgo_minima`.
8. Calcular el tamaño de posición según el % de riesgo definido en
   `risk-policy.yaml`, descontando comisión y slippage estimado, y
   ajustando a los filtros reales del exchange (`LOT_SIZE`, `MIN_NOTIONAL`,
   etc.) consultados dinámicamente.
9. Si el tamaño resultante es menor al mínimo operable del exchange:
   **rechazar la operación**, nunca aumentar el riesgo para alcanzar el
   mínimo.
10. Registrar la decisión completa (ver `DATA_CONTRACTS.md`) incluso si la
    operación fue rechazada en cualquiera de los pasos anteriores.

### Reglas de gestión de la posición abierta

- Mover el stop a breakeven una vez alcanzado
  `breakeven_trigger_pct` de recorrido a favor (parámetro configurable).
- El stop solo puede moverse a favor (reducir riesgo), nunca en contra.
- Ninguna gestión discrecional: toda regla de gestión debe estar en código,
  no aplicarse manualmente "porque se ve bien".

## Fuera de alcance en esta versión (explícitamente prohibido hasta nueva orden)

- Estrategias basadas en libro de órdenes (absorción, desequilibrio L2):
  requieren grabación histórica propia primero (ver `DATA_CONTRACTS.md`,
  sección de order book). No se puede backtestear esto con velas solamente.
- Cualquier modelo de machine learning (redes neuronales, clasificadores,
  etc.): solo se considera después de que `volume_breakout_mvp` tenga un
  backtest y validación fuera de muestra aprobados, para tener una base de
  comparación honesta.
- Retrocesos de Fibonacci, ondas de Elliott, u otro análisis técnico basado
  en patrones geométricos sin relación con oferta/demanda real —
  explícitamente excluido de este proyecto.

## Cómo agregar una estrategia nueva (proceso obligatorio)

1. Documentarla en este archivo ANTES de escribir código (regla de entrada,
   regla de salida, datos que usa, parámetros).
2. Implementarla en `src/strategy/` heredando de `base_strategy.py`.
3. Backtestear siguiendo `VALIDATION_PROTOCOL.md` completo.
4. Solo si aprueba el checklist, se activa en `settings.yaml` con
   `habilitada: true` — y esto lo hace el usuario, no Codex por su cuenta.
