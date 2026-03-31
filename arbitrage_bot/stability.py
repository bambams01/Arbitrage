from __future__ import annotations

import time


def confirm_opportunity_stability(exchange_manager, symbol: str, buy_exchange: str, sell_exchange: str, checks: int = 3, delay_seconds: float = 1.0) -> bool:
    observed = 0
    for index in range(checks):
        buy_tickers = exchange_manager.fetch_tickers([symbol]).get(buy_exchange, {})
        sell_tickers = exchange_manager.fetch_tickers([symbol]).get(sell_exchange, {})

        buy = buy_tickers.get(symbol)
        sell = sell_tickers.get(symbol)
        if buy and sell and buy.get("ask") and sell.get("bid") and float(sell.get("bid")) > float(buy.get("ask")):
            observed += 1

        if index < checks - 1:
            time.sleep(delay_seconds)

    return observed == checks
