import math
import pygame
from .base_scene import BaseScene


class SunkenShip(BaseScene):
    """Dust motes drift through light from the portholes."""

    def draw_ambient(self, screen):
        for i in range(30):
            x = (i * 97 + self.time * 12 * (1 + i % 3)) % 1280
            y = 80 + (i * 53 + math.sin(self.time + i) * 20) % 540
            pygame.draw.circle(screen, (240, 230, 190), (int(x), int(y)), 2)
