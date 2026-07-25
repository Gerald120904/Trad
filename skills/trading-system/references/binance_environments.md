# Entornos de Binance usados en este proyecto

| Entorno | Precios/libro | Fondos | Uso en este proyecto |
|---|---|---|---|
| Spot Testnet | Independientes del mercado real | Virtuales | Fase 2: validar integración técnica con la API (auth, envío de órdenes, manejo de errores) |
| Spot Demo Mode | Similares al mercado real, mismos filtros que producción | Virtuales | Fase 2: validar comportamiento realista antes de arriesgar capital real |
| Producción (real) | Reales | Reales | Fase 3, solo tras aprobar `docs/LIVE_PROMOTION_CHECKLIST.md` |

Advertencia oficial de Binance sobre Demo Mode: datos realistas no equivalen
a resultados reales garantizados. No asumir que una estrategia que funciona
en Demo Mode funcionará igual en producción — solo reduce el riesgo de
sorpresas técnicas (redondeos, mínimos, comportamiento de órdenes).
