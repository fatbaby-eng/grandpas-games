"""Simon-says dance: watch Sidney's four moves, then repeat them with the arrow keys
(or by clicking the arrows). A wrong move just replays the sequence."""
import random
import pygame

from .base_minigame import BaseMinigame

ARROWS = ["left", "up", "down", "right"]
KEYS = {pygame.K_LEFT: "left", pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_RIGHT: "right"}


class CrabDance(BaseMinigame):
    id = "crab_dance"

    def setup(self):
        self.sequence = [random.choice(ARROWS) for _ in range(4)]
        self.phase = "show"
        self.show_index = 0
        self.show_timer = 0.8
        self.input_index = 0
        self.flash = None
        self.flash_timer = 0.0
        self.arrow_rects = {a: pygame.Rect(self.area.centerx - 290 + i * 160, self.area.top + 330, 130, 110)
                            for i, a in enumerate(ARROWS)}
        self.crab_x = self.area.centerx

    def _press(self, direction):
        if self.phase != "input":
            return
        self.flash, self.flash_timer = direction, 0.3
        if direction == self.sequence[self.input_index]:
            self.input_index += 1
            self.game.audio.play("click")
            self.crab_x += {"left": -60, "right": 60}.get(direction, 0)
            if self.input_index >= len(self.sequence):
                self.say(self.info.get("win_text", "Perfect moves!"), 1.0)
                self.finish()
        else:
            self.fail(self.info.get("retry_text"))
            self.phase, self.show_index, self.show_timer, self.input_index = "show", 0, 1.2, 0

    def on_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in KEYS:
            self._press(KEYS[event.key])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for a, r in self.arrow_rects.items():
                if r.collidepoint(event.pos):
                    self._press(a)
        return True

    def on_update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash = None
        if self.phase == "show":
            self.show_timer -= dt
            if self.show_timer <= 0:
                if self.show_index < len(self.sequence):
                    self.flash, self.flash_timer = self.sequence[self.show_index], 0.45
                    self.game.audio.play("bubble")
                    self.show_index += 1
                    self.show_timer = 0.75
                else:
                    self.phase = "input"
                    self.say(self.info.get("your_turn_text", "Your turn!"), 1.2)

    def _draw_arrow(self, screen, rect, direction, lit):
        color = (255, 220, 90) if lit else (200, 210, 230)
        pygame.draw.rect(screen, color, rect, border_radius=16)
        pygame.draw.rect(screen, (60, 80, 120), rect, 3, border_radius=16)
        cx, cy = rect.center
        pts = {"left": [(cx - 35, cy), (cx + 20, cy - 30), (cx + 20, cy + 30)],
               "right": [(cx + 35, cy), (cx - 20, cy - 30), (cx - 20, cy + 30)],
               "up": [(cx, cy - 35), (cx - 30, cy + 20), (cx + 30, cy + 20)],
               "down": [(cx, cy + 35), (cx - 30, cy - 20), (cx + 30, cy - 20)]}[direction]
        pygame.draw.polygon(screen, (40, 60, 100), pts)

    def on_draw(self, screen):
        font = self.game.assets.font(24, bold=True)
        status = self.info.get("watch_text", "Watch Sidney...") if self.phase == "show" else \
            f"{self.info.get('repeat_text', 'Repeat the moves')}  {self.input_index} / {len(self.sequence)}"
        lbl = font.render(status, True, (30, 60, 120))
        screen.blit(lbl, lbl.get_rect(center=(self.area.centerx, self.area.top + 130)))
        crab = self.game.assets.character("sidney", 120, 80, int(self.time * 60))
        screen.blit(crab, crab.get_rect(midbottom=(int(self.crab_x), self.area.top + 290)))
        for a, r in self.arrow_rects.items():
            self._draw_arrow(screen, r, a, self.flash == a)
        tip = self.game.assets.font(18).render(self.info.get("keys_text", "Arrow keys or click the arrows"), True, (120, 130, 150))
        screen.blit(tip, tip.get_rect(center=(self.area.centerx, self.area.top + 470)))
