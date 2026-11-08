import math
import random
import pygame
from .base_scene import BaseScene
from ..engine.config import WIDTH, PLAY_H


class FestivalGrounds(BaseScene):
    """Balloons drift up; once the shell is home, confetti falls forever."""

    COLORS = [(255, 90, 90), (255, 200, 60), (90, 220, 120), (90, 160, 255), (230, 120, 255)]

    def __init__(self, game, data):
        super().__init__(game, data)
        self.confetti = [[random.uniform(0, WIDTH), random.uniform(-PLAY_H, 0), random.uniform(40, 120),
                          random.choice(self.COLORS)] for _ in range(120)]

    def update(self, dt):
        super().update(dt)
        if self.game.state.has_flag("shell_returned"):
            for c in self.confetti:
                c[1] += c[2] * dt
                c[0] += math.sin(self.time * 2 + c[1] * 0.01) * 20 * dt
                if c[1] > PLAY_H:
                    c[1] = random.uniform(-60, 0)
                    c[0] = random.uniform(0, WIDTH)

    def draw_ambient(self, screen):
        for i in range(8):
            x = 80 + i * 160 + math.sin(self.time + i) * 12
            y = 120 + (i * 37 + self.time * 15) % 260
            color = self.COLORS[i % len(self.COLORS)]
            pygame.draw.ellipse(screen, color, (x, y, 36, 46))
            pygame.draw.line(screen, (240, 240, 240), (x + 18, y + 46), (x + 18 + math.sin(self.time * 2 + i) * 6, y + 90), 2)

    def draw_front(self, screen):
        if self.game.state.has_flag("shell_returned"):
            for x, y, _, color in self.confetti:
                pygame.draw.rect(screen, color, (int(x), int(y), 7, 11))
