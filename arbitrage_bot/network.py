from __future__ import annotations


def infer_transfer_network(buy_currency: dict, sell_currency: dict) -> tuple[str | None, bool, float]:
    buy_networks = buy_currency.get("networks") or {}
    sell_networks = sell_currency.get("networks") or {}

    for network_name, buy_info in buy_networks.items():
        sell_info = sell_networks.get(network_name)
        if not sell_info:
            continue

        withdraw_ok = buy_info.get("withdraw", buy_currency.get("withdraw", False))
        deposit_ok = sell_info.get("deposit", sell_currency.get("deposit", False))
        if not withdraw_ok or not deposit_ok:
            continue

        fee = buy_info.get("fee")
        try:
            fee = float(fee) if fee is not None else 0.0
        except Exception:
            fee = 0.0
        return network_name, True, fee

    withdraw_ok = buy_currency.get("withdraw", False)
    deposit_ok = sell_currency.get("deposit", False)
    if withdraw_ok and deposit_ok:
        fee = buy_currency.get("fee") or 0.0
        try:
            fee = float(fee)
        except Exception:
            fee = 0.0
        return None, True, fee

    return None, False, 0.0
