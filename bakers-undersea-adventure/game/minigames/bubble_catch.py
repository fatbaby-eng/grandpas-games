"""Move the net left/right (mouse or arrow keys) and catch 5 bubbles in a row.
Bubbles come out of Mr. Puffer's machine shaped like silly things."""
import random
import pygame

from .base_minigame import BaseMinigame


class BubbleCatch(BaseMinigame):
    id = "bubble_catch"
    GOAL = 5

    def setup(self):
        self.net = pygame.Rect(0, self.area.top + 120, 150, 40)
        self.net.centerx = self.area.centerx
        self.bubbles = []
        self.streak = 0
        self.spawn_timer = 0.0
        self.shapes = self.info.get("shapes", ["bubble"])
        self.keys = 0

    def on_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.net.centerx = event.pos[0]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.keys = -1
            elif event.key == pygame.K_RIGHT:
                self.keys = 1
        elif event.type == pygame.KEYUP and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.keys = 0
        return True

    def on_update(self, dt):
        self.net.centerx += self.keys * 500 * dt
        self.net.clamp_ip(self.area)
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = random.uniform(0.9, 1.4)
            self.bubbles.append({
                "x": random.uniform(self.area.left + 80, self.area.right - 80),
                "y": self.area.bottom - 40, "vy": random.uniform(140, 220), "phase": random.uniform(0, 6),
                "r": random.randint(26, 40), "label": random.choice(self.shapes), "caught": False,
            })
        for b in self.bubbles:
            b["y"] -= b["vy"] * dt
            b["x"] += 40 * dt * (1 if int(self.time * 2 + b["phase"]) % 2 else -1)
            if not b["caught"] and self.net.collidepoint(b["x"], b["y"]):
                b["caught"] = True
                self.streak += 1
                self.game.audio.play("pickup")
                self.say(self.info.get("catch_text", "{label}!").format(label=b["label"]), 0.8)
                if self.streak >= self.GOAL:
                    self.finish()
            elif not b["caught"] and b["y"] < self.net.top - 10:
                b["caught"] = True
                if self.streak > 0:
                    self.streak = 0
                    self.fail()
        self.bubbles = [b for b in self.bubbles if b["y"] > self.area.top + 60 and not (b["caught"] and b["y"] < self.net.bottom)]

    def on_draw(self, screen):
        font = self.game.assets.font(26, bold=True)
        txt = font.render(f"Caught in a row: {self.streak} / {self.GOAL}", True, (30, 60, 120))
        screen.blit(txt, (self.area.left + 24, self.area.top + 20))
        pygame.draw.rect(screen, (255, 200, 90), self.net, border_radius=12)
        pygame.draw.rect(screen, (120, 80, 20), self.net, 3, border_radius=12)
        for i in range(1, 6):
            pygame.draw.line(screen, (120, 80, 20), (self.net.left + i * 25, self.net.top), (self.net.left + i * 25, self.net.bottom), 1)
        small = self.game.assets.font(18)
        for b in self.bubbles:
            if b["caught"]:
                continue
            pygame.draw.circle(screen, (180, 230, 255), (int(b["x"]), int(b["y"])), b["r"])
            pygame.draw.circle(screen, (90, 160, 220), (int(b["x"]), int(b["y"])), b["r"], 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(b["x"] - b["r"] * 0.4), int(b["y"] - b["r"] * 0.4)), b["r"] // 5)
            lbl = small.render(b["label"], True, (20, 40, 80))
            screen.blit(lbl, lbl.get_rect(center=(int(b["x"]), int(b["y"]))))
