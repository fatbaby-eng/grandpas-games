"""All mutable game progress in one serialisable object."""
from .config import SAVE_VERSION
from .inventory import Inventory


class GameState:
    def __init__(self, start_scene="coral_reef", start_pos=(640, 520)):
        self.flags: set[str] = set()
        self.counters: dict[str, int] = {}
        self.inventory = Inventory(on_change=self._progress)
        self.scene_id = start_scene
        self.player_pos = list(start_pos)
        self.hints_enabled = True
        self.minigames_done: set[str] = set()
        self.play_time = 0.0
        # Bumped whenever something meaningful changes; the hint system watches it.
        self.progress_version = 0

    # Flags ----------------------------------------------------------------
    def has_flag(self, flag: str) -> bool:
        return flag in self.flags

    def set_flag(self, flag: str) -> bool:
        if flag in self.flags:
            return False
        self.flags.add(flag)
        self._progress()
        return True

    def clear_flag(self, flag: str) -> bool:
        if flag not in self.flags:
            return False
        self.flags.discard(flag)
        self._progress()
        return True

    def inc(self, counter: str, amount: int = 1) -> int:
        self.counters[counter] = self.counters.get(counter, 0) + amount
        return self.counters[counter]

    def _progress(self):
        self.progress_version += 1

    # Serialisation --------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "version": SAVE_VERSION,
            "scene": self.scene_id,
            "player_pos": [int(self.player_pos[0]), int(self.player_pos[1])],
            "inventory": self.inventory.to_list(),
            "flags": sorted(self.flags),
            "counters": dict(self.counters),
            "hints_enabled": self.hints_enabled,
            "minigames_done": sorted(self.minigames_done),
            "play_time": round(self.play_time, 1),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        state = cls(start_scene=data.get("scene", "coral_reef"),
                    start_pos=tuple(data.get("player_pos", (640, 520))))
        state.flags = set(data.get("flags", []))
        state.counters = dict(data.get("counters", {}))
        state.inventory.load_list(data.get("inventory", []))
        state.hints_enabled = bool(data.get("hints_enabled", True))
        state.minigames_done = set(data.get("minigames_done", []))
        state.play_time = float(data.get("play_time", 0.0))
        return state
