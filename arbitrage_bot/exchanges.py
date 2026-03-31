from __future__ import annotations

import time
from typing import Any

import ccxt


class ExchangeManager:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        self.instances: dict[str, Any] = {}
        self.markets_cache: dict[str, dict] = {}
        self.currencies_cache: dict[str, dict] = {}
        self.last_market_refresh = 0.0
        self.last_currency_refresh = 0.0

    def initialize(self) -> None:
        for exchange_cfg in self.config.get("exchanges", []):
            if not exchange_cfg.get("enabled", False):
                continue

            exchange_id = exchange_cfg["id"]
            klass = getattr(ccxt, exchange_id, None)
            if klass is None:
                self.logger.warning("Exchange %s tidak didukung oleh ccxt", exchange_id)
                continue

            params = {
                "enableRateLimit": True,
                "apiKey": exchange_cfg.get("api_key") or None,
                "secret": exchange_cfg.get("secret") or None,
                "password": exchange_cfg.get("password") or None,
            }
            params = {k: v for k, v in params.items() if v is not None}

            instance = klass(params)
            self.instances[exchange_id] = instance
            self.logger.info("Initialized exchange: %s", exchange_id)

    def refresh_markets(self, force: bool = False) -> dict[str, dict]:
        interval = self.config.get("bot", {}).get("market_refresh_minutes", 60) * 60
        now = time.time()
        if not force and self.markets_cache and now - self.last_market_refresh < interval:
            return self.markets_cache

        refreshed = {}
        for exchange_id, exchange in self.instances.items():
            try:
                markets = exchange.load_markets()
                refreshed[exchange_id] = markets
                self.logger.info("Loaded markets: %s (%s symbols)", exchange_id, len(markets))
            except Exception as exc:
                self.logger.exception("Failed to load markets for %s: %s", exchange_id, exc)

        self.markets_cache = refreshed
        self.last_market_refresh = now
        return refreshed

    def refresh_currencies(self, force: bool = False) -> dict[str, dict]:
        interval = self.config.get("bot", {}).get("network_refresh_minutes", 15) * 60
        now = time.time()
        if not force and self.currencies_cache and now - self.last_currency_refresh < interval:
            return self.currencies_cache

        refreshed = {}
        for exchange_id, exchange in self.instances.items():
            try:
                currencies = exchange.fetch_currencies()
                refreshed[exchange_id] = currencies
                self.logger.info("Loaded currencies: %s (%s assets)", exchange_id, len(currencies))
            except Exception as exc:
                self.logger.warning("Failed to fetch currencies for %s: %s", exchange_id, exc)
                refreshed[exchange_id] = {}

        self.currencies_cache = refreshed
        self.last_currency_refresh = now
        return refreshed

    def fetch_tickers(self, symbols: list[str]) -> dict[str, dict]:
        all_tickers: dict[str, dict] = {}
        for exchange_id, exchange in self.instances.items():
            try:
                supported = [s for s in symbols if s in exchange.markets]
                if not supported:
                    all_tickers[exchange_id] = {}
                    continue

                tickers = exchange.fetch_tickers(supported)
                all_tickers[exchange_id] = tickers
                self.logger.info("Fetched tickers: %s (%s symbols)", exchange_id, len(tickers))
            except Exception as exc:
                self.logger.warning("Failed to fetch tickers for %s: %s", exchange_id, exc)
                all_tickers[exchange_id] = {}
        return all_tickers

    def estimate_trading_fee_pct(self, exchange_id: str, symbol: str) -> float:
        market = self.markets_cache.get(exchange_id, {}).get(symbol, {})
        taker = market.get("taker")
        if taker is None:
            return 0.001
        return float(taker)

    def fetch_order_book(self, exchange_id: str, symbol: str, limit: int = 20) -> dict:
        exchange = self.instances[exchange_id]
        return exchange.fetch_order_book(symbol, limit=limit)
