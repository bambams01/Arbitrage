from __future__ import annotations

import requests


class TelegramNotifier:
    def __init__(self, cfg: dict, logger):
        self.enabled = cfg.get("enabled", False)
        self.bot_token = cfg.get("bot_token", "")
        self.chat_id = cfg.get("chat_id", "")
        self.logger = logger

    def send(self, message: str) -> None:
        if not self.enabled:
            return
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram enabled but bot token/chat id kosong")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
        except Exception as exc:
            self.logger.warning("Failed to send Telegram alert: %s", exc)
