# Fase 1R - Diagnóstico de la hipótesis rechazada

Fecha: 2026-07-25
Referencia congelada: tag `phase1-rejected-v1`

## Resultado preservado

La estrategia `volume_breakout_mvp` v1 permanece **RECHAZADA**. Este
diagnóstico no modifica parámetros, criterios de aceptación ni resultados.

## Integridad técnica

Sobre 2,016 velas BTCUSDT Spot de 5 minutos:

- Velas duplicadas: 0
- Velas fuera de orden: 0
- Velas sintéticas por huecos: 0
- Filas OHLC inválidas: 0
- Filas donde volumen comprador + vendedor difiere del volumen total: 0

La convención de delta fue verificada: `is_buyer_maker=false` se agrega como
volumen taker comprador y `is_buyer_maker=true` como volumen taker vendedor.
La causalidad permanece intacta: niveles y referencia de volumen terminan en
la vela anterior; la entrada ocurre en la apertura siguiente.

## Embudo OOS por ventana

| Ventana | Velas | Listas tras warm-up | Rupturas | Pasa volumen | Pasa delta | Ejecutadas |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 201 | 201 | 10 | 3 | 1 | 1 |
| 2 | 201 | 201 | 2 | 0 | 0 | 0 |
| 3 | 201 | 201 | 7 | 1 | 1 | 1 |
| 4 | 201 | 201 | 10 | 1 | 1 | 1 |
| 5 | 204 | 204 | 10 | 2 | 1 | 1 |
| **Total** | **1,008** | **1,008** | **39** | **7** | **4** | **4** |

Parámetros seleccionados por entrenamiento:

- Ventanas 1-3: nivel 40, volumen 40, volumen relativo 2.0, delta 0.10.
- Ventanas 4-5: nivel 20, volumen 40, volumen relativo 2.0, delta 0.10.

## Conclusión

No hay evidencia de un fallo de datos, causalidad, warm-up o motor de riesgo.
El filtro dominante es volumen relativo: conserva 7 de 39 rupturas (17.9%).
El delta conserva 4 de esas 7 (57.1%). Todas las señales finales se
ejecutaron, por lo que tamaño y capital no explican la escasez observada.

Esto no autoriza a reducir umbrales. Los resultados de entrenamiento también
fueron negativos en las cinco ventanas seleccionadas (profit factor entre
0.21 y 0.26 aproximadamente). La siguiente variante debe especificarse antes
de evaluarse y usar un periodo de investigación separado.

Fases 2 y 3 permanecen bloqueadas.
