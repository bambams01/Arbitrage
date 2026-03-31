from __future__ import annotations


def simulate_market_buy_from_asks(asks: list[list[float]], quote_amount: float) -> tuple[float | None, float, float]:
    if quote_amount <= 0:
        return None, 0.0, 0.0

    remaining_quote = quote_amount
    acquired_base = 0.0
    spent_quote = 0.0

    for level in asks:
        if len(level) < 2:
            continue
        price, amount = float(level[0]), float(level[1])
        if price <= 0 or amount <= 0:
            continue

        level_quote = price * amount
        take_quote = min(level_quote, remaining_quote)
        take_base = take_quote / price

        acquired_base += take_base
        spent_quote += take_quote
        remaining_quote -= take_quote

        if remaining_quote <= 1e-12:
            break

    if acquired_base <= 0:
        return None, 0.0, spent_quote

    avg_price = spent_quote / acquired_base
    return avg_price, acquired_base, spent_quote


def simulate_market_sell_to_bids(bids: list[list[float]], base_amount: float) -> tuple[float | None, float, float]:
    if base_amount <= 0:
        return None, 0.0, 0.0

    remaining_base = base_amount
    sold_base = 0.0
    received_quote = 0.0

    for level in bids:
        if len(level) < 2:
            continue
        price, amount = float(level[0]), float(level[1])
        if price <= 0 or amount <= 0:
            continue

        take_base = min(amount, remaining_base)
        sold_base += take_base
        received_quote += take_base * price
        remaining_base -= take_base

        if remaining_base <= 1e-12:
            break

    if sold_base <= 0:
        return None, 0.0, received_quote

    avg_price = received_quote / sold_base
    return avg_price, sold_base, received_quote
