"""Custom cursors: arrow (walk), hand (interact), eye (examine), talk (speech bubble),
exit (door arrow) and item (the selected inventory icon)."""
import pygame

WHITE = (255, 255, 255)
BLACK = (20, 20, 30)


def _arrow():
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    pts = [(2, 2), (2, 26), (9, 20), (14, 30), (19, 28), (14, 18), (24, 18)]
    pygame.draw.polygon(s, WHITE, pts)
    pygame.draw.polygon(s, BLACK, pts, 2)
    return s, (2, 2)


def _hand():
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(s, WHITE, (8, 12, 18, 16), border_radius=6)
    for i in range(4):
        pygame.draw.rect(s, WHITE, (8 + i * 5, 2 + (0 if i else 6), 4, 14), border_radius=2)
    pygame.draw.rect(s, BLACK, (8, 12, 18, 16), 2, border_radius=6)
    pygame.draw.rect(s, WHITE, (3, 16, 7, 6), border_radius=2)
    return s, (14, 4)


def _eye():
    s = pygame.Surface((36, 24), pygame.SRCALPHA)
    pygame.draw.ellipse(s, WHITE, (2, 4, 32, 16))
    pygame.draw.ellipse(s, BLACK, (2, 4, 32, 16), 2)
    pygame.draw.circle(s, (60, 140, 220), (18, 12), 6)
    pygame.draw.circle(s, BLACK, (18, 12), 3)
    return s, (18, 12)


def _talk():
    s = pygame.Surface((36, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(s, WHITE, (2, 2, 32, 22))
    pygame.draw.polygon(s, WHITE, [(8, 20), (6, 30), (16, 22)])
    pygame.draw.ellipse(s, BLACK, (2, 2, 32, 22), 2)
    for x in (11, 18, 25):
        pygame.draw.circle(s, BLACK, (x, 13), 2)
    return s, (6, 30)


def _exit():
    s = pygame.Surface((36, 32), pygame.SRCALPHA)
    pts = [(2, 10), (20, 10), (20, 2), (34, 16), (20, 30), (20, 22), (2, 22)]
    pygame.draw.polygon(s, (120, 255, 160), pts)
    pygame.draw.polygon(s, BLACK, pts, 2)
    return s, (18, 16)


class CursorManager:
    KINDS = ("arrow", "hand", "eye", "talk", "exit", "item")

    def __init__(self):
        self.surfaces = {
            "arrow": _arrow(), "hand": _hand(), "eye": _eye(), "talk": _talk(), "exit": _exit(),
        }
        self.kind = "arrow"
        self.item_surface = None
        self.visible = True
        pygame.mouse.set_visible(False)

    def set(self, kind: str):
        if kind in self.surfaces or kind == "item":
            self.kind = kind

    def set_item_icon(self, surface: pygame.Surface | None):
        self.item_surface = surface

    def draw(self, screen):
        if not self.visible or not pygame.mouse.get_focused():
            return
        pos = pygame.mouse.get_pos()
        if self.kind == "item" and self.item_surface is not None:
            icon = self.item_surface
            screen.blit(icon, icon.get_rect(center=pos))
            small, hot = self.surfaces["hand"]
            screen.blit(small, (pos[0] - 8, pos[1] - 8))
            return
        surf, hot = self.surfaces.get(self.kind, self.surfaces["arrow"])
        screen.blit(surf, (pos[0] - hot[0], pos[1] - hot[1]))
