"""Generic data-driven scene. Everything a scene shows or does comes from its
entry in scenes.json; subclasses only add ambient visuals.

Hotspot schema (all optional keys marked with ?):
    id, type: npc | item | humor | exit | object
    rect: [x, y, w, h]
    walk_to?: [x, y]        Baker walks here before interacting
    visible_if? / hidden_if?: condition
    label?, color?, prop?: rect|blob|arrow|none, image?, draw?: bool
    npc:    character, dialogue: id | [{"if": cond, "id": ...}], counter?
    item:   item (item id), pickup_flag? (defaults to picked_<id>)
    humor:  text: str | [str], speaker?, sound?, actions?
    exit:   to, spawn?, requires?: cond, blocked?: [actions]
    object: on_click?: [actions], dialogue?: id|[...], examine?: str
    any:    use?: {item_id | "*": [actions] | {"actions": [...], "consume": bool}}
"""
import math
import random

import pygame

from ..engine.conditions import check, pick
from ..engine.config import WIDTH, PLAY_H


class Scene:
    def on_enter(self): ...
    def on_exit(self): ...
    def handle_event(self, event) -> bool: return False
    def update(self, dt): ...
    def draw(self, screen): ...


def _point_in_poly(pt, poly) -> bool:
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1
            if x < xin:
                inside = not inside
    return inside


def _closest_on_segment(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return a
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return (ax + t * dx, ay + t * dy)


def clamp_to_poly(pt, poly):
    if _point_in_poly(pt, poly):
        return pt
    best, best_d = pt, float("inf")
    for i in range(len(poly)):
        c = _closest_on_segment(pt, poly[i], poly[(i + 1) % len(poly)])
        d = (c[0] - pt[0]) ** 2 + (c[1] - pt[1]) ** 2
        if d < best_d:
            best, best_d = c, d
    return best


class Particle:
    def __init__(self, x, y, vx, vy, life, radius, color):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max_life = life
        self.radius = radius
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, screen):
        alpha = max(0, int(255 * self.life / self.max_life))
        s = pygame.Surface((self.radius * 2 + 2, self.radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.radius + 1, self.radius + 1), self.radius, 2)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))


class BaseScene(Scene):
    def __init__(self, game, data: dict):
        self.game = game
        self.data = data
        self.id = data["id"]
        self.walkable = [tuple(p) for p in data.get("walkable", [[0, 380], [WIDTH, 380], [WIDTH, PLAY_H - 10], [0, PLAY_H - 10]])]
        self.particles: list[Particle] = []
        self.time = 0.0
        self.hover = None
        self.talking_to = None
        self.debug = False
        self._rng = random.Random(self.id)

    # Lifecycle ----------------------------------------------------------------
    def on_enter(self):
        self.game.audio.music(self.data.get("music", "underwater"))
        self.game.actions.run(self.data.get("on_enter"))
        for entry in self.data.get("on_enter_once", []):
            flag = entry.get("flag")
            if flag and not self.game.state.has_flag(flag) and check(entry.get("if"), self.game.state):
                self.game.state.set_flag(flag)
                self.game.actions.run(entry.get("actions"))
                break

    def on_exit(self):
        self.talking_to = None
        self.game.player.stop()

    # Hotspots -------------------------------------------------------------------
    def visible_hotspots(self) -> list[dict]:
        state = self.game.state
        out = []
        for hs in self.data.get("hotspots", []):
            if hs.get("type") == "item":
                flag = hs.get("pickup_flag", f"picked_{hs['id']}")
                if state.has_flag(flag) or state.inventory.has(hs["item"]):
                    continue
            if not check(hs.get("visible_if"), state):
                continue
            if "hidden_if" in hs and check(hs["hidden_if"], state):
                continue
            out.append(hs)
        return out

    def hotspot_at(self, pos):
        for hs in reversed(self.visible_hotspots()):
            if pygame.Rect(hs["rect"]).collidepoint(pos):
                return hs
        return None

    def hotspot_by_id(self, hs_id):
        for hs in self.data.get("hotspots", []):
            if hs["id"] == hs_id:
                return hs
        return None

    @staticmethod
    def cursor_for(hs) -> str:
        if hs is None:
            return "arrow"
        return {"npc": "talk", "item": "hand", "humor": "eye", "exit": "exit", "object": "hand"}.get(hs.get("type"), "hand")

    # Events ---------------------------------------------------------------------
    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if event.pos[1] < PLAY_H:
                self.hover = self.hotspot_at(event.pos)
                if self.game.state.inventory.selected_item():
                    self.game.cursor.set("item")
                else:
                    self.game.cursor.set(self.cursor_for(self.hover))
            else:
                self.hover = None
                self.game.cursor.set("arrow")
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.debug = not self.debug
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] < PLAY_H:
            if event.button == 1:
                self.click(event.pos)
                return True
            if event.button == 3:
                self.game.state.inventory.deselect()
                self.game.cursor.set(self.cursor_for(self.hotspot_at(event.pos)))
                return True
        return False

    def click(self, pos):
        if self.game.scenes.transitioning:
            return
        player = self.game.player
        inv = self.game.state.inventory
        selected = inv.selected_item()
        hs = self.hotspot_at(pos)
        self.talking_to = None
        if hs is None:
            if selected:
                inv.deselect()
                self.game.cursor.set("arrow")
                return
            player.set_target(clamp_to_poly(pos, self.walkable))
            return
        walk_to = hs.get("walk_to")
        if walk_to and (abs(player.pos[0] - walk_to[0]) > 3 or abs(player.pos[1] - walk_to[1]) > 3):
            player.set_target(walk_to, on_arrive=lambda: self.interact(hs, selected))
        else:
            if hs.get("type") != "exit":
                player.facing = "right" if pygame.Rect(hs["rect"]).centerx >= player.pos[0] else "left"
            self.interact(hs, selected)

    # Interaction ----------------------------------------------------------------
    def interact(self, hs: dict, item: str | None):
        g = self.game
        state = g.state
        if hs not in self.visible_hotspots():
            return
        if item:
            state.inventory.deselect()
            g.cursor.set(self.cursor_for(hs))
            self._use_item(hs, item)
            return
        kind = hs.get("type")
        if kind == "npc":
            if hs.get("counter"):
                state.inc(hs["counter"])
            choice = pick(hs.get("dialogue"), state)
            dialogue_id = choice["id"] if isinstance(choice, dict) else choice
            if dialogue_id:
                self.talking_to = hs["id"]
                g.dialogue.start(dialogue_id)
            g.actions.run(hs.get("on_talk"))
        elif kind == "item":
            state.set_flag(hs.get("pickup_flag", f"picked_{hs['id']}"))
            g.actions.run([{"give_item": hs["item"]}])
            self.burst(pygame.Rect(hs["rect"]).center)
            pickup = g.content.item(hs["item"]).get("pickup")
            if pickup:
                g.dialogue.start_lines([{"speaker": "baker", "text": pickup, "voice": f"pickup_{hs['item']}"}])
            g.actions.run(hs.get("actions"))
        elif kind == "humor":
            g.audio.play(hs.get("sound", "bubble"))
            self.burst(pygame.Rect(hs["rect"]).center, count=14)
            texts = hs.get("text")
            n = state.inc(f"humor_{self.id}_{hs['id']}") - 1
            if isinstance(texts, list):
                n %= len(texts)
                text = texts[n]
            else:
                n, text = 0, texts
            if text:
                g.dialogue.start_lines([{"speaker": hs.get("speaker", "baker"), "text": text,
                                         "voice": f"humor_{self.id}_{hs['id']}_{n + 1:02d}"}])
            g.actions.run(hs.get("actions"))
        elif kind == "exit":
            if check(hs.get("requires"), state):
                g.actions.run(hs.get("actions"))
                g.scenes.switch(hs["to"], hs.get("spawn"))
            else:
                g.actions.run(hs.get("blocked"))
        elif kind == "object":
            if hs.get("on_click"):
                g.actions.run(hs["on_click"])
            elif hs.get("dialogue"):
                choice = pick(hs["dialogue"], state)
                dialogue_id = choice["id"] if isinstance(choice, dict) else choice
                if dialogue_id:
                    g.dialogue.start(dialogue_id)
            elif hs.get("examine"):
                g.dialogue.start_lines([{"speaker": "baker", "text": hs["examine"]}])

    def _use_item(self, hs: dict, item: str):
        g = self.game
        uses = hs.get("use", {})
        entry = uses.get(item, uses.get("*"))
        if entry is None:
            g.dialogue.start(g.content.quests.get("wrong_item_dialogue", "wrong_item"))
            return
        if isinstance(entry, dict):
            if not check(entry.get("if"), g.state):
                g.actions.run(entry.get("else") or [{"dialogue": g.content.quests.get("wrong_item_dialogue", "wrong_item")}])
                return
            if entry.get("consume"):
                g.state.inventory.remove(item)
            g.actions.run(entry.get("actions"))
        else:
            g.actions.run(entry)

    # Effects ---------------------------------------------------------------------
    def burst(self, center, count=8):
        for _ in range(count):
            self.particles.append(Particle(center[0] + random.uniform(-14, 14), center[1] + random.uniform(-10, 10),
                                           random.uniform(-25, 25), random.uniform(-90, -40),
                                           random.uniform(0.8, 1.6), random.randint(3, 8), (220, 240, 255)))

    # Update / draw ---------------------------------------------------------------
    def update(self, dt):
        self.time += dt
        self.game.player.update(dt)
        self.game.state.player_pos = [int(self.game.player.pos[0]), int(self.game.player.pos[1])]
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        if not self.game.dialogue.is_active():
            self.talking_to = None
        if random.random() < dt * 0.6:
            self.particles.append(Particle(random.uniform(0, WIDTH), PLAY_H + 10, random.uniform(-10, 10),
                                           random.uniform(-70, -30), random.uniform(5, 9), random.randint(2, 5), (200, 230, 255)))

    def draw_background(self, screen):
        screen.blit(self.game.assets.background(self.data), (0, 0))

    def draw_ambient(self, screen):
        """Subclass hook: drawn after the background, before hotspots."""

    def draw_front(self, screen):
        """Subclass hook: drawn after everything (overlays like cave darkness)."""

    def draw(self, screen):
        g = self.game
        self.draw_background(screen)
        self.draw_ambient(screen)
        drawables = []
        frame = int(self.time * 60)
        for hs in self.visible_hotspots():
            if hs.get("draw", True) is False:
                continue
            rect = pygame.Rect(hs["rect"])
            kind = hs.get("type")
            if kind == "npc" and hs.get("character"):
                talking = self.talking_to == hs["id"] and g.dialogue.current_speaker() == hs["character"]
                facing = hs.get("facing", "left" if rect.centerx > g.player.pos[0] else "right")
                surf = g.assets.character(hs["character"], rect.w, rect.h, frame + hash(hs["id"]) % 40, facing, talking)
                drawables.append((rect.bottom, surf, rect))
            elif kind == "item":
                size = min(rect.w, rect.h)
                surf = g.assets.icon(hs["item"], size)
                r = surf.get_rect(center=(rect.centerx, rect.centery + math.sin(self.time * 3 + rect.x) * 3))
                drawables.append((rect.bottom, surf, r))
            else:
                surf = g.assets.prop(self.id, hs)
                drawables.append((rect.bottom - 1, surf, rect))
        drawables.sort(key=lambda d: d[0])
        player_bottom = g.player.pos[1]
        player_drawn = False
        for bottom, surf, rect in drawables:
            if not player_drawn and bottom > player_bottom:
                g.player.draw(screen, g.assets, talking=g.dialogue.current_speaker() == "baker")
                player_drawn = True
            screen.blit(surf, rect)
        if not player_drawn:
            g.player.draw(screen, g.assets, talking=g.dialogue.current_speaker() == "baker")
        if self.hover is not None and not g.dialogue.is_active():
            glow = pygame.Rect(self.hover["rect"]).inflate(10, 10)
            pygame.draw.rect(screen, (255, 255, 200), glow, 3, border_radius=12)
        for p in self.particles:
            p.draw(screen)
        self.draw_front(screen)
        if self.debug:
            pygame.draw.polygon(screen, (0, 255, 0), self.walkable, 2)
            for hs in self.data.get("hotspots", []):
                pygame.draw.rect(screen, (255, 0, 255), hs["rect"], 1)
                lbl = g.assets.font(14).render(hs["id"], True, (255, 0, 255))
                screen.blit(lbl, (hs["rect"][0], hs["rect"][1] - 14))
