"""Loads every JSON content file once and hands out the parsed data."""
import json
from pathlib import Path

from .config import CONTENT_DIR

FILES = ("scenes", "items", "dialogue", "quests", "characters")


class Content:
    def __init__(self, content_dir: Path | None = None):
        self.dir = Path(content_dir) if content_dir else CONTENT_DIR
        for name in FILES:
            with open(self.dir / f"{name}.json", encoding="utf-8") as fh:
                setattr(self, name, json.load(fh))

    # Convenience accessors -------------------------------------------------
    def scene(self, scene_id: str) -> dict:
        return self.scenes[scene_id]

    def item(self, item_id: str) -> dict:
        return self.items[item_id]

    def character(self, char_id: str) -> dict:
        return self.characters.get(char_id, {"name": char_id, "color": [200, 200, 200]})

    def dialogue_entry(self, dialogue_id: str) -> dict:
        return self.dialogue[dialogue_id]
