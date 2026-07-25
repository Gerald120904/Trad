# Filtros de symbol relevantes en Binance Spot

Consultar siempre vía `GET /api/v3/exchangeInfo?symbol=BTCUSDT` (o el
símbolo activo), nunca hardcodear los valores.

- **PRICE_FILTER**: define `minPrice`, `maxPrice`, `tickSize` — el precio de
  cualquier orden debe ser múltiplo de `tickSize`.
- **LOT_SIZE**: define `minQty`, `maxQty`, `stepSize` — la cantidad debe ser
  múltiplo de `stepSize`.
- **MARKET_LOT_SIZE**: igual que LOT_SIZE pero específico para órdenes de
  mercado.
- **MIN_NOTIONAL** / **NOTIONAL**: valor mínimo (precio × cantidad) que debe
  tener la orden para ser aceptada.
- **MAX_NUM_ORDERS**: número máximo de órdenes abiertas simultáneas
  permitidas para el símbolo.
- **MAX_NUM_ALGO_ORDERS**: máximo de órdenes tipo algo (ej. stop-loss,
  take-profit) simultáneas.

Regla del proyecto: si el tamaño de posición calculado por riesgo es menor
al mínimo permitido por estos filtros, la operación se **rechaza**. Nunca
se aumenta el riesgo para alcanzar el mínimo (ver `docs/RISK_POLICY.md`).
