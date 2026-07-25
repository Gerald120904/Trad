# VALIDATION_PROTOCOL.md — Protocolo de backtesting y validación

## 1. Principio general

No se acepta una estrategia solo por tener un win rate alto. Se evalúa el
conjunto completo de métricas de esta sección, y se exige consistencia
entre ventanas de tiempo distintas (walk-forward), no solo un buen resultado
en un periodo específico.

## 2. Métricas obligatorias en cada reporte de backtest

- Rentabilidad neta después de costos (comisiones + slippage estimado)
- Profit factor
- Expectativa por operación (expected value)
- Máximo drawdown (%)
- Duración del máximo drawdown (en operaciones y en tiempo)
- Ratio beneficio/riesgo realizado (no el teórico de la regla, el que
  realmente se obtuvo)
- Número total de operaciones (mínimo 100 para considerar la muestra
  relevante — con menos, el resultado se reporta pero se marca como "no
  concluyente")
- Exposición temporal (% del tiempo con posición abierta)
- Racha máxima de pérdidas consecutivas
- Resultado desglosado por régimen de mercado (al menos: tendencia alcista,
  tendencia bajista, rango/lateral)
- Sensibilidad del resultado a comisiones y slippage (¿qué pasa si el
  slippage real es el doble de lo estimado?)
- Estabilidad entre ventanas walk-forward (¿el resultado es parecido en
  cada ventana, o depende de una sola ventana "con suerte"?)
- Diferencia entre resultado in-sample (entrenamiento/ajuste) y out-of-sample
  (fuera de muestra)

## 3. Walk-forward validation (obligatorio, no opcional)

- Dividir el histórico en al menos 4-5 ventanas consecutivas.
- Ajustar parámetros (si los hay) solo con la ventana de entrenamiento.
- Evaluar SIEMPRE en la ventana siguiente, nunca en la misma con la que se
  ajustó.
- Reportar el resultado de cada ventana por separado, no solo el promedio.

## 4. Simulación de costos reales

- Comisión: usar la comisión real de Binance Spot para el nivel de cuenta
  del usuario (consultar, no asumir 0%).
- Slippage: estimar de forma conservadora (ej. 1-2 ticks o un % fijo
  configurable) y correr también un escenario "slippage x2" como prueba de
  sensibilidad.

## 5. Criterios para RECHAZAR una estrategia (cualquiera de estos basta)

- Menos de 100 operaciones en el histórico disponible.
- Profit factor <= 1 después de costos.
- El resultado depende de una sola ventana walk-forward (las demás son
  planas o negativas).
- El resultado colapsa con "slippage x2".
- El drawdown máximo supera un umbral definido como aceptable por el
  usuario antes de empezar (documentar ese umbral en la tarea correspondiente).

## 6. Del backtest a Demo Mode (secuencia obligatoria)

```
Backtest histórico (este documento)
        ↓  (debe aprobar todos los criterios de la sección 5, en sentido inverso)
Paper broker determinista (misma lógica, datos en vivo, sin red real)
        ↓
Binance Demo Mode (datos similares al mercado real, mismos filtros de exchange)
        ↓
Shadow mode (evalúa señales en tiempo real pero NO coloca órdenes, ni
             siquiera en demo — solo registra qué habría hecho)
        ↓
Capital real mínimo (ver LIVE_PROMOTION_CHECKLIST.md)
```

Nota sobre Demo Mode: Binance advierte explícitamente que datos realistas
no equivalen a resultados reales garantizados. Demo Mode reduce el riesgo
de sorpresas por redondeos, tamaños mínimos y comportamiento de órdenes,
pero no reemplaza la validación estadística del backtest.
