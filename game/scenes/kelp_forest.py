import math
import pygame
from .base_scene import BaseScene


class KelpForest(BaseScene):
    """Tall kelp strands sway in the foreground."""

    def draw_front(self, screen):
        layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(7):
            x = 30 + i * 190
            pts = []
            for seg in range(9):
                y = 640 - seg * 70
                pts.append((x + math.sin(self.time * 1.5 + i + seg * 0.5) * (6 + seg * 3), y))
            pygame.draw.lines(layer, (30, 120, 60, 120), False, pts, 14)
        screen.blit(layer, (0, 0))
