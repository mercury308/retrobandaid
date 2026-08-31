import json
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "last_source_dir": "",
    "last_patch_dir": "",
    "last_output_dir": "",
    "theme": "system",
    "keep_copier_headers": True,
    "verify_checksums": True,
}


class ConfigManager:
    """Loads and persists user settings as JSON in the user's config directory."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = Path(config_path) if config_path else self._default_config_path()
        self._data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    @staticmethod
    def _default_config_path() -> Path:
        return Path.home() / ".retrobandaid" / "config.json"

    def load(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass  # fall back to defaults on a corrupt/unreadable config file

    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._data)
