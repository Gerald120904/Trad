# RISK_POLICY.md — Política de riesgo (explicación de `config/risk-policy.yaml`)

Este documento explica el "por qué" de cada regla en
`config/risk-policy.yaml`. El archivo YAML es la fuente de verdad que lee el
código; este Markdown es la justificación para humanos (y para Codex, para
que entienda por qué no debe tocarlo fuera de una tarea dedicada).

## Objetivos reales de esta política (no "0% de error")

No existe forma honesta de garantizar un porcentaje de error en la
predicción del mercado. Lo que sí se puede exigir y medir:

- **0 órdenes que evadan el módulo de riesgo.**
- **0 activaciones accidentales del modo real.**
- **0 claves privadas almacenadas en git.**
- **100% de las órdenes reconciliadas contra el exchange** (lo que el bot
  cree que pasó coincide con lo que el exchange confirma).
- **100% de las posiciones con salida protectora (stop-loss) comprobada.**
- **Menos de 0.1% de errores técnicos no controlados**, medido sobre una
  muestra grande de eventos simulados (esto es una meta de calidad de
  software, no una promesa sobre el mercado).
- **Pérdida máxima diaria, semanal y total limitada automáticamente.**
- **Las estrategias no pueden modificar por sí mismas sus propios límites
  de riesgo.**

## Por qué el capital empieza en $0 / mínimo

Con poco capital, cualquier error de diseño se paga proporcionalmente caro
en comisiones y en mínimos de exchange. Empezar en simulación total (Fase 0
y 1 no cuestan nada) permite encontrar errores de diseño sin que cuesten
dinero real.

## Por qué el circuit breaker detiene el bot en vez de "reducir riesgo y seguir"

Reducir el riesgo automáticamente tras pérdidas y seguir operando es una
decisión de estrategia, no de seguridad — y tomar esa decisión en caliente,
sin supervisión humana, es exactamente el tipo de "autonomía peligrosa" que
este proyecto evita. Por eso el circuit breaker detiene el bot por completo
y exige revisión manual.

## Por qué el bot nunca aumenta el riesgo para alcanzar el mínimo del exchange

Es tentador, con poco capital, subir el tamaño de la operación "un poco" para
que supere el `MIN_NOTIONAL` del exchange. Hacerlo de forma automática
significa que el bot está decidiendo cuánto capital arriesgar en tiempo
real, fuera de la política ya aprobada. Por eso la regla es: si no alcanza
el mínimo con el riesgo permitido, se rechaza la operación, punto.

## Proceso para cambiar este archivo

1. Se abre una tarea explícita titulada "Cambio de política de riesgo".
2. Se documenta la razón del cambio y la fecha.
3. Se edita `config/risk-policy.yaml` a mano (revisado por el usuario).
4. Nunca se hace como parte de una tarea de "mejorar la estrategia" o
   "arreglar un bug".
