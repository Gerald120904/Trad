# Reporte de Compuerta 1 — Estrategia y backtest

## Decisión: **RECHAZADA**

- Mercado: `spot`
- Símbolo: `BTCUSDT`
- Periodo: `2026-07-18` a `2026-07-24`
- Intervalo: `5m`
- Velas: `2016`
- Velas sin operaciones completadas causalmente: `0`

## Resultado fuera de muestra

- Operaciones: **4**
- Retorno neto: **-0.40%**
- Profit factor: **0.000**
- Drawdown máximo: **0.40%**
- Win rate: **0.00%**

## Estrés con slippage duplicado

- Retorno neto: **-0.42%**
- Profit factor: **0.000**
- Drawdown máximo: **0.42%**

## Criterios

| Criterio | Estado | Observado | Requerido |
|---|---:|---:|---:|
| `complete_market_cost_model` | **PASS** | `spot` | `spot; futures requiere funding/liquidación/contrato` |
| `five_walk_forward_windows` | **PASS** | `5` | `5` |
| `minimum_oos_trades` | **FAIL** | `4` | `>= 100` |
| `positive_oos_return` | **FAIL** | `-0.003980409806108696` | `> 0` |
| `oos_profit_factor` | **FAIL** | `0.0` | `>= 1.15` |
| `maximum_drawdown` | **PASS** | `0.003998899239933906` | `<= 0.2` |
| `positive_windows` | **FAIL** | `0` | `>= 3` |
| `profit_concentration` | **FAIL** | `1.0` | `<= 0.6` |
| `double_slippage_positive` | **FAIL** | `-0.0041788858550504526` | `> 0` |
| `double_slippage_profit_factor` | **FAIL** | `0.0` | `>= 1.0` |
| `mandatory_stops` | **PASS** | `1.0` | `1.0` |
| `risk_engine_violations` | **PASS** | `0` | `0` |
| `no_catastrophic_regime` | **PASS** | `0` | `0` |

## Resultados por régimen

| Régimen | Trades | PnL neto | Win rate | PF |
|---|---:|---:|---:|---:|
| `bear_low_vol` | 1 | -0.99 | 0.00% | 0.000 |
| `bull_high_vol` | 2 | -2.09 | 0.00% | 0.000 |
| `sideways_low_vol` | 1 | -0.90 | 0.00% | 0.000 |

## Conclusión

La estrategia queda rechazada. El proyecto debe detenerse aquí, ajustar la hipótesis y repetir toda la Compuerta 1. No puede avanzar a paper broker, Demo ni ejecución real.
