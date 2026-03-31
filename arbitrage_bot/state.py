from __future__ import annotations

from pathlib import Path
import json


class AlertState:
    def __init__(self, path: str = "state/alerts.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def should_alert(self, key: str, net_spread_pct: float, threshold_delta: float = 0.2) -> bool:
        previous = self.data.get(key)
        if previous is None:
            self.data[key] = net_spread_pct
            self._save()
            return True
        if abs(net_spread_pct - float(previous)) >= threshold_delta:
            self.data[key] = net_spread_pct
            self._save()
            return True
        return False

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
