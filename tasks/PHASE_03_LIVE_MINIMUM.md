# PHASE_03_LIVE_MINIMUM.md — Capital real mínimo

## Precondición (verificar antes de tocar una sola línea de esta fase)

`docs/LIVE_PROMOTION_CHECKLIST.md` debe estar 100% marcado como completo
por el usuario, con fecha. Si Codex detecta que este archivo no está
completo, debe detenerse y decírselo al usuario explícitamente, sin asumir
que "probablemente ya está listo".

## Tareas

1. Implementar `src/execution/live_broker.py` usando `BINANCE_LIVE_API_KEY`.
   - Verificar programáticamente, al iniciar, que la API key NO tiene
     permiso de retiro (si la API de Binance lo expone; si no, dejarlo
     como recordatorio manual explícito en el log de arranque).
2. El cambio de `TRADING_MODE` a `live` en `.env`/`settings.yaml` debe
   requerir, además del valor en el archivo, un argumento explícito al
   arrancar el proceso (ej. `python -m src.main --confirm-live`), de forma
   que no baste con un error de tipeo en un archivo de configuración para
   activar dinero real.
3. Definir el capital real en `config/risk-policy.yaml` a mano (el usuario
   edita `capital.total_asignado_usd`, no el bot).
4. Arrancar en real con el capital mínimo definido y supervisar activamente
   los primeros días (no dejarlo desatendido de inmediato).
5. Mantener las mismas reglas exactas que se validaron en Demo Mode. Ningún
   ajuste de "última hora" a la estrategia durante el periodo mínimo de
   evaluación en real.

## Checklist de salida de esta fase (hacia escalar capital)

- Usar el checklist de `LIVE_PROMOTION_CHECKLIST.md`, sección
  "Capital real mínimo → Escalar capital".
