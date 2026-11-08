"""Click the three shells to change their colours until they match the pattern on
the chest. Three wrong checks and the shells politely solve themselves."""
import random
import pygame

from .base_minigame import BaseMinigame
from ..engine.ui import Button


class ShellPuzzle(BaseMinigame):
    id = "shell_puzzle"

    def setup(self):
        self.colors = [tuple(c) for c in self.info.get("colors", [[255, 120, 120], [120, 200, 255], [255, 230, 120]])]
        self.target = [random.randrange(len(self.colors)) for _ in range(3)]
        self.current = [random.randrange(len(self.colors)) for _ in range(3)]
        if self.current == self.target:
            self.current[0] = (self.current[0] + 1) % len(self.colors)
        self.shell_rects = [pygame.Rect(self.area.centerx - 260 + i * 200, self.area.top + 290, 140, 120) for i in range(3)]
        self.check_button = Button((self.area.centerx - 80, self.area.bottom - 130, 160, 50),
                                   self.info.get("check_text", "Check!"), callback=self.check)
        self.auto_timer = None

    def on_event(self, event):
        if self.auto_timer is not None:
            return True
        if self.check_button.handle_event(event):
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.shell_rects):
                if r.collidepoint(event.pos):
                    self.current[i] = (self.current[i] + 1) % len(self.colors)
                    self.game.audio.play("click")
        return True

    def check(self):
        if self.current == self.target:
            self.say(self.info.get("win_text", "It matches!"), 1.0)
            self.finish()
        else:
            self.fail()
            if self.fails >= 3:
                self.say(self.info.get("auto_text", "The shells wiggle... and sort themselves out!"), 2.0)
                self.current = list(self.target)
                self.auto_timer = 1.6

    def on_update(self, dt):
        if self.auto_timer is not None:
            self.auto_timer -= dt
            if self.auto_timer <= 0:
                self.finish()

    def _shell(self, screen, rect, color, small=False):
        pygame.draw.ellipse(screen, color, rect)
        dark = tuple(max(0, c - 70) for c in color)
        pygame.draw.ellipse(screen, dark, rect, 3)
        for i in range(1, 5):
            pygame.draw.line(screen, dark, rect.midbottom, (rect.left + rect.w * i / 5, rect.top + 6), 2)

    def on_draw(self, screen):
        font = self.game.assets.font(22)
        lbl = font.render(self.info.get("pattern_text", "Match this pattern:"), True, (60, 70, 100))
        screen.blit(lbl, lbl.get_rect(center=(self.area.centerx, self.area.top + 130)))
        for i, t in enumerate(self.target):
            r = pygame.Rect(self.area.centerx - 150 + i * 110, self.area.top + 160, 80, 70)
            self._shell(screen, r, self.colors[t])
        for i, r in enumerate(self.shell_rects):
            self._shell(screen, r, self.colors[self.current[i]])
            hint = font.render("click", True, (120, 130, 150))
            screen.blit(hint, hint.get_rect(midtop=(r.centerx, r.bottom + 6)))
        if self.auto_timer is None:
            self.check_button.draw(screen, self.game.assets.font(26))
