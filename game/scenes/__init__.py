"""Scene registry: scene ids from scenes.json map to classes here. Any id not
listed uses BaseScene, so new scenes can be added with JSON alone."""
from .base_scene import BaseScene
from .coral_reef import CoralReef
from .kelp_forest import KelpForest
from .sunken_ship import SunkenShip
from .dark_cave import DarkCave
from .festival_grounds import FestivalGrounds

REGISTRY = {
    "__default__": BaseScene,
    "coral_reef": CoralReef,
    "kelp_forest": KelpForest,
    "sunken_ship": SunkenShip,
    "dark_cave": DarkCave,
    "festival_grounds": FestivalGrounds,
}
