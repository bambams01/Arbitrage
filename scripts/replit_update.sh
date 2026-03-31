#!/usr/bin/env bash
set -euo pipefail

echo "[replit-update] Pulling latest changes from GitHub..."
git pull origin main

source .venv/bin/activate || true
pip install -r requirements.txt

echo "[replit-update] Update complete. Restart the repl if needed."
