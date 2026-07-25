# trading-system

Sistema de trading algorítmico para Binance Spot, con capital pequeño,
construido con Codex CLI siguiendo un desarrollo por fases estrictas.

## Filosofía

No prometemos predecir el mercado. Prometemos:
- Que ninguna orden se ejecute sin pasar por el módulo de riesgo.
- Que el modo real nunca se active por accidente.
- Que toda estrategia tenga evidencia estadística (fuera de muestra) antes
  de arriesgar capital real.
- Que las pérdidas estén limitadas y controladas por diseño, no por suerte.

## Requisitos (Windows local)

- Python 3.11+ (https://www.python.org/downloads/windows/)
- Git para Windows
- Codex CLI instalado y autenticado
- Cuenta de Binance (para Testnet, Demo Mode y, más adelante, real)

## Setup inicial

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env
```

Editar `.env` con tus credenciales de Testnet/Demo (nunca las de real todavía).

## Orden de trabajo

Seguir estrictamente `tasks/PHASE_00_RESEARCH.md`, luego
`PHASE_01_BACKTEST.md`, `PHASE_02_DEMO.md`, y solo al final
`PHASE_03_LIVE_MINIMUM.md`. Ver `AGENTS.md` para las reglas que Codex debe
respetar en todo momento.

## Estado actual del proyecto

- [ ] Fase 0 — Investigación y contratos de datos
- [ ] Fase 1 — Backtest
- [ ] Fase 2 — Binance Demo Mode / shadow mode
- [ ] Fase 3 — Capital real mínimo

Actualizar este checklist a medida que se completan fases (con fecha y
resultado del checklist de validación correspondiente).
