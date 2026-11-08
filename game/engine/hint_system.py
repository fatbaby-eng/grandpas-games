"""Shows a gentle hint bubble after a while without progress (and on demand via '?')."""
import pygame

from .conditions import pick
from .config import HINT_DELAY, WIDTH
from .ui import draw_panel, draw_text, INK


class HintSystem:
    def __init__(self, game):
        self.game = game
        self.timer = 0.0
        self.visible = False
        self.text = ""
        self._last_version = -1
        self._last_scene = None
        self.rect = pygame.Rect(WIDTH - 440, 20, 420, 110)

    @property
    def enabled(self):
        return self.game.state.hints_enabled

    def toggle(self) -> bool:
        self.game.state.hints_enabled = not self.game.state.hints_enabled
        if not self.enabled:
            self.visible = False
        return self.enabled

    def reset(self):
        self.timer = 0.0
        self.visible = False

    def _current_hint(self) -> str | None:
        scene = self.game.scenes.current
        if scene is None:
            return None
        hints = scene.data.get("hints", [])
        choice = pick(hints, self.game.state)
        if choice is None:
            generic = self.game.content.quests.get("generic_hint")
            return generic
        return choice.get("text")

    def request_now(self):
        text = self._current_hint()
        if text:
            self.text = text
            self.visible = True
            self.timer = 0.0

    def update(self, dt):
        state = self.game.state
        scene_id = state.scene_id
        if state.progress_version != self._last_version or scene_id != self._last_scene:
            self._last_version = state.progress_version
            self._last_scene = scene_id
            self.reset()
            return
        if self.game.dialogue.is_active() or self.game.minigame is not None:
            return
        self.timer += dt
        if self.enabled and not self.visible and self.timer >= HINT_DELAY:
            self.request_now()

    def handle_event(self, event) -> bool:
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                and self.rect.collidepoint(event.pos):
            self.visible = False
            return True
        return False

    def draw(self, screen):
        if not self.visible:
            return
        font = self.game.assets.font(22)
        lines = len(self.text) // 36 + 1
        self.rect.height = 50 + lines * font.get_linesize()
        draw_panel(screen, self.rect, fill=(255, 250, 205), edge=(230, 170, 40), radius=16)
        draw_text(screen, "Coral whispers:", self.game.assets.font(18, bold=True), (150, 100, 20),
                  (self.rect.left + 16, self.rect.top + 10))
        draw_text(screen, self.text, font, INK, (self.rect.left + 16, self.rect.top + 34),
                  max_width=self.rect.width - 32)
