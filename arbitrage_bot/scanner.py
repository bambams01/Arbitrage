from __future__ import annotations

from arbitrage_bot.models import Opportunity
from arbitrage_bot.network import infer_transfer_network


def scan_opportunities(config: dict, exchange_manager, pair_index: dict[str, list[str]], logger) -> list[Opportunity]:
    if not pair_index:
        return []

    symbols = sorted(pair_index.keys())
    tickers_by_exchange = exchange_manager.fetch_tickers(symbols)
    currencies_by_exchange = exchange_manager.currencies_cache
    bot_cfg = config.get("bot", {})

    min_spread_pct = float(bot_cfg.get("min_spread_pct", 1.0))
    min_net_spread_pct = float(bot_cfg.get("min_net_spread_pct", 0.5))
    min_quote_volume_usdt = float(bot_cfg.get("min_quote_volume_usdt", 0))
    min_buy_usdt = float(bot_cfg.get("min_buy_usdt", 25))

    opportunities: list[Opportunity] = []

    for symbol, exchanges in pair_index.items():
        base_asset = symbol.split("/")[0]
        rows = []

        for exchange_id in exchanges:
            ticker = tickers_by_exchange.get(exchange_id, {}).get(symbol)
            if not ticker:
                continue

            ask = ticker.get("ask")
            bid = ticker.get("bid")
            quote_volume = ticker.get("quoteVolume")
            base_volume = ticker.get("baseVolume")

            if ask is None or bid is None or ask <= 0 or bid <= 0:
                continue
            if ask * min_buy_usdt < min_buy_usdt:
                continue
            if quote_volume is not None and quote_volume < min_quote_volume_usdt:
                continue

            rows.append(
                {
                    "exchange": exchange_id,
                    "ask": float(ask),
                    "bid": float(bid),
                    "quote_volume": float(quote_volume) if quote_volume is not None else None,
                    "base_volume": float(base_volume) if base_volume is not None else None,
                }
            )

        if len(rows) < 2:
            continue

        buy_side = min(rows, key=lambda x: x["ask"])
        sell_side = max(rows, key=lambda x: x["bid"])

        if buy_side["exchange"] == sell_side["exchange"]:
            continue
        if sell_side["bid"] <= buy_side["ask"]:
            continue

        gross_spread_pct = ((sell_side["bid"] - buy_side["ask"]) / buy_side["ask"]) * 100
        if gross_spread_pct < min_spread_pct:
            continue

        buy_fee_pct = exchange_manager.estimate_trading_fee_pct(buy_side["exchange"], symbol) * 100
        sell_fee_pct = exchange_manager.estimate_trading_fee_pct(sell_side["exchange"], symbol) * 100

        buy_currency = currencies_by_exchange.get(buy_side["exchange"], {}).get(base_asset, {})
        sell_currency = currencies_by_exchange.get(sell_side["exchange"], {}).get(base_asset, {})
        network_name, transferable, withdraw_fee_coin = infer_transfer_network(buy_currency, sell_currency)
        if not transferable:
            continue

        withdraw_fee_pct = 0.0
        if withdraw_fee_coin and min_buy_usdt > 0:
            withdraw_fee_pct = ((withdraw_fee_coin * buy_side["ask"]) / min_buy_usdt) * 100

        net_spread_pct = gross_spread_pct - buy_fee_pct - sell_fee_pct - withdraw_fee_pct
        if net_spread_pct < min_net_spread_pct:
            continue

        opportunities.append(
            Opportunity(
                symbol=symbol,
                buy_exchange=buy_side["exchange"],
                sell_exchange=sell_side["exchange"],
                buy_price=buy_side["ask"],
                sell_price=sell_side["bid"],
                gross_spread_pct=gross_spread_pct,
                net_spread_pct=net_spread_pct,
                buy_fee_pct=buy_fee_pct,
                sell_fee_pct=sell_fee_pct,
                withdraw_fee_pct=withdraw_fee_pct,
                quote_volume_hint=buy_side["quote_volume"] or sell_side["quote_volume"],
                network=network_name,
            )
        )

    opportunities.sort(key=lambda x: x.net_spread_pct, reverse=True)
    logger.info("Scanner found %s opportunities", len(opportunities))
    return opportunities
