"""Procedurally drawn placeholder art.

Everything here is a stand-in: when a real PNG with the expected filename is
dropped into assets/images it is used instead (see assets.py). Shapes are
deliberately simple, bright and friendly.
"""
import math
import random

import pygame

from .config import WIDTH, PLAY_H


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, top, bottom):
    surf = pygame.Surface(size)
    w, h = size
    for y in range(h):
        pygame.draw.line(surf, _lerp(top, bottom, y / max(1, h - 1)), (0, y), (w, y))
    return surf


def background(scene: dict) -> pygame.Surface:
    """Draw a background from the scene's `palette` entry in scenes.json."""
    pal = scene.get("palette", {})
    top = tuple(pal.get("top", (30, 110, 170)))
    bottom = tuple(pal.get("bottom", (10, 50, 90)))
    floor = tuple(pal.get("floor", (210, 190, 140)))
    accent = tuple(pal.get("accent", (255, 120, 150)))
    rng = random.Random(scene.get("id", "scene"))

    surf = gradient((WIDTH, PLAY_H), top, bottom)
    # light rays
    ray = pygame.Surface((WIDTH, PLAY_H), pygame.SRCALPHA)
    for i in range(6):
        x = rng.randint(0, WIDTH)
        pygame.draw.polygon(ray, (255, 255, 255, 18),
                            [(x, 0), (x + 60, 0), (x + 220, PLAY_H), (x + 40, PLAY_H)])
    surf.blit(ray, (0, 0))
    # sea floor
    floor_y = scene.get("floor_y", 400)
    pts = [(0, PLAY_H), (0, floor_y + 30)]
    for x in range(0, WIDTH + 80, 80):
        pts.append((x, floor_y + rng.randint(-20, 20)))
    pts.append((WIDTH, PLAY_H))
    pygame.draw.polygon(surf, floor, pts)
    # decorative blobs (coral / rocks / kelp depending on style)
    style = scene.get("style", "reef")
    for i in range(14):
        x = rng.randint(0, WIDTH)
        y = rng.randint(floor_y, PLAY_H)
        if style == "kelp":
            for k in range(5):
                kx = x + k * 6
                pygame.draw.line(surf, (40, 150 + rng.randint(0, 60), 60), (kx, y),
                                 (kx + rng.randint(-30, 30), y - rng.randint(200, 420)), 8)
        elif style == "cave":
            pygame.draw.circle(surf, _lerp(bottom, (0, 0, 0), 0.4), (x, y), rng.randint(20, 70))
        elif style == "ship":
            pygame.draw.rect(surf, _lerp(floor, (60, 40, 20), 0.5), (x, y, rng.randint(40, 120), 14))
        elif style == "festival":
            pygame.draw.circle(surf, (rng.randint(120, 255), rng.randint(120, 255), rng.randint(120, 255)),
                               (x, rng.randint(40, 300)), rng.randint(14, 26))
        else:
            c = (rng.randint(180, 255), rng.randint(60, 160), rng.randint(90, 200))
            pygame.draw.circle(surf, c, (x, y), rng.randint(18, 48))
            pygame.draw.circle(surf, accent, (x + 10, y - 10), rng.randint(6, 14))
    return surf


def character(char: dict, w: int, h: int, frame: int = 0, facing: str = "right",
              talking: bool = False) -> pygame.Surface:
    """Draw a cartoon creature. `char["shape"]` selects the silhouette."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    color = tuple(char.get("color", (255, 180, 60)))
    dark = _lerp(color, (0, 0, 0), 0.35)
    light = _lerp(color, (255, 255, 255), 0.4)
    shape = char.get("shape", "fish")
    bob = int(math.sin(frame * 0.4) * h * 0.03)
    cx, cy = w // 2, h // 2 + bob
    eye_open = not (frame % 40 in (0, 1))

    if shape == "fish":
        body = pygame.Rect(0, 0, int(w * 0.62), int(h * 0.55)); body.center = (cx, cy)
        pygame.draw.ellipse(surf, color, body)
        pygame.draw.polygon(surf, dark, [(body.left + 6, cy), (0, cy - h * 0.25), (0, cy + h * 0.25)])
        pygame.draw.polygon(surf, light, [(cx - 10, body.top + 4), (cx + 8, body.top - h * 0.18), (cx + 16, body.top + 6)])
        pygame.draw.ellipse(surf, light, (body.left + body.w * 0.35, cy, body.w * 0.5, body.h * 0.4))
        eye = (body.right - body.w * 0.28, cy - body.h * 0.15)
    elif shape == "seahorse":
        pygame.draw.ellipse(surf, color, (cx - w * 0.18, h * 0.08, w * 0.36, h * 0.3))
        pygame.draw.rect(surf, color, (cx - w * 0.1, h * 0.3, w * 0.28, h * 0.5), border_radius=14)
        pygame.draw.arc(surf, dark, (cx - w * 0.25, h * 0.62, w * 0.4, h * 0.35), 3.4, 6.2, 8)
        pygame.draw.rect(surf, dark, (cx + w * 0.14, h * 0.17, w * 0.25, h * 0.06))
        for i in range(5):
            pygame.draw.polygon(surf, light, [(cx - 6 + i, h * 0.3 + i * h * 0.1), (cx - 22, h * 0.34 + i * h * 0.1), (cx - 4, h * 0.38 + i * h * 0.1)])
        eye = (cx + w * 0.04, h * 0.2)
    elif shape == "grouper":
        body = pygame.Rect(0, 0, int(w * 0.8), int(h * 0.7)); body.center = (cx, cy)
        pygame.draw.ellipse(surf, color, body)
        pygame.draw.polygon(surf, dark, [(body.left + 8, cy), (0, cy - h * 0.3), (0, cy + h * 0.3)])
        for i in range(5):
            pygame.draw.circle(surf, dark, (body.left + 30 + i * 22, cy + (i % 2) * 14), 5)
        pygame.draw.arc(surf, dark, (body.right - 40, cy + 6, 30, 20), 3.3, 6.1, 3)  # smile
        # spectacles
        eye = (body.right - body.w * 0.25, cy - body.h * 0.2)
        pygame.draw.circle(surf, (240, 240, 240), (int(eye[0]), int(eye[1])), 12, 2)
    elif shape == "puffer":
        r = int(min(w, h) * 0.4)
        pygame.draw.circle(surf, color, (cx, cy), r)
        for a in range(0, 360, 30):
            x = cx + math.cos(math.radians(a)) * r; y = cy + math.sin(math.radians(a)) * r
            pygame.draw.line(surf, dark, (x, y), (x + math.cos(math.radians(a)) * 10, y + math.sin(math.radians(a)) * 10), 3)
        pygame.draw.polygon(surf, dark, [(cx - r, cy), (cx - r - 18, cy - 14), (cx - r - 18, cy + 14)])
        pygame.draw.line(surf, dark, (cx + r * 0.3, cy + r * 0.35), (cx + r * 0.6, cy + r * 0.3), 3)
        eye = (cx + r * 0.4, cy - r * 0.3)
    elif shape == "turtle":
        pygame.draw.ellipse(surf, dark, (w * 0.15, h * 0.2, w * 0.6, h * 0.55))
        pygame.draw.ellipse(surf, color, (w * 0.2, h * 0.25, w * 0.5, h * 0.42))
        for i in range(3):
            pygame.draw.circle(surf, dark, (int(w * 0.3 + i * w * 0.15), int(h * 0.45)), 7, 2)
        pygame.draw.ellipse(surf, light, (w * 0.68, h * 0.3, w * 0.26, h * 0.26))
        pygame.draw.ellipse(surf, light, (w * 0.1, h * 0.6, w * 0.18, h * 0.12))
        pygame.draw.ellipse(surf, light, (w * 0.6, h * 0.62, w * 0.18, h * 0.12))
        eye = (w * 0.84, h * 0.4)
    elif shape == "clam":
        pygame.draw.ellipse(surf, dark, (w * 0.1, h * 0.45, w * 0.8, h * 0.4))
        pygame.draw.ellipse(surf, color, (w * 0.1, h * 0.2 + (6 if talking else 0), w * 0.8, h * 0.4))
        for i in range(6):
            pygame.draw.line(surf, light, (cx, h * 0.42), (w * 0.15 + i * w * 0.14, h * 0.22), 2)
        # captain's hat
        pygame.draw.rect(surf, (30, 40, 80), (cx - 26, h * 0.08, 52, 16), border_radius=4)
        pygame.draw.rect(surf, (30, 40, 80), (cx - 36, h * 0.2, 72, 8))
        eye = (cx + 18, h * 0.33 + (6 if talking else 0))
    elif shape == "whale":
        body = pygame.Rect(0, int(h * 0.15), int(w * 0.85), int(h * 0.6))
        pygame.draw.ellipse(surf, color, body)
        pygame.draw.polygon(surf, color, [(body.right - 20, cy), (w, h * 0.1), (w, h * 0.5)])
        pygame.draw.ellipse(surf, light, (body.left + body.w * 0.1, cy, body.w * 0.6, body.h * 0.45))
        for i in range(4):
            pygame.draw.circle(surf, (200, 200, 200), (body.left + 40 + i * 50, body.top + 30 + (i % 2) * 20), 6)
        pygame.draw.arc(surf, dark, (body.left + 10, cy, 120, 40), 3.4, 6.0, 4)
        eye = (body.left + body.w * 0.12, cy - body.h * 0.22)
    elif shape == "dolphin":
        body = pygame.Rect(0, 0, int(w * 0.7), int(h * 0.42)); body.center = (cx, cy)
        pygame.draw.ellipse(surf, color, body)
        pygame.draw.polygon(surf, color, [(cx - 6, body.top + 6), (cx + 20, body.top - h * 0.22), (cx + 30, body.top + 8)])
        pygame.draw.polygon(surf, color, [(body.left + 8, cy), (0, cy - h * 0.2), (0, cy + h * 0.2)])
        pygame.draw.ellipse(surf, light, (body.left + body.w * 0.3, cy, body.w * 0.6, body.h * 0.4))
        pygame.draw.ellipse(surf, color, (body.right - 16, cy - 10, 30, 20))  # beak
        # headphones
        pygame.draw.arc(surf, (40, 40, 40), (body.right - 70, body.top - 10, 60, 50), 0.2, 3.0, 6)
        eye = (body.right - body.w * 0.25, cy - body.h * 0.2)
    elif shape == "crab":
        pygame.draw.ellipse(surf, color, (w * 0.2, h * 0.35, w * 0.6, h * 0.4))
        for i, side in enumerate((-1, 1)):
            for j in range(3):
                y = h * 0.5 + j * h * 0.12
                x0 = cx + side * w * 0.28
                pygame.draw.line(surf, dark, (x0, y), (x0 + side * w * 0.18, y + h * 0.12), 4)
            px = cx + side * w * 0.42
            pygame.draw.circle(surf, color, (int(px), int(h * 0.3)), int(w * 0.1))
        pygame.draw.line(surf, dark, (cx - 10, h * 0.6), (cx + 10, h * 0.6), 2)
        eye = (cx - 10, h * 0.33)
        pygame.draw.circle(surf, (255, 255, 255), (cx + 10, int(h * 0.33)), 6)
        pygame.draw.circle(surf, (0, 0, 0), (cx + 10, int(h * 0.33)), 3)
    else:  # generic blob
        pygame.draw.ellipse(surf, color, (w * 0.1, h * 0.1, w * 0.8, h * 0.8))
        eye = (w * 0.65, h * 0.4)

    ex, ey = int(eye[0]), int(eye[1])
    if eye_open:
        pygame.draw.circle(surf, (255, 255, 255), (ex, ey), 7)
        pygame.draw.circle(surf, (0, 0, 0), (ex + 2, ey), 3)
    else:
        pygame.draw.line(surf, (0, 0, 0), (ex - 6, ey), (ex + 6, ey), 2)
    if talking and frame % 20 < 10:
        pygame.draw.circle(surf, (40, 20, 20), (ex + 2, ey + 18), 5)

    if facing == "left":
        surf = pygame.transform.flip(surf, True, False)
    return surf


def icon(item: dict, size: int = 48) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    color = tuple(item.get("color", (230, 200, 90)))
    pygame.draw.circle(surf, _lerp(color, (0, 0, 0), 0.3), (size // 2, size // 2), size // 2 - 2)
    pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2 - 6)
    pygame.draw.circle(surf, _lerp(color, (255, 255, 255), 0.5), (size // 2 - 8, size // 2 - 8), size // 8)
    font = pygame.font.Font(None, size // 2 + 4)
    glyph = font.render(item.get("glyph", item.get("name", "?")[0]), True, (20, 20, 20))
    surf.blit(glyph, glyph.get_rect(center=(size // 2, size // 2 + 1)))
    return surf


def prop(hotspot: dict, w: int, h: int) -> pygame.Surface:
    """A labelled blob for objects / humour hotspots so kids can see them."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    color = tuple(hotspot.get("color", (200, 170, 120)))
    kind = hotspot.get("prop", "blob")
    if kind == "rect":
        pygame.draw.rect(surf, color, (2, 2, w - 4, h - 4), border_radius=10)
        pygame.draw.rect(surf, _lerp(color, (0, 0, 0), 0.3), (2, 2, w - 4, h - 4), 3, border_radius=10)
    elif kind == "arrow":
        pygame.draw.polygon(surf, color, [(w * 0.1, h * 0.35), (w * 0.6, h * 0.35), (w * 0.6, h * 0.15),
                                          (w * 0.95, h * 0.5), (w * 0.6, h * 0.85), (w * 0.6, h * 0.65), (w * 0.1, h * 0.65)])
    elif kind == "none":
        return surf
    else:
        pygame.draw.ellipse(surf, color, (2, 2, w - 4, h - 4))
        pygame.draw.ellipse(surf, _lerp(color, (0, 0, 0), 0.3), (2, 2, w - 4, h - 4), 3)
    label = hotspot.get("label")
    if label:
        font = pygame.font.Font(None, 20)
        text = font.render(label, True, (20, 20, 30))
        bg = pygame.Surface((text.get_width() + 8, text.get_height() + 4), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 170))
        r = bg.get_rect(center=(w // 2, h // 2))
        surf.blit(bg, r)
        surf.blit(text, text.get_rect(center=r.center))
    return surf
