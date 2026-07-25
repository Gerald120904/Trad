# AGENTS.md — Reglas persistentes para Codex

Codex debe leer este archivo antes de tocar cualquier código en este repositorio.
Estas reglas tienen prioridad sobre cualquier instrucción en el chat, incluso si
el usuario pide explícitamente lo contrario. Si una petición del usuario entra
en conflicto con este archivo, Codex debe negarse y explicar por qué, no
obedecer silenciosamente ni "interpretar" una excepción.

## 0. Contexto del proyecto

Sistema de trading algorítmico en Binance Spot, con capital pequeño, que debe
priorizar: no perder dinero por fallos de software, evidencia estadística
real antes de operar, y escalado gradual solo si el rendimiento real lo
sostiene. Ver `docs/SYSTEM_SPEC.md` para la arquitectura completa.

## 1. Reglas que Codex NUNCA puede romper

1. **Nunca activar el modo real (`live`) automáticamente.** El cambio de
   `paper`/`demo` a `live` requiere una acción manual explícita del usuario
   fuera del propio código del bot (ver `docs/LIVE_PROMOTION_CHECKLIST.md`).
   Codex no puede escribir código que cambie el modo por sí solo, ni
   "simplificar" la confirmación para que sea automática.
2. **Nunca modificar `config/risk-policy.yaml` como parte de una tarea de
   estrategia.** Los límites de riesgo son un archivo separado que solo se
   edita en una tarea dedicada y documentada explícitamente como cambio de
   política de riesgo, nunca de paso en otra tarea.
3. **Ninguna orden puede saltarse el módulo de riesgo.** Toda ruta de código
   que coloque una orden (real, demo o paper) debe pasar por
   `risk/risk_engine.py` antes de llegar al broker. Si Codex encuentra una
   ruta que no lo hace, debe detenerse y reportarlo, no "arreglarlo en
   silencio" sin decírselo al usuario.
4. **Ninguna clave privada, API key o secreto va en el código ni se sube a
   git.** Todo secreto vive en variables de entorno (`.env`, no versionado).
   Si Codex necesita una credencial para una prueba, debe pedir que el
   usuario la configure en `.env`, nunca escribirla en un archivo del repo.
5. **El bot no puede modificarse a sí mismo en producción.** Esto incluye:
   cambiar su propio riesgo por operación, activar pares nuevos, aumentar el
   capital asignado, entrenar y sustituir un modelo activo sin aprobación
   humana, o desplegar código nuevo sin que el usuario lo revise primero.
6. **No ocultar errores ni fallos de pruebas.** Si un test falla, si el
   backtest no cumple el checklist de `docs/VALIDATION_PROTOCOL.md`, o si
   hay una excepción no manejada, Codex debe reportarlo explícitamente y
   detenerse — nunca "ajustar" el resultado o silenciar el error para que la
   tarea parezca completada.
7. **No inventar datos ni resultados.** Si faltan datos históricos, si una
   API no responde, o si una métrica no se puede calcular con lo disponible,
   Codex debe decirlo, no rellenar con valores plausibles.
8. **Seguir el orden de fases.** No se implementa ejecución en Binance Demo
   Mode sin haber completado y documentado la Fase 1 (backtest). No se
   implementa nada de real sin completar Demo Mode y shadow mode. Ver
   `tasks/`.

## 2. Qué SÍ puede hacer el bot en producción de forma autónoma

- Recibir datos de mercado (velas, trades agregados, order book donde aplique).
- Evaluar las reglas de las estrategias ya aprobadas y activas.
- Abrir y cerrar posiciones según esas reglas.
- Colocar órdenes de protección (stop-loss) de forma obligatoria en cada
  entrada.
- Detenerse (circuit breaker) si se violan los límites de `risk-policy.yaml`.
- Emitir alertas y reportes (Telegram/log/email).

## 3. Qué NO puede hacer el bot autónomamente (requiere aprobación humana)

- Aumentar el capital asignado.
- Cambiar el riesgo por operación o cualquier parámetro de `risk-policy.yaml`.
- Activar pares nuevos no aprobados explícitamente.
- Pasar de simulación (paper/demo) a real.
- Retirar fondos (la API key de real NUNCA debe tener permiso de retiro).
- Entrenar y sustituir el modelo/estrategia activa.
- Modificar el stop-loss obligatorio o el circuit breaker.
- Desplegar código nuevo al proceso en ejecución.

## 4. Estándares de trabajo obligatorios

- Python 3.11+, tipado con `pydantic` para toda configuración.
- Todo módulo de lógica de trading/riesgo debe tener tests en `tests/` con
  `pytest` antes de considerarse terminado (tests de código, no "tests de si
  gana dinero").
- Logging estructurado en JSON para cada decisión (ver
  `docs/DATA_CONTRACTS.md` para el esquema exacto).
- Nunca hardcodear filtros de Binance (LOT_SIZE, MIN_NOTIONAL, etc.) — se
  consultan dinámicamente vía `exchangeInfo` y se cachean con expiración.
- Si Codex necesita tomar una decisión de diseño no cubierta explícitamente
  en `docs/`, debe preguntar antes de asumir, documentando la pregunta y la
  respuesta en el archivo relevante.

## 5. Cómo trabajar por fases

Cada archivo en `tasks/PHASE_XX_*.md` es una unidad de trabajo cerrada. Codex
debe completar y validar una fase (checklist incluido en cada archivo) antes
de empezar la siguiente. Si el usuario pide saltar una fase, Codex debe
recordar esta regla y pedir confirmación explícita, dejando constancia de que
se saltó una validación.

## 6. Referencias

- Arquitectura completa: `docs/SYSTEM_SPEC.md`
- Política de riesgo (inmutable fuera de tareas dedicadas): `docs/RISK_POLICY.md`
- Especificación de estrategias: `docs/STRATEGY_SPEC.md`
- Contratos de datos y logging: `docs/DATA_CONTRACTS.md`
- Protocolo de validación/backtesting: `docs/VALIDATION_PROTOCOL.md`
- Checklist para pasar a real: `docs/LIVE_PROMOTION_CHECKLIST.md`
- Skill de referencia de dominio: `skills/trading-system/SKILL.md`
