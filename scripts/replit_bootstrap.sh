#!/usr/bin/env bash
set -euo pipefail

echo "[replit-bootstrap] Starting setup..."

if [ ! -d .venv ]; then
  python -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f config.yaml ]; then
  cp config.example.yaml config.yaml
  echo "[replit-bootstrap] config.yaml created from config.example.yaml"
fi

echo "[replit-bootstrap] Setup complete."
echo "[replit-bootstrap] Run with: python main.py --config config.yaml"
