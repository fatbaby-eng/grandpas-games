"""Global constants. Nothing here is content; content lives in game/content/*.json."""
from pathlib import Path

TITLE = "Baker's Undersea Adventure"
WIDTH, HEIGHT = 1280, 720
FPS = 60

INVENTORY_BAR_H = 80
PLAY_H = HEIGHT - INVENTORY_BAR_H          # 640: the part of the window the scene uses
PLAYER_SPEED = 260.0                       # pixels per second
HINT_DELAY = 180.0                         # seconds without progress before a hint bubble appears
MINIGAME_SKIP_AFTER = 30.0                 # seconds before the Skip button appears
MINIGAME_SKIP_FAILS = 3                    # or after this many failed attempts

ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "game" / "content"
ASSETS_DIR = ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"
FONTS_DIR = ASSETS_DIR / "fonts"

SAVE_VERSION = 1
APP_DIR_NAME = "BakersUnderseaAdventure"
