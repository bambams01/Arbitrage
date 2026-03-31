# Arbitrage Bot

Bot arbitrase crypto multi-exchange berbasis Python.

## Fitur saat ini
- Multi-exchange via `ccxt`
- Sinkronisasi market dan pair `*/USDT`
- Pair index untuk pair yang tersedia di >=2 exchange
- Scanner spread dasar
- Estimasi fee trading
- Cek network/transfer baseline (best effort)
- Telegram alert
- `paper_trade` mode (aman untuk uji coba)
- Struktur modular untuk dikembangkan ke eksekusi real trade

## Catatan penting
Bot ini **belum aman untuk live trading otomatis**. Default-nya dibuat untuk:
- scanning opportunity
- paper trading
- alerting
- logging

Eksekusi real trade, withdraw, dan auto-sell lintas exchange butuh hardening tambahan, terutama untuk:
- balance handling
- withdrawal safety
- network confirmation
- slippage real-time
- retry / timeout / partial fill
- risk management

## Instalasi
```bash
python -m venv .venv
. .venv/bin/activate  # Linux
pip install -r requirements.txt
```

## Konfigurasi
Salin `config.example.yaml` menjadi `config.yaml`, lalu sesuaikan.

Opsional: isi token API exchange jika ingin baca balance/private endpoint.
Untuk scanning market publik, biasanya tidak wajib.

## Menjalankan
```bash
python main.py --config config.yaml
```

## Catatan SSL / sertifikat
Jika exchange API gagal di mesin tertentu dengan error SSL/certificate, biasanya masalah ada di environment OS/Python certificate store, bukan di logika bot. Pada VPS Linux yang sehat, ini biasanya jauh lebih minim.

## Struktur
- `main.py` - entry point
- `arbitrage_bot/config.py` - loader config
- `arbitrage_bot/exchanges.py` - init exchange + market sync
- `arbitrage_bot/pairs.py` - pair normalization + pair index
- `arbitrage_bot/scanner.py` - spread scanning
- `arbitrage_bot/notifier.py` - Telegram alert
- `arbitrage_bot/executor.py` - paper trade / execution stub
- `arbitrage_bot/logging_utils.py` - logger setup

## Roadmap
- orderbook simulation
- network metadata yang lebih akurat per exchange
- persistence state
- stability confirmation beberapa tick
- paper portfolio
- risk engine
- optional websocket ticker feeds
