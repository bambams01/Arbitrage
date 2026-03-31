from __future__ import annotations

from pathlib import Path
import yaml


def load_config(path: str = "config.yaml") -> dict:
    cfg_path = Path(path)
    if not cfg_path.exists():
        example = Path("config.example.yaml")
        if example.exists():
            raise FileNotFoundError(
                f"Config '{path}' tidak ditemukan. Salin '{example}' menjadi '{path}' lalu edit isinya."
            )
        raise FileNotFoundError(f"Config '{path}' tidak ditemukan.")

    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    data.setdefault("bot", {})
    data.setdefault("telegram", {})
    data.setdefault("exchanges", [])
    return data
