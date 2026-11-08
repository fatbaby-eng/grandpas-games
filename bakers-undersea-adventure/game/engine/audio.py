"""Sound effects and music loops. Silently does nothing if the mixer is unavailable."""
import pygame

from .config import AUDIO_DIR


class AudioManager:
    def __init__(self):
        self.ok = False
        self.muted = False
        self._sounds: dict = {}
        self._music = None
        self._voice_channel = None
        self._voice_cache: dict = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(16)
            self._voice_channel = pygame.mixer.Channel(15)
            self.ok = True
        except pygame.error:
            self.ok = False

    def _path(self, name):
        for ext in (".ogg", ".wav"):
            p = AUDIO_DIR / f"{name}{ext}"
            if p.is_file():
                return p
        return None

    def play(self, name: str, volume: float = 0.8):
        if not self.ok or self.muted or not name:
            return
        if name not in self._sounds:
            path = self._path(name)
            try:
                self._sounds[name] = pygame.mixer.Sound(str(path)) if path else None
            except pygame.error:
                self._sounds[name] = None
        snd = self._sounds[name]
        if snd:
            snd.set_volume(volume)
            snd.play()

    def music(self, name: str | None, volume: float = 0.5):
        if not self.ok:
            return
        if name == self._music:
            return
        self._music = name
        try:
            pygame.mixer.music.stop()
            path = self._path(name) if name else None
            if path and not self.muted:
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1, fade_ms=600)
        except pygame.error:
            pass

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        if self.ok:
            if self.muted:
                pygame.mixer.music.stop()
            else:
                current, self._music = self._music, None
                self.music(current)
        return self.muted

    # Voice-over ---------------------------------------------------------------
    def play_voice(self, name: str):
        """Play assets/audio/voice/<name>.(ogg|wav) if it exists."""
        if not self.ok or self.muted or self._voice_channel is None:
            return
        if name not in self._voice_cache:
            snd = None
            for ext in (".ogg", ".wav"):
                path = AUDIO_DIR / "voice" / f"{name}{ext}"
                if path.is_file():
                    try:
                        snd = pygame.mixer.Sound(str(path))
                    except pygame.error:
                        snd = None
                    break
            self._voice_cache[name] = snd
        snd = self._voice_cache[name]
        if snd:
            self._voice_channel.play(snd)

    def stop_voice(self):
        if self.ok and self._voice_channel is not None:
            self._voice_channel.stop()
