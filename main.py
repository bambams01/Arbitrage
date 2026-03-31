from __future__ import annotations

import argparse
import time

from arbitrage_bot.config import load_config
from arbitrage_bot.exchanges import ExchangeManager
from arbitrage_bot.executor import TradeExecutor
from arbitrage_bot.logging_utils import setup_logger
from arbitrage_bot.notifier import TelegramNotifier
from arbitrage_bot.pairs import build_pair_index
from arbitrage_bot.scanner import scan_opportunities
from arbitrage_bot.state import AlertState


def format_alert(opp) -> str:
    return (
        "Arbitrage opportunity\n"
        f"Pair: {opp.symbol}\n"
        f"Buy: {opp.buy_exchange} @ {opp.buy_price:.8f}\n"
        f"Sell: {opp.sell_exchange} @ {opp.sell_price:.8f}\n"
        f"Gross spread: {opp.gross_spread_pct:.4f}%\n"
        f"Net spread: {opp.net_spread_pct:.4f}%\n"
        f"Buy fee: {opp.buy_fee_pct:.4f}%\n"
        f"Sell fee: {opp.sell_fee_pct:.4f}%\n"
        f"Withdraw fee impact: {opp.withdraw_fee_pct:.4f}%\n"
        f"Network: {opp.network or '-'}\n"
        f"Sim buy: {opp.simulated_buy_price or opp.buy_price:.8f}\n"
        f"Sim sell: {opp.simulated_sell_price or opp.sell_price:.8f}\n"
        f"Tradable base: {opp.tradable_base_amount or 0:.8f}\n"
        f"Expected quote out: {opp.expected_quote_out or 0:.8f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Crypto arbitrage scanner")
    parser.add_argument("--config", default="config.yaml", help="Path ke config YAML")
    args = parser.parse_args()

    logger = setup_logger()
    logger.info("Starting arbitrage bot")

    config = load_config(args.config)
    notifier = TelegramNotifier(config.get("telegram", {}), logger)
    exchange_manager = ExchangeManager(config, logger)
    executor = TradeExecutor(config, logger)
    alert_state = AlertState()

    exchange_manager.initialize()
    if not exchange_manager.instances:
        logger.error("Tidak ada exchange aktif. Periksa config.yaml")
        return

    bot_cfg = config.get("bot", {})
    scan_interval = float(bot_cfg.get("scan_interval_seconds", 5))

    while True:
        try:
            markets = exchange_manager.refresh_markets()
            exchange_manager.refresh_currencies()
            pair_index = build_pair_index(markets)
            logger.info("Pair index contains %s candidates", len(pair_index))

            if not pair_index:
                logger.warning("Tidak ada pair kandidat. Cek exchange aktif, koneksi, atau market availability.")
                time.sleep(scan_interval)
                continue

            opportunities = scan_opportunities(config, exchange_manager, pair_index, logger)
            for opp in opportunities[:10]:
                logger.info(
                    "OPP %s | BUY %s %.8f | SELL %s %.8f | NET %.4f%%",
                    opp.symbol,
                    opp.buy_exchange,
                    opp.buy_price,
                    opp.sell_exchange,
                    opp.sell_price,
                    opp.net_spread_pct,
                )
                alert_key = f"{opp.symbol}:{opp.buy_exchange}:{opp.sell_exchange}"
                if alert_state.should_alert(alert_key, opp.net_spread_pct):
                    notifier.send(format_alert(opp))
                executor.handle(opp)

            time.sleep(scan_interval)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as exc:
            logger.exception("Unexpected error: %s", exc)
            time.sleep(scan_interval)


if __name__ == "__main__":
    main()
