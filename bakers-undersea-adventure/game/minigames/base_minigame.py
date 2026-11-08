"""Shared frame for the four mini-games: title, instructions, a Skip button that
appears after 30 seconds or 3 failed attempts, and a finish hook. None of them
can be lost; the worst case is a skip, which still grants the reward."""
import pygame

from ..engine.config import WIDTH, PLAY_H, MINIGAME_SKIP_AFTER, MINIGAME_SKIP_FAILS
from ..engine.ui import Button, draw_panel, draw_text, INK


class BaseMinigame:
    id = "base"

    def __init__(self, game, info: dict, on_complete):
        self.game = game
        self.info = info                      # title/instructions/etc from quests.json["minigames"][id]
        self.on_complete = on_complete
        self.time = 0.0
        self.fails = 0
        self.done = False
        self.message = ""
        self.message_timer = 0.0
        self.area = pygame.Rect(60, 20, WIDTH - 120, PLAY_H - 40)
        self.skip_button = Button((self.area.right - 150, self.area.top + 14, 130, 44),
                                  info.get("skip_text", "Skip"), callback=self.skip, color=(220, 220, 230), font_size=24)
        self.setup()

    # Hooks for subclasses ------------------------------------------------------
    def setup(self): ...
    def on_event(self, event) -> bool: return False
    def on_update(self, dt): ...
    def on_draw(self, screen): ...

    # Shared behaviour ----------------------------------------------------------
    def can_skip(self) -> bool:
        return self.time >= MINIGAME_SKIP_AFTER or self.fails >= MINIGAME_SKIP_FAILS

    def say(self, text, seconds=1.6):
        self.message = text
        self.message_timer = seconds

    def fail(self, text=None):
        self.fails += 1
        self.game.audio.play("bubble")
        self.say(text or self.info.get("retry_text", "Almost! Try again."))

    def skip(self):
        if self.can_skip() and not self.done:
            self.finish(skipped=True)

    def finish(self, skipped=False):
        if self.done:
            return
        self.done = True
        self.game.audio.play("success")
        self.game.end_minigame(self, skipped)

    def handle_event(self, event) -> bool:
        if self.can_skip() and self.skip_button.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.can_skip():
            self.skip()
            return True
        self.on_event(event)
        return True            # mini-games swallow everything while active

    def update(self, dt):
        self.time += dt
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
        self.on_update(dt)

    def draw(self, screen):
        shade = pygame.Surface((WIDTH, PLAY_H), pygame.SRCALPHA)
        shade.fill((0, 20, 50, 160))
        screen.blit(shade, (0, 0))
        draw_panel(screen, self.area, fill=(225, 243, 255))
        fonts = self.game.assets
        draw_text(screen, self.info.get("title", self.id), fonts.font(40, bold=True), INK,
                  (self.area.centerx, self.area.top + 16), center=True)
        draw_text(screen, self.info.get("instructions", ""), fonts.font(22), (60, 70, 100),
                  (self.area.centerx, self.area.top + 62), center=True, max_width=self.area.width - 340)
        self.on_draw(screen)
        if self.message:
            draw_text(screen, self.message, fonts.font(30, bold=True), (200, 90, 20),
                      (self.area.centerx, self.area.bottom - 60), center=True)
        if self.can_skip():
            self.skip_button.draw(screen, fonts.font(24))
        else:
            remaining = max(0, int(MINIGAME_SKIP_AFTER - self.time) + 1)
            tip = fonts.font(16).render(f"skip appears in {remaining}s", True, (120, 130, 150))
            screen.blit(tip, tip.get_rect(topright=(self.area.right - 20, self.area.top + 22)))
