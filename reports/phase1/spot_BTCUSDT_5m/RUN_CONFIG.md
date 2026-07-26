# Configuración congelada - rechazo Fase 1 v1

Ejecutado el 2026-07-25 sobre la Compuerta 0 aprobada:

```powershell
python -m phase1.run `
  --market spot `
  --symbol BTCUSDT `
  --start-date 2026-07-18 `
  --end-date 2026-07-24 `
  --bar-interval 5m `
  --starting-capital 1000 `
  --fee-rate 0.001 `
  --slippage-bps 2 `
  --risk-per-trade 0.005 `
  --max-position-fraction 0.25 `
  --max-leverage 1
```

El código de la ejecución corresponde al paquete local
`binance_trading_gates_0_1`. Resultado automático: `REJECTED`.
