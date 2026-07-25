# LIVE_PROMOTION_CHECKLIST.md — Checklist para pasar a capital real

Este checklist se completa a mano por el usuario. Codex puede ayudar a
verificar cada punto técnicamente, pero **no puede marcar este checklist
como aprobado ni cambiar el modo a `live` por sí mismo** (ver `AGENTS.md`).

## Backtest → Paper/Testnet

- [ ] Mínimo 100 operaciones en el backtest histórico
- [ ] Walk-forward validation completo (mínimo 4-5 ventanas), documentado
- [ ] Probado en al menos 2 regímenes de mercado distintos
- [ ] Comisiones y slippage estimado incluidos, con prueba de sensibilidad
      "slippage x2"
- [ ] Estrategia rechazada según criterios de `VALIDATION_PROTOCOL.md`
      sección 5 → NO cumple ninguno de los criterios de rechazo

## Testnet/Paper → Binance Demo Mode

- [ ] Corrida en paper broker determinista sin errores técnicos durante al
      menos 2 semanas
- [ ] Reconciliación funcionando y probada (forzar una discrepancia
      simulada y confirmar que se detecta y alerta)

## Demo Mode → Shadow Mode

- [ ] Mínimo 4-6 semanas corriendo en Binance Demo Mode
- [ ] Resultados en Demo Mode razonablemente consistentes con el backtest
      (si difieren mucho, investigar por qué antes de continuar)
- [ ] Circuit breaker probado explícitamente (forzar una racha de pérdidas
      simulada y confirmar que el bot se detiene solo y alerta)
- [ ] Alertas (Telegram/email) funcionando y probadas con un evento real
- [ ] Ninguna posición quedó sin stop-loss detectable en el exchange en
      ningún momento de la corrida

## Shadow Mode → Capital real mínimo

- [ ] Mínimo 2-4 semanas en shadow mode (evaluando señales en tiempo real
      sin colocar ninguna orden, ni en demo)
- [ ] Las señales de shadow mode coinciden con lo que se esperaría según
      backtest + Demo Mode
- [ ] API key de real creada SIN permiso de retiro (withdrawal deshabilitado)
- [ ] API key de real restringida por IP (si corre en VPS con IP fija)
- [ ] `config/risk-policy.yaml` revisado a mano, capital real definido
      explícitamente (no dejar en $0 esperando que el bot lo detecte)
- [ ] Confirmado: el cambio de modo a `live` requiere un paso manual fuera
      del propio bot (no un simple flag en `settings.yaml` editado por error)

## Capital real mínimo → Escalar capital

- [ ] Mínimo 4-8 semanas operando en real con el capital mínimo
- [ ] Ningún cambio de reglas de estrategia "de último momento" durante ese
      periodo
- [ ] Drawdown real dentro de lo esperado por el backtest (si el drawdown
      real es notablemente peor, NO escalar — volver a revisar la estrategia)
- [ ] Decisión de escalar tomada explícitamente por el usuario, documentada
      con fecha y monto nuevo en `risk-policy.yaml`
