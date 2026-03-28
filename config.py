# config.py

def load_config():
    # Example configuration
    return {
        "min_spread": 0.01,
        "min_volume": 100,
        "min_buy_usdt": 10,
        "exchanges": ["exchange1", "exchange2"],
        "scan_interval": 3,
        "telegram_config": {
            "enabled": True,
            "bot_token": "your_bot_token",
            "chat_id": "your_chat_id"
        }
    }