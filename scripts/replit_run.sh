#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
  bash scripts/replit_bootstrap.sh
fi

source .venv/bin/activate
python main.py --config config.yaml
