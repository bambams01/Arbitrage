# Arbitrage Bot

Bot arbitrase crypto multi-exchange berbasis Python.

## Fitur saat ini
- Multi-exchange via `ccxt`
- Sinkronisasi market dan pair `*/USDT`
- Pair index untuk pair yang tersedia di >=2 exchange
- Scanner spread yang lebih realistis
- Simulasi orderbook buy/sell
- Estimasi fee trading
- Cek network/transfer baseline (best effort)
- Stability check beberapa tick
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

## Menjalankan di Replit
- Import repo ini ke Replit
- Replit akan memakai `.replit` dan `replit.nix`
- Saat dijalankan, script `scripts/replit_run.sh` akan dipakai
- Bootstrap awal ada di `scripts/replit_bootstrap.sh`
- Update cepat dari GitHub bisa dilakukan dengan `bash scripts/replit_update.sh`
- Edit `config.yaml` sesuai kebutuhan
- Untuk Telegram, isi `bot_token` dan `chat_id`
- Untuk uji coba, biarkan `paper_trade: true`

Catatan:
- Replit cocok untuk demo dan pengujian
- Replit kurang ideal untuk scanner 24/7 jangka panjang
- Untuk operasi serius, pindah ke VPS/Armbian lebih baik

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
- network metadata yang lebih akurat per exchange
- persistence state yang lebih kaya
- paper portfolio
- risk engine
- optional websocket ticker feeds
- live trading path yang aman dan dibatasi
