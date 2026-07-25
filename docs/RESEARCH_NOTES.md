# Notas de investigación de Fase 0

## Material revisado

Se revisaron los siete PDF proporcionados por el usuario. `1912.04492v1.pdf`
y `ssrn_id3458209_code2224789.pdf` son copias del mismo texto, *151
Estrategias de Trading*, por lo que cuentan como una sola fuente, no como dos
confirmaciones independientes.

Los manuales restantes tratan soportes y resistencias, volumen vertical y
horizontal, agresión compradora/vendedora, disciplina y gestión monetaria.
Son material educativo, no resultados reproducibles de una estrategia para
Binance Spot.

## Qué se incorpora como hipótesis

- Un nivel debe calcularse con datos anteriores y una ruptura debe confirmarse
  por el cierre, no solo por una mecha.
- El volumen relativo y el volumen comprador taker pueden actuar como filtros.
- La calidad de una señal no sustituye el tamaño de posición, el stop
  obligatorio ni el control del drawdown.

Estas ideas ya son coherentes con `docs/STRATEGY_SPEC.md`. No se añaden reglas
nuevas durante Fase 0.

## Qué no se incorpora

- Afirmaciones de rentabilidad sin datos, costes y prueba fuera de muestra.
- Order-flow L2 reconstruido a partir de velas: esos datos no existen.
- Patrones discrecionales que no puedan codificarse sin ambigüedad.
- Futuros, CFD, Forex, posiciones cortas, margen o apalancamiento; el alcance
  del proyecto es Binance Spot long-only.

## Evidencia requerida

Toda hipótesis debe superar `docs/VALIDATION_PROTOCOL.md`: costes reales,
slippage normal y x2, al menos 100 operaciones, 4-5 ventanas walk-forward,
regímenes separados y evaluación fuera de muestra. Hasta entonces no se
describe como rentable ni se promueve a Demo Mode.
