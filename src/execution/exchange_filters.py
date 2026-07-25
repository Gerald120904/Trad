"""Dynamic Binance Spot symbol-filter cache and order-size validation."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class ExchangeFilterConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    cache_path: Path
    cache_ttl_seconds: int = Field(default=300, ge=1, le=86_400)


class ExchangeInfoClient(Protocol):
    def get_symbol_info(self, symbol: str) -> dict[str, Any] | None: ...


@dataclass(frozen=True)
class ValidationResult:
    accepted: bool
    reasons: tuple[str, ...]
    normalized_quantity: Decimal
    normalized_price: Decimal


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid decimal for {label}: {value!r}") from exc
    if not result.is_finite():
        raise ValueError(f"Non-finite decimal for {label}")
    return result


def _aligned(value: Decimal, minimum: Decimal, step: Decimal) -> bool:
    return step == 0 or (value - minimum) % step == 0


class ExchangeFilterCache:
    """Caches raw exchangeInfo responses with a strict expiry timestamp."""

    def __init__(
        self,
        client: ExchangeInfoClient,
        config: ExchangeFilterConfig,
        *,
        clock: Any = time.time,
    ) -> None:
        self._client = client
        self._config = config
        self._clock = clock

    def get(self, symbol: str) -> dict[str, Any]:
        symbol = symbol.upper()
        cached = self._read_cache()
        entry = cached.get(symbol)
        now = float(self._clock())
        if entry and now - float(entry["fetched_at"]) < self._config.cache_ttl_seconds:
            return dict(entry["symbol_info"])
        info = self._client.get_symbol_info(symbol)
        if not info:
            raise LookupError(f"Binance exchangeInfo has no symbol {symbol}")
        cached[symbol] = {"fetched_at": now, "symbol_info": info}
        self._write_cache(cached)
        return info

    def _read_cache(self) -> dict[str, Any]:
        try:
            with self._config.cache_path.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
            return payload if isinstance(payload, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _write_cache(self, payload: dict[str, Any]) -> None:
        path = self._config.cache_path
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=True, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)


def validate_order_size(
    symbol_info: dict[str, Any],
    quantity: Decimal | str,
    price: Decimal | str,
    *,
    order_type: str = "LIMIT",
    open_orders: int = 0,
    open_algo_orders: int = 0,
) -> ValidationResult:
    """Validate quantity and price against the live filters supplied by Binance."""

    qty = _decimal(quantity, "quantity")
    px = _decimal(price, "price")
    reasons: list[str] = []
    if qty <= 0:
        reasons.append("quantity_must_be_positive")
    if px <= 0:
        reasons.append("price_must_be_positive")

    filters = {item["filterType"]: item for item in symbol_info.get("filters", [])}
    price_filter = filters.get("PRICE_FILTER")
    if price_filter:
        minimum = _decimal(price_filter["minPrice"], "minPrice")
        maximum = _decimal(price_filter["maxPrice"], "maxPrice")
        tick = _decimal(price_filter["tickSize"], "tickSize")
        if minimum and px < minimum:
            reasons.append("price_below_minimum")
        if maximum and px > maximum:
            reasons.append("price_above_maximum")
        if not _aligned(px, minimum, tick):
            reasons.append("price_not_aligned_to_tick_size")

    lot_name = "MARKET_LOT_SIZE" if order_type.upper() == "MARKET" and "MARKET_LOT_SIZE" in filters else "LOT_SIZE"
    lot_filter = filters.get(lot_name)
    if lot_filter:
        minimum = _decimal(lot_filter["minQty"], "minQty")
        maximum = _decimal(lot_filter["maxQty"], "maxQty")
        step = _decimal(lot_filter["stepSize"], "stepSize")
        if qty < minimum:
            reasons.append("quantity_below_minimum")
        if maximum and qty > maximum:
            reasons.append("quantity_above_maximum")
        if not _aligned(qty, minimum, step):
            reasons.append("quantity_not_aligned_to_step_size")

    notional = qty * px
    min_notional_filter = filters.get("NOTIONAL") or filters.get("MIN_NOTIONAL")
    if min_notional_filter:
        minimum = _decimal(min_notional_filter.get("minNotional", "0"), "minNotional")
        maximum = _decimal(min_notional_filter.get("maxNotional", "0"), "maxNotional")
        if notional < minimum:
            reasons.append("notional_below_minimum")
        if maximum and notional > maximum:
            reasons.append("notional_above_maximum")

    max_orders = filters.get("MAX_NUM_ORDERS")
    if max_orders and open_orders >= int(max_orders["maxNumOrders"]):
        reasons.append("max_open_orders_reached")
    max_algo = filters.get("MAX_NUM_ALGO_ORDERS")
    if max_algo and open_algo_orders >= int(max_algo["maxNumAlgoOrders"]):
        reasons.append("max_open_algo_orders_reached")

    return ValidationResult(not reasons, tuple(reasons), qty, px)
