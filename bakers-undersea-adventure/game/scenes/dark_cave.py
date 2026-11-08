import math
import pygame
from .base_scene import BaseScene
from ..engine.config import WIDTH, PLAY_H


class DarkCave(BaseScene):
    """Dark until lit: a lantern gives a big warm circle, the bubble helmet a smaller
    blue one. Bioluminescent spots always glow so the screen is never pitch black."""

    def draw_front(self, screen):
        state = self.game.state
        dark = pygame.Surface((WIDTH, PLAY_H), pygame.SRCALPHA)
        dark.fill((0, 5, 20, 215))
        px, py = int(self.game.player.pos[0]), int(self.game.player.pos[1] - 30)
        if state.inventory.has("lantern"):
            radius, color = 380, (255, 220, 150)
        elif state.inventory.has("bubble_helmet"):
            radius, color = 300, (150, 220, 255)
        else:
            radius, color = 120, (120, 160, 200)
        pulse = int(math.sin(self.time * 3) * 8)
        for r, a in ((radius + pulse, 215), (int(radius * 0.7), 150), (int(radius * 0.4), 80)):
            pygame.draw.circle(dark, (0, 0, 0, 0), (px, py), r)
        # Bill is never invisible: glow-worms perch on him, brighter once you're friends
        bill_alpha = 60 if (state.has_flag("found_bill") or state.has_flag("shell_freed")) else 140
        pygame.draw.ellipse(dark, (0, 5, 20, bill_alpha), (540, 130, 620, 360))
        pygame.draw.circle(dark, (0, 0, 0, 0), (px, py), radius + pulse)
        screen.blit(dark, (0, 0))
        glow = pygame.Surface((WIDTH, PLAY_H), pygame.SRCALPHA)
        for i in range(26):
            x = (i * 151) % WIDTH
            y = 40 + (i * 83) % 560
            a = int(120 + 100 * math.sin(self.time * 2 + i))
            pygame.draw.circle(glow, (120, 255, 220, max(30, a)), (x, y), 4 + i % 3)
        screen.blit(glow, (0, 0))
