"""Asset loading with placeholder fallbacks.

Lookup order for an image: assets/images/<filename>, else a procedurally drawn
placeholder. Real art drops in by matching the filenames referenced in
game/content/*.json (see assets/manifest.json for the full list).
"""
import pygame

from . import placeholders
from .config import IMAGES_DIR, FONTS_DIR


def _display_ready():
    return pygame.display.get_init() and pygame.display.get_surface() is not None


class AssetManager:
    def __init__(self, content):
        self.content = content
        self._images: dict = {}
        self._fonts: dict = {}
        self._font_path = None
        if FONTS_DIR.is_dir():
            ttfs = sorted(FONTS_DIR.glob("*.ttf")) + sorted(FONTS_DIR.glob("*.otf"))
            if ttfs:
                self._font_path = str(ttfs[0])

    # Fonts ------------------------------------------------------------------
    def font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self._fonts:
            f = pygame.font.Font(self._font_path, size)
            f.set_bold(bold and self._font_path is None)
            self._fonts[key] = f
        return self._fonts[key]

    # Images -----------------------------------------------------------------
    def _finish(self, surf: pygame.Surface) -> pygame.Surface:
        if _display_ready():
            return surf.convert_alpha()
        return surf

    def _file(self, filename: str | None, size=None):
        if not filename:
            return None
        path = IMAGES_DIR / filename
        if not path.is_file():
            return None
        try:
            surf = pygame.image.load(str(path))
        except pygame.error:
            return None
        if size and surf.get_size() != tuple(size):
            surf = pygame.transform.smoothscale(surf, size)
        return self._finish(surf)

    def background(self, scene: dict) -> pygame.Surface:
        key = ("bg", scene["id"])
        if key not in self._images:
            surf = self._file(scene.get("background"), (1280, 640))
            if surf is None:
                surf = placeholders.background(scene)
                surf = surf.convert() if _display_ready() else surf
            self._images[key] = surf
        return self._images[key]

    def character(self, char_id: str, w: int, h: int, frame: int = 0,
                  facing: str = "right", talking: bool = False) -> pygame.Surface:
        char = self.content.character(char_id)
        anim_frame = (frame // 8) % 2 if talking else 0
        key = ("char", char_id, w, h, anim_frame, facing, talking, frame % 40 in (0, 1))
        if key not in self._images:
            sprite_name = char.get("sprite")
            surf = self._file(sprite_name, (w, h))
            if surf is not None and facing == "left":
                surf = pygame.transform.flip(surf, True, False)
            if surf is None:
                surf = self._finish(placeholders.character(char, w, h, frame, facing, talking))
            self._images[key] = surf
        return self._images[key]

    def icon(self, item_id: str, size: int = 48) -> pygame.Surface:
        key = ("icon", item_id, size)
        if key not in self._images:
            item = self.content.item(item_id)
            surf = self._file(item.get("icon"), (size, size))
            if surf is None:
                surf = self._finish(placeholders.icon(item, size))
            self._images[key] = surf
        return self._images[key]

    def prop(self, scene_id: str, hotspot: dict) -> pygame.Surface:
        w, h = hotspot["rect"][2], hotspot["rect"][3]
        key = ("prop", scene_id, hotspot["id"], w, h)
        if key not in self._images:
            surf = self._file(hotspot.get("image"), (w, h))
            if surf is None:
                surf = self._finish(placeholders.prop(hotspot, w, h))
            self._images[key] = surf
        return self._images[key]

    def portrait(self, char_id: str, size: int = 96) -> pygame.Surface:
        char = self.content.character(char_id)
        key = ("portrait", char_id, size)
        if key not in self._images:
            surf = self._file(char.get("portrait"), (size, size))
            if surf is None:
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 255, 255), (size // 2, size // 2), size // 2)
                pygame.draw.circle(surf, tuple(char.get("color", (200, 200, 200))), (size // 2, size // 2), size // 2 - 4)
                face = placeholders.character(char, int(size * 0.9), int(size * 0.62), frame=5)
                surf.blit(face, face.get_rect(center=(size // 2, size // 2)))
                surf = self._finish(surf)
            self._images[key] = surf
        return self._images[key]
