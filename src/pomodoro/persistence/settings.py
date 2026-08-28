"""JSON-backed persistence for user settings (timer config + UI prefs)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..core.timer import TimerConfig
from .paths import app_data_dir

_SETTINGS_FILENAME = "settings.json"

_DEFAULT_THEME = "dark"


class SettingsStore:
    """Loads/saves :class:`TimerConfig` plus a couple of UI preferences."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (app_data_dir() / _SETTINGS_FILENAME)
        self.theme: str = _DEFAULT_THEME
        self.last_tag: str = ""
        self.config: TimerConfig = TimerConfig()
        self.load()

    def load(self) -> None:
        if not self.path.is_file():
            return
        try:
            raw: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        config_fields = {f for f in TimerConfig.__dataclass_fields__}
        config_data = {k: v for k, v in raw.get("config", {}).items() if k in config_fields}
        try:
            self.config = TimerConfig(**{**asdict(TimerConfig()), **config_data})
        except (TypeError, ValueError):
            self.config = TimerConfig()

        self.theme = raw.get("theme", _DEFAULT_THEME)
        self.last_tag = raw.get("last_tag", "")

    def save(self) -> None:
        payload = {
            "config": asdict(self.config),
            "theme": self.theme,
            "last_tag": self.last_tag,
        }
        try:
            self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass
