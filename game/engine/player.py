"""Baker: the player sprite. Walks in straight lines toward click targets."""
import math

import pygame

from .config import PLAYER_SPEED


class Player:
    W, H = 110, 70

    def __init__(self, pos=(640, 520)):
        self.pos = [float(pos[0]), float(pos[1])]   # feet / anchor point
        self.target = None
        self.on_arrive = None
        self.facing = "right"
        self.frame = 0
        self.speed = PLAYER_SPEED

    @property
    def moving(self) -> bool:
        return self.target is not None

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos[0] - self.W / 2), int(self.pos[1] - self.H), self.W, self.H)

    def teleport(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.target = None
        self.on_arrive = None

    def set_target(self, pos, on_arrive=None):
        self.target = (float(pos[0]), float(pos[1]))
        self.on_arrive = on_arrive
        if abs(self.target[0] - self.pos[0]) > 4:
            self.facing = "right" if self.target[0] > self.pos[0] else "left"

    def stop(self):
        self.target = None
        self.on_arrive = None

    def update(self, dt):
        self.frame += 1
        if self.target is None:
            return
        dx = self.target[0] - self.pos[0]
        dy = self.target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        step = self.speed * dt
        if dist <= step:
            self.pos = [self.target[0], self.target[1]]
            self.target = None
            cb, self.on_arrive = self.on_arrive, None
            if cb:
                cb()
        else:
            self.pos[0] += dx / dist * step
            self.pos[1] += dy / dist * step

    def draw(self, screen, assets, talking=False):
        bob = math.sin(self.frame * (0.25 if self.moving else 0.08)) * (4 if self.moving else 2)
        sprite = assets.character("baker", self.W, self.H, self.frame, self.facing, talking)
        rect = sprite.get_rect(midbottom=(int(self.pos[0]), int(self.pos[1] + bob)))
        screen.blit(sprite, rect)
