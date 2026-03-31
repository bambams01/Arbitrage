from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TickerSnapshot:
    exchange: str
    symbol: str
    ask: float | None
    bid: float | None
    quote_volume: float | None
    base_volume: float | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Opportunity:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    gross_spread_pct: float
    net_spread_pct: float
    buy_fee_pct: float
    sell_fee_pct: float
    withdraw_fee_pct: float
    quote_volume_hint: float | None = None
    network: str | None = None
    simulated_buy_price: float | None = None
    simulated_sell_price: float | None = None
    tradable_base_amount: float | None = None
    expected_quote_out: float | None = None
