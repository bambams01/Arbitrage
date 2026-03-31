from __future__ import annotations

from arbitrage_bot.models import Opportunity
from arbitrage_bot.network import infer_transfer_network
from arbitrage_bot.orderbook import simulate_market_buy_from_asks, simulate_market_sell_to_bids
from arbitrage_bot.stability import confirm_opportunity_stability


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
    orderbook_limit = int(bot_cfg.get("orderbook_limit", 20))
    stability_checks = int(bot_cfg.get("stability_checks", 2))
    stability_delay_seconds = float(bot_cfg.get("stability_delay_seconds", 1.0))

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

        try:
            buy_book = exchange_manager.fetch_order_book(buy_side["exchange"], symbol, orderbook_limit)
            sell_book = exchange_manager.fetch_order_book(sell_side["exchange"], symbol, orderbook_limit)
        except Exception as exc:
            logger.warning("Orderbook fetch failed for %s: %s", symbol, exc)
            continue

        sim_buy_price, acquired_base, spent_quote = simulate_market_buy_from_asks(
            buy_book.get("asks", []), min_buy_usdt
        )
        if sim_buy_price is None or acquired_base <= 0 or spent_quote <= 0:
            continue

        fee_base_loss = acquired_base * (buy_fee_pct / 100)
        transferable_base = max(acquired_base - fee_base_loss - withdraw_fee_coin, 0.0)
        if transferable_base <= 0:
            continue

        sim_sell_price, sold_base, received_quote = simulate_market_sell_to_bids(
            sell_book.get("bids", []), transferable_base
        )
        if sim_sell_price is None or sold_base <= 0 or received_quote <= 0:
            continue

        sell_fee_quote = received_quote * (sell_fee_pct / 100)
        final_quote = max(received_quote - sell_fee_quote, 0.0)
        if final_quote <= 0:
            continue

        simulated_gross_spread_pct = ((sim_sell_price - sim_buy_price) / sim_buy_price) * 100
        withdraw_fee_pct = ((withdraw_fee_coin * sim_buy_price) / spent_quote) * 100 if spent_quote > 0 else 0.0
        net_spread_pct = ((final_quote - spent_quote) / spent_quote) * 100

        if simulated_gross_spread_pct < min_spread_pct:
            continue
        if net_spread_pct < min_net_spread_pct:
            continue

        stable = confirm_opportunity_stability(
            exchange_manager,
            symbol,
            buy_side["exchange"],
            sell_side["exchange"],
            checks=stability_checks,
            delay_seconds=stability_delay_seconds,
        )
        if not stable:
            continue

        opportunities.append(
            Opportunity(
                symbol=symbol,
                buy_exchange=buy_side["exchange"],
                sell_exchange=sell_side["exchange"],
                buy_price=buy_side["ask"],
                sell_price=sell_side["bid"],
                gross_spread_pct=simulated_gross_spread_pct,
                net_spread_pct=net_spread_pct,
                buy_fee_pct=buy_fee_pct,
                sell_fee_pct=sell_fee_pct,
                withdraw_fee_pct=withdraw_fee_pct,
                quote_volume_hint=buy_side["quote_volume"] or sell_side["quote_volume"],
                network=network_name,
                simulated_buy_price=sim_buy_price,
                simulated_sell_price=sim_sell_price,
                tradable_base_amount=transferable_base,
                expected_quote_out=final_quote,
            )
        )

    opportunities.sort(key=lambda x: x.net_spread_pct, reverse=True)
    logger.info("Scanner found %s opportunities", len(opportunities))
    return opportunities
