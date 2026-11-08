"""Shared drawing helpers: wrapped text, panels, buttons, toasts, inventory bar."""
import pygame

from .config import WIDTH, HEIGHT, INVENTORY_BAR_H, PLAY_H

INK = (30, 30, 50)
PANEL = (250, 248, 235)
PANEL_EDGE = (60, 90, 140)
ACCENT = (255, 170, 60)


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if font.size(trial)[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(surface, text, font, color, pos, max_width=None, center=False, shadow=None):
    lines = wrap_text(text, font, max_width) if max_width else [text]
    x, y = pos
    for line in lines:
        img = font.render(line, True, color)
        rect = img.get_rect()
        if center:
            rect.midtop = (x, y)
        else:
            rect.topleft = (x, y)
        if shadow:
            sh = font.render(line, True, shadow)
            surface.blit(sh, rect.move(2, 2))
        surface.blit(img, rect)
        y += font.get_linesize()
    return y


def draw_panel(surface, rect, fill=PANEL, edge=PANEL_EDGE, radius=18, alpha=235):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*fill, alpha), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, (*edge, 255), panel.get_rect(), 4, border_radius=radius)
    surface.blit(panel, rect.topleft)


class Button:
    def __init__(self, rect, label, callback=None, color=ACCENT, text_color=INK, font_size=28):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.hover = False
        self.enabled = True

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            if self.callback:
                self.callback()
            return True
        return False

    def draw(self, surface, font):
        color = self.color if not self.hover else tuple(min(255, c + 30) for c in self.color)
        if not self.enabled:
            color = (170, 170, 170)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, PANEL_EDGE, self.rect, 3, border_radius=14)
        img = font.render(self.label, True, self.text_color)
        surface.blit(img, img.get_rect(center=self.rect.center))


class Toast:
    """Short 'Got: Gear!' style message that floats above the inventory bar."""

    def __init__(self):
        self.text = None
        self.timer = 0.0

    def show(self, text, seconds=2.5):
        self.text = text
        self.timer = seconds

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.text = None

    def draw(self, surface, font):
        if not self.text:
            return
        img = font.render(self.text, True, INK)
        rect = img.get_rect(midbottom=(WIDTH // 2, PLAY_H - 16)).inflate(30, 16)
        draw_panel(surface, rect, radius=12)
        surface.blit(img, img.get_rect(center=rect.center))


class InventoryBar:
    SLOT = 64
    GAP = 10

    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(0, PLAY_H, WIDTH, INVENTORY_BAR_H)
        self.hint_button = Button((WIDTH - 170, PLAY_H + 14, 70, 52), "?", font_size=36)
        self.menu_button = Button((WIDTH - 90, PLAY_H + 14, 76, 52), "Menu", font_size=24)
        self.hover_item = None

    def slot_rects(self):
        items = self.game.state.inventory.items()
        x = 16
        y = PLAY_H + (INVENTORY_BAR_H - self.SLOT) // 2
        for item_id in items:
            yield item_id, pygame.Rect(x, y, self.SLOT, self.SLOT)
            x += self.SLOT + self.GAP

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover_item = None
            for item_id, rect in self.slot_rects():
                if rect.collidepoint(event.pos):
                    self.hover_item = item_id
            self.hint_button.handle_event(event)
            self.menu_button.handle_event(event)
            return self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                return False
            if self.hint_button.rect.collidepoint(event.pos):
                self.game.hints.request_now()
                return True
            if self.menu_button.rect.collidepoint(event.pos):
                self.game.open_pause()
                return True
            inv = self.game.state.inventory
            for item_id, rect in self.slot_rects():
                if rect.collidepoint(event.pos):
                    selected = inv.selected_item()
                    if selected and selected != item_id:
                        self.game.use_item_on_item(selected, item_id)
                    else:
                        inv.toggle_select(item_id)
                        self.game.audio.play("click")
                    return True
            inv.deselect()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.rect.collidepoint(event.pos):
            # right-click an item to read its description
            for item_id, rect in self.slot_rects():
                if rect.collidepoint(event.pos):
                    self.game.describe_item(item_id)
                    return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, (18, 40, 70), self.rect)
        pygame.draw.line(surface, (90, 160, 210), (0, PLAY_H), (WIDTH, PLAY_H), 3)
        inv = self.game.state.inventory
        font = self.game.assets.font(20)
        for item_id, rect in self.slot_rects():
            pygame.draw.rect(surface, (40, 80, 120), rect, border_radius=10)
            if inv.selected_item() == item_id:
                pygame.draw.rect(surface, ACCENT, rect, 4, border_radius=10)
            icon = self.game.assets.icon(item_id, self.SLOT - 12)
            surface.blit(icon, icon.get_rect(center=rect.center))
        if self.hover_item:
            name = self.game.content.item(self.hover_item)["name"]
            img = font.render(name, True, (255, 255, 255))
            surface.blit(img, (16, HEIGHT - 20 - img.get_height() // 2 + 10 - 8))
        self.hint_button.draw(surface, self.game.assets.font(36))
        self.menu_button.draw(surface, self.game.assets.font(22))
