# Glosario de dominio usado en este proyecto

- **Volumen**: cantidad negociada en un periodo de tiempo (indicador vertical).
- **Volume Profile**: cantidad negociada por nivel de precio (indicador horizontal).
- **Delta**: diferencia entre compras y ventas a mercado en una vela/periodo.
- **Order flow**: flujo de órdenes a mercado, medido vía delta u order book.
- **Drawdown**: caída desde un máximo de capital hasta el siguiente mínimo,
  antes de una nueva recuperación.
- **Profit factor**: ganancia bruta total / pérdida bruta total.
- **Walk-forward validation**: validar una estrategia en ventanas de tiempo
  consecutivas, ajustando parámetros solo en la ventana de entrenamiento y
  evaluando siempre en la ventana siguiente (nunca la misma).
- **Slippage**: diferencia entre el precio esperado de una orden y el precio
  real de ejecución.
- **Circuit breaker**: mecanismo que detiene el sistema automáticamente al
  alcanzar un límite de riesgo predefinido.
- **Look-ahead bias**: error de backtesting en que la estrategia usa,
  sin querer, información que no estaría disponible en el momento real de
  la decisión.
