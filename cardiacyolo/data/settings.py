"""Application settings management."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("cardiacyolo")

DEFAULT_SETTINGS_PATH = Path.home() / ".cardiacyolo" / "settings.json"

DEFAULT_SETTINGS = {
    "default_model": "YOLOv26",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "use_gpu": True,
    "output_directory": str(Path.home() / "CardiacYOLO_Output"),
    "auto_save_results": True,
    "theme": "light",
    "language": "en",
}


class Settings:
    """Manages application settings stored as JSON."""

    def __init__(self, settings_path=None):
        self.settings_path = Path(settings_path) if settings_path else DEFAULT_SETTINGS_PATH
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self._settings: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load settings from disk, falling back to defaults."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    self._settings = json.load(f)
                # Fill in any missing defaults
                for key, value in DEFAULT_SETTINGS.items():
                    self._settings.setdefault(key, value)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load settings: {e}. Using defaults.")
                self._settings = DEFAULT_SETTINGS.copy()
        else:
            self._settings = DEFAULT_SETTINGS.copy()
            self.save()

    def save(self):
        """Persist settings to disk."""
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default=None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        self._settings[key] = value
        self.save()

    def reset(self):
        """Reset to default settings."""
        self._settings = DEFAULT_SETTINGS.copy()
        self.save()

    def all(self) -> Dict[str, Any]:
        return dict(self._settings)
