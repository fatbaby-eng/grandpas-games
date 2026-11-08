"""Creates scene objects from scenes.json and switches between them with a fade."""
import pygame

from .config import WIDTH, PLAY_H


class SceneManager:
    FADE_TIME = 0.35

    def __init__(self, game, registry: dict):
        self.game = game
        self.registry = registry          # scene_id -> Scene subclass (falls back to BaseScene)
        self.current = None
        self._pending = None              # (scene_id, spawn) while fading out
        self._fade = 0.0                  # 0..1 darkness
        self._fading_out = False
        self._cache: dict = {}

    def _make(self, scene_id: str):
        if scene_id not in self._cache:
            data = dict(self.game.content.scene(scene_id))
            data["id"] = scene_id
            cls = self.registry.get(scene_id, self.registry["__default__"])
            self._cache[scene_id] = cls(self.game, data)
        return self._cache[scene_id]

    def switch(self, scene_id: str, spawn=None, instant=False):
        if instant or self.current is None:
            self._do_switch(scene_id, spawn)
            self._fade = 1.0 if not instant else 0.0
            self._fading_out = False
            return
        self._pending = (scene_id, spawn)
        self._fading_out = True

    def _do_switch(self, scene_id, spawn):
        if self.current is not None:
            self.current.on_exit()
        scene = self._make(scene_id)
        self.current = scene
        self.game.state.scene_id = scene_id
        pos = spawn or scene.data.get("spawn", [640, 520])
        self.game.player.teleport(pos)
        self.game.state.player_pos = list(pos)
        scene.on_enter()
        self.game.save_game(autosave=True)

    @property
    def transitioning(self) -> bool:
        return self._fading_out or self._fade > 0

    def update(self, dt):
        if self._fading_out:
            self._fade = min(1.0, self._fade + dt / self.FADE_TIME)
            if self._fade >= 1.0:
                scene_id, spawn = self._pending
                self._pending = None
                self._fading_out = False
                self._do_switch(scene_id, spawn)
        elif self._fade > 0:
            self._fade = max(0.0, self._fade - dt / self.FADE_TIME)
        if self.current is not None:
            self.current.update(dt)

    def draw(self, screen):
        if self.current is not None:
            self.current.draw(screen)
        if self._fade > 0:
            shade = pygame.Surface((WIDTH, PLAY_H))
            shade.fill((0, 0, 0))
            shade.set_alpha(int(255 * self._fade))
            screen.blit(shade, (0, 0))
