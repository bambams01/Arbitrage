from __future__ import annotations

from arbitrage_bot.models import Opportunity


class TradeExecutor:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger

    def handle(self, opportunity: Opportunity) -> None:
        paper_trade = self.config.get("bot", {}).get("paper_trade", True)
        if paper_trade:
            self.logger.info(
                "[PAPER] %s | BUY %s @ %.8f | SELL %s @ %.8f | NET %.4f%%",
                opportunity.symbol,
                opportunity.buy_exchange,
                opportunity.buy_price,
                opportunity.sell_exchange,
                opportunity.sell_price,
                opportunity.net_spread_pct,
            )
            return

        self.logger.warning(
            "Live trading belum diimplementasikan. Opportunity terdeteksi: %s", opportunity
        )
