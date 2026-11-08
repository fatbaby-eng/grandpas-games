"""JSON save file in the user's home directory (one slot, autosaved on scene change)."""
import json
import os
import sys
from pathlib import Path

from .config import APP_DIR_NAME, SAVE_VERSION


def default_save_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_DIR_NAME


class SaveManager:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else default_save_dir() / "save.json"

    def exists(self) -> bool:
        return self.path.is_file()

    def save(self, state: dict) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(state)
        payload.setdefault("version", SAVE_VERSION)
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.path)       # atomic on every platform we support
        return self.path

    def load(self) -> dict | None:
        if not self.exists():
            return None
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(data, dict) or data.get("version", 0) > SAVE_VERSION:
            return None
        return data

    def delete(self):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
