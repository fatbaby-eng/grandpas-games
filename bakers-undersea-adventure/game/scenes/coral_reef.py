import math
import pygame
from .base_scene import BaseScene


class CoralReef(BaseScene):
    """Hub scene: swaying anemone fronds along the sea floor."""

    def draw_ambient(self, screen):
        for i in range(9):
            x = 60 + i * 140
            sway = math.sin(self.time * 2 + i) * 8
            for k in range(5):
                pygame.draw.line(screen, (255, 120 + k * 20, 170), (x + k * 7, 630),
                                 (x + k * 7 + sway, 580 - k * 4), 5)
