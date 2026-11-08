"""The Game object: owns every manager, runs the main loop, and handles the
title screen, pause menu, mini-game menu and ending slides."""
import pygame

from .actions import ActionRunner
from .assets import AssetManager
from .audio import AudioManager
from .conditions import check
from .config import TITLE, WIDTH, HEIGHT, FPS, PLAY_H
from .content import Content
from .cursor import CursorManager
from .dialogue import DialogueManager
from .hint_system import HintSystem
from .input_handler import InputHandler
from .player import Player
from .save_load import SaveManager
from .scene_manager import SceneManager
from .state import GameState
from .ui import Button, Toast, InventoryBar, draw_panel, draw_text, INK
from ..scenes import REGISTRY as SCENE_REGISTRY
from ..minigames import REGISTRY as MINIGAME_REGISTRY


class Game:
    def __init__(self, save_path=None, content_dir=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.content = Content(content_dir)
        self.assets = AssetManager(self.content)
        self.audio = AudioManager()
        self.saves = SaveManager(save_path)
        self.state = GameState(start_scene=self.content.quests.get("start_scene", "coral_reef"))
        self.player = Player()
        self.cursor = CursorManager()
        self.actions = ActionRunner(self)
        self.dialogue = DialogueManager(self.content, self.actions.run, self.assets, self.audio)
        self.scenes = SceneManager(self, SCENE_REGISTRY)
        self.hints = HintSystem(self)
        self.toast = Toast()
        self.inventory_bar = InventoryBar(self)
        self.input = InputHandler()
        self.minigame = None
        self.mode = "title"            # title | playing | paused | minigames | ending
        self.running = True
        self.ending_slides = []
        self.ending_index = 0
        self.frame = 0
        self._build_menus()

    # Menus --------------------------------------------------------------------
    def _build_menus(self):
        ui = self.content.quests.get("ui", {})
        cx = WIDTH // 2
        self.title_buttons = [
            Button((cx - 150, 400, 300, 56), ui.get("new_game", "New Game"), self.new_game),
            Button((cx - 150, 470, 300, 56), ui.get("continue", "Continue"), self.load_game),
            Button((cx - 150, 540, 300, 56), ui.get("quit", "Quit"), self.quit, color=(200, 210, 230)),
        ]
        self.pause_buttons = [
            Button((cx - 150, 170, 300, 50), ui.get("resume", "Resume"), self.close_pause),
            Button((cx - 150, 230, 300, 50), ui.get("save", "Save Game"), lambda: self.save_game(autosave=False)),
            Button((cx - 150, 290, 300, 50), "", self.toggle_hints),
            Button((cx - 150, 350, 300, 50), "", self.toggle_sound),
            Button((cx - 150, 410, 300, 50), ui.get("minigames", "Mini-games"), self.open_minigame_menu),
            Button((cx - 150, 470, 300, 50), ui.get("to_title", "Quit to Title"), self.to_title, color=(200, 210, 230)),
        ]
        self.minigame_buttons = []
        y = 200
        for mg_id, info in self.content.quests.get("minigames", {}).items():
            self.minigame_buttons.append(Button((cx - 200, y, 400, 50), info.get("title", mg_id),
                                                lambda m=mg_id: self.start_minigame(m, [], from_menu=True)))
            y += 60
        self.minigame_buttons.append(Button((cx - 200, y + 10, 400, 50), ui.get("back", "Back"), self.open_pause, color=(200, 210, 230)))

    def _refresh_toggle_labels(self):
        ui = self.content.quests.get("ui", {})
        on, off = ui.get("on", "On"), ui.get("off", "Off")
        self.pause_buttons[2].label = f"{ui.get('hints', 'Hints')}: {on if self.state.hints_enabled else off}"
        self.pause_buttons[3].label = f"{ui.get('sound', 'Sound')}: {off if self.audio.muted else on}"

    # Game flow ------------------------------------------------------------------
    def new_game(self):
        self.state = GameState(start_scene=self.content.quests.get("start_scene", "coral_reef"))
        self.scenes = SceneManager(self, SCENE_REGISTRY)
        self.hints = HintSystem(self)
        self.dialogue = DialogueManager(self.content, self.actions.run, self.assets, self.audio)
        self.minigame = None
        self.mode = "playing"
        self.scenes.switch(self.state.scene_id, None, instant=True)
        self.actions.run(self.content.quests.get("on_new_game"))

    def load_game(self):
        data = self.saves.load()
        if data is None:
            self.toast.show(self.content.quests.get("ui", {}).get("no_save", "No saved game yet."))
            return
        self.state = GameState.from_dict(data)
        self.scenes = SceneManager(self, SCENE_REGISTRY)
        self.hints = HintSystem(self)
        self.dialogue = DialogueManager(self.content, self.actions.run, self.assets, self.audio)
        self.minigame = None
        self.mode = "playing"
        self.scenes.switch(self.state.scene_id, list(self.state.player_pos), instant=True)

    def save_game(self, autosave=True):
        if self.mode not in ("playing", "paused") and not autosave:
            return
        if self.scenes.current is None:
            return
        self.saves.save(self.state.to_dict())
        if not autosave:
            self.toast.show(self.content.quests.get("ui", {}).get("saved", "Game saved!"))
            self.close_pause()

    def to_title(self):
        self.save_game(autosave=True)
        self.audio.music(None)
        self.mode = "title"

    def quit(self):
        self.running = False

    def open_pause(self):
        if self.mode in ("playing", "minigames"):
            self._refresh_toggle_labels()
            self.mode = "paused"

    def close_pause(self):
        if self.mode in ("paused", "minigames"):
            self.mode = "playing"

    def toggle_hints(self):
        self.hints.toggle()
        self._refresh_toggle_labels()

    def toggle_sound(self):
        self.audio.toggle_mute()
        self._refresh_toggle_labels()

    def open_minigame_menu(self):
        self.mode = "minigames"

    # Mini-games -----------------------------------------------------------------
    def start_minigame(self, mg_id: str, on_complete, from_menu=False):
        cls = MINIGAME_REGISTRY[mg_id]
        info = self.content.quests.get("minigames", {}).get(mg_id, {})
        self.minigame = cls(self, info, on_complete)
        self.minigame.from_menu = from_menu
        self.mode = "playing"
        self.cursor.set("arrow")

    def end_minigame(self, minigame, skipped: bool):
        on_complete = minigame.on_complete
        self.minigame = None
        self.state.minigames_done.add(minigame.id)
        self.hints.reset()
        if getattr(minigame, "from_menu", False):
            return
        self.actions.run(on_complete)

    # Ending -----------------------------------------------------------------------
    def start_ending(self):
        slides = [s for s in self.content.quests.get("ending", []) if check(s.get("if"), self.state)]
        self.ending_slides = slides
        self.ending_index = 0
        self.mode = "ending"
        self.audio.music(self.content.quests.get("ending_music", "festival"))
        self.save_game(autosave=True)

    def _advance_ending(self):
        self.ending_index += 1
        if self.ending_index >= len(self.ending_slides):
            self.mode = "playing"

    # Items ----------------------------------------------------------------------------
    def use_item_on_item(self, a: str, b: str):
        items = self.content.items
        entry = items.get(a, {}).get("combine", {}).get(b) or items.get(b, {}).get("combine", {}).get(a)
        self.state.inventory.deselect()
        if entry is None:
            self.dialogue.start(self.content.quests.get("wrong_item_dialogue", "wrong_item"))
            return
        for item_id in entry.get("consume", []):
            self.state.inventory.remove(item_id)
        self.actions.run(entry.get("actions"))

    def describe_item(self, item_id: str):
        item = self.content.item(item_id)
        self.dialogue.start_lines([{"speaker": "baker", "text": item.get("description", item["name"])}])

    # Main loop -------------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.handle_input()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_event_global(self, event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == "playing" and self.minigame is None:
                    self.open_pause()
                    return True
                if self.mode in ("paused", "minigames"):
                    self.close_pause()
                    return True
            if event.key == pygame.K_h and self.mode == "playing":
                self.toggle_hints()
                return True
            if event.key == pygame.K_m:
                self.toggle_sound()
                return True
        return False

    def handle_input(self):
        if self.mode == "title":
            layers = [self, _ButtonLayer(self.title_buttons)]
        elif self.mode == "paused":
            layers = [self, _ButtonLayer(self.pause_buttons)]
        elif self.mode == "minigames":
            layers = [self, _ButtonLayer(self.minigame_buttons)]
        elif self.mode == "ending":
            layers = [self, _EndingLayer(self)]
        else:
            layers = [self, self.minigame, self.dialogue, self.hints, self.inventory_bar, self.scenes.current]
        self.input.poll(layers)
        if self.input.quit_requested:
            if self.mode in ("playing", "paused"):
                self.save_game(autosave=True)
            self.running = False

    # `self` acts as the top-most layer for global keys
    def handle_event(self, event) -> bool:
        return self.handle_event_global(event)

    def update(self, dt):
        self.frame += 1
        self.toast.update(dt)
        if self.mode == "playing":
            self.state.play_time += dt
            if self.minigame is not None:
                self.minigame.update(dt)
            else:
                self.scenes.update(dt)
                self.dialogue.update(dt)
                self.hints.update(dt)
            inv = self.state.inventory
            if inv.selected_item():
                self.cursor.set_item_icon(self.assets.icon(inv.selected_item(), 40))
                if self.input.mouse_pos[1] < PLAY_H and self.minigame is None and not self.dialogue.is_active():
                    self.cursor.set("item")
            elif self.cursor.kind == "item":
                self.cursor.set("arrow")
            if self.dialogue.is_active() or self.minigame is not None:
                self.cursor.set("arrow")
        elif self.mode == "ending":
            self.scenes.update(dt)
        else:
            self.cursor.set("arrow")

    def draw(self):
        screen = self.screen
        if self.mode == "title":
            self._draw_title(screen)
        else:
            self.scenes.draw(screen)
            self.inventory_bar.draw(screen)
            if self.mode == "playing":
                if self.minigame is not None:
                    self.minigame.draw(screen)
                else:
                    self.dialogue.draw(screen)
                    self.hints.draw(screen)
            elif self.mode == "paused":
                self._draw_menu(screen, self.content.quests.get("ui", {}).get("paused", "Paused"), self.pause_buttons)
            elif self.mode == "minigames":
                self._draw_menu(screen, self.content.quests.get("ui", {}).get("minigames", "Mini-games"), self.minigame_buttons)
            elif self.mode == "ending":
                self._draw_ending(screen)
        self.toast.draw(screen, self.assets.font(26))
        self.cursor.draw(screen)

    def _draw_title(self, screen):
        start = dict(self.content.scene(self.content.quests.get("start_scene", "coral_reef")))
        start["id"] = self.content.quests.get("start_scene", "coral_reef")
        screen.blit(self.assets.background(start), (0, 0))
        pygame.draw.rect(screen, (18, 40, 70), (0, PLAY_H, WIDTH, HEIGHT - PLAY_H))
        hero = self.assets.character("baker", 260, 170, self.frame)
        screen.blit(hero, hero.get_rect(center=(WIDTH // 2, 290)))
        draw_text(screen, TITLE, self.assets.font(72, bold=True), (255, 240, 200), (WIDTH // 2, 60), center=True, shadow=(20, 40, 80))
        draw_text(screen, self.content.quests.get("tagline", ""), self.assets.font(28), (230, 240, 255), (WIDTH // 2, 150), center=True, shadow=(20, 40, 80))
        self.title_buttons[1].enabled = self.saves.exists()
        for btn in self.title_buttons:
            btn.draw(screen, self.assets.font(30))

    def _draw_menu(self, screen, title, buttons):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 10, 30, 150))
        screen.blit(shade, (0, 0))
        panel = pygame.Rect(WIDTH // 2 - 240, 80, 480, 500)
        draw_panel(screen, panel)
        draw_text(screen, title, self.assets.font(44, bold=True), INK, (WIDTH // 2, 100), center=True)
        for btn in buttons:
            btn.draw(screen, self.assets.font(26))

    def _draw_ending(self, screen):
        if not self.ending_slides:
            return
        slide = self.ending_slides[min(self.ending_index, len(self.ending_slides) - 1)]
        panel = pygame.Rect(140, 120, WIDTH - 280, 380)
        draw_panel(screen, panel, fill=(255, 250, 230))
        speaker = slide.get("speaker")
        y = panel.top + 40
        if speaker:
            portrait = self.assets.portrait(speaker, 120)
            screen.blit(portrait, portrait.get_rect(midtop=(WIDTH // 2, y)))
            y += 140
        draw_text(screen, slide.get("text", ""), self.assets.font(32), INK, (WIDTH // 2, y), center=True, max_width=panel.width - 80)
        tip = self.assets.font(20).render(self.content.quests.get("ui", {}).get("click_continue", "click to continue"), True, (120, 120, 140))
        screen.blit(tip, tip.get_rect(bottomright=(panel.right - 24, panel.bottom - 16)))


class _ButtonLayer:
    def __init__(self, buttons):
        self.buttons = buttons

    def handle_event(self, event) -> bool:
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return event.type == pygame.MOUSEBUTTONDOWN


class _EndingLayer:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event) -> bool:
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or \
                (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)):
            self.game._advance_ending()
            return True
        return event.type == pygame.MOUSEBUTTONDOWN
