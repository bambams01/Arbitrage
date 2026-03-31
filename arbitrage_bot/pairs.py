from __future__ import annotations

from collections import defaultdict


def normalize_symbol(symbol: str) -> str:
    return symbol.replace(":USDT", "").replace("-", "/").upper()


def build_pair_index(exchange_markets: dict[str, dict]) -> dict[str, list[str]]:
    pair_map: dict[str, list[str]] = defaultdict(list)

    for exchange_id, markets in exchange_markets.items():
        for symbol, market in markets.items():
            if market.get("quote") != "USDT":
                continue
            normalized = normalize_symbol(symbol)
            pair_map[normalized].append(exchange_id)

    return {symbol: exch for symbol, exch in pair_map.items() if len(exch) >= 2}
