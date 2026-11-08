"""Click the glowing note. Eight notes, no way to lose: a wrong click just wobbles."""
import math
import random
import pygame

from .base_minigame import BaseMinigame


class DJBeat(BaseMinigame):
    id = "dj_beat"
    COUNT = 8

    def setup(self):
        self.notes = [pygame.Rect(self.area.left + 90 + i * 135, self.area.top + 250, 100, 100) for i in range(self.COUNT)]
        self.colors = [((80 + i * 23) % 256, (160 + i * 41) % 256, (220 - i * 17) % 256) for i in range(self.COUNT)]
        self.order = list(range(self.COUNT))
        random.shuffle(self.order)
        self.index = 0
        self.wobble = {}

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.notes):
                if r.collidepoint(event.pos):
                    if i == self.order[self.index]:
                        self.index += 1
                        self.game.audio.play("pickup")
                        if self.index >= self.COUNT:
                            self.say(self.info.get("win_text", "What a beat!"), 1.0)
                            self.finish()
                    else:
                        self.wobble[i] = 0.4
                        self.game.audio.play("click")
        return True

    def on_update(self, dt):
        for k in list(self.wobble):
            self.wobble[k] -= dt
            if self.wobble[k] <= 0:
                del self.wobble[k]

    def on_draw(self, screen):
        font = self.game.assets.font(24, bold=True)
        lbl = font.render(f"{self.info.get('progress_text', 'Notes')}  {self.index} / {self.COUNT}", True, (30, 60, 120))
        screen.blit(lbl, lbl.get_rect(center=(self.area.centerx, self.area.top + 130)))
        dj = self.game.assets.character("dj", 220, 150, int(self.time * 60), talking=True)
        screen.blit(dj, dj.get_rect(midtop=(self.area.centerx, self.area.top + 380)))
        for i, r in enumerate(self.notes):
            rect = r.copy()
            if i in self.wobble:
                rect.x += int(math.sin(self.time * 40) * 6)
            lit = self.index < self.COUNT and self.order[self.index] == i
            done = i in self.order[:self.index]
            color = self.colors[i] if not done else (200, 200, 200)
            if lit:
                glow = pygame.Surface((rect.w + 40, rect.h + 40), pygame.SRCALPHA)
                a = int(120 + 100 * math.sin(self.time * 8))
                pygame.draw.circle(glow, (255, 255, 160, a), (rect.w // 2 + 20, rect.h // 2 + 20), rect.w // 2 + 18)
                screen.blit(glow, (rect.x - 20, rect.y - 20))
            pygame.draw.circle(screen, color, rect.center, rect.w // 2)
            pygame.draw.circle(screen, (40, 40, 60), rect.center, rect.w // 2, 3)
            note = self.game.assets.font(48).render("♪", True, (20, 20, 40))
            screen.blit(note, note.get_rect(center=rect.center))
