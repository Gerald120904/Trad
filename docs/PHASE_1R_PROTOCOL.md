# Fase 1R - Protocolo preregistrado de reformulación

Estado al 2026-07-25:

- Fase 0: PASS para el periodo auditado.
- `volume_breakout_mvp` v1: RECHAZADA y congelada en
  `phase1-rejected-v1`.
- Fases 2 y 3: BLOQUEADAS.

## Suficiencia obligatoria

Para velas de cinco minutos se requieren al menos 180 días completos
(preferidos: 365), sin huecos no explicados y nuevamente aprobados por Fase
0. El primer 70% será investigación/desarrollo y el último 30% será
confirmación final intacta. La confirmación no se usará para seleccionar
indicadores, parámetros, stops, objetivos, intervalos o símbolos.

Antes del backtest formal se medirá frecuencia. Una hipótesis sin eventos
potenciales suficientes para alcanzar razonablemente 100 operaciones OOS
será `NO_EVALUABLE_POR_FRECUENCIA`.

## Hipótesis congeladas

- **H1 - Breakout causal base:** cierre sobre resistencia previa, ATR válido,
  entrada en la apertura siguiente y posición válida con stop.
- **H2 - Breakout con volumen:** H1 y volumen relativo >= 1.50, calculado
  contra una referencia terminada en la vela anterior.
- **H3 - Breakout con delta:** H1 y `delta_ratio > 0`.
- **H4 - Breakout con volumen y delta:** H1, volumen relativo >= 1.50 y
  `delta_ratio > 0`.

## Rejilla congelada

- `level_lookback`: 20, 40, 80
- `volume_lookback`: 20, 40, 80 (ignorado por H1/H3)
- `atr_period`: 14
- `atr_stop_multiple`: 1.5, 2.0
- `reward_risk`: 1.5, 2.0
- `max_holding_bars`: 12, 24, 48
- `risk_per_trade`: 0.5%
- `max_position_fraction`: 25%
- `max_leverage`: 1

No se añadirán valores tras observar resultados OOS o de confirmación.

## Elegibilidad de entrenamiento

El optimizador solo puede seleccionar candidatos con retorno neto > 0,
profit factor > 1.00, stops en 100% de posiciones, cero violaciones de
riesgo, muestra mínima de entrenamiento y drawdown dentro del límite. Si
ninguno es elegible, la ventana será `NO_MODEL` y ejecutará cero operaciones
OOS. Está prohibido seleccionar automáticamente la alternativa menos mala.

## Diseño y resultados permitidos

Cada hipótesis usa cinco ventanas walk-forward, entrenamiento anterior,
parámetros congelados OOS, capital continuo y OOS sin solapamiento. Debe
reportar el embudo completo desde velas hasta cierres, incluyendo rechazos
por ATR, stop, tamaño, capital y posición existente.

Resultados permitidos: `APROBADA`, `RECHAZADA`, `NO_MODEL` o
`NO_EVALUABLE_POR_FRECUENCIA`. Solo `APROBADA` permite considerar Fase 2.
Los criterios de aceptación de `docs/VALIDATION_PROTOCOL.md` permanecen sin
cambios.
