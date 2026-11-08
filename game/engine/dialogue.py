"""Dialogue boxes driven by game/content/dialogue.json.

A dialogue entry looks like:
    "coral_intro": {
        "lines": [
            {"speaker": "coral", "text": "Baker! The Conch Shell is GONE!", "actions": [...]},
            {"speaker": "baker", "text": "...", "choices": [{"text": "...", "next": "other_id"}]}
        ],
        "end": [ {"set_flag": "main_conch"} ]
    }
`speaker` is a character id from characters.json. Actions run when their line
is shown; `end` actions run when the last line is dismissed.
"""
import pygame

from .config import WIDTH, PLAY_H
from .ui import draw_panel, draw_text, Button, INK


class DialogueManager:
    BOX = pygame.Rect(40, PLAY_H - 230, WIDTH - 80, 210)

    def __init__(self, content, run_actions, assets, audio=None):
        self.content = content
        self.run_actions = run_actions
        self.assets = assets
        self.audio = audio
        self._lines: list[dict] = []
        self._end: list = []
        self._index = -1
        self._active = False
        self._choice_buttons: list[Button] = []
        self.current_id = None
        self.frame = 0

    # Control ---------------------------------------------------------------
    def start(self, dialogue_id: str):
        entry = self.content.dialogue_entry(dialogue_id)
        self.current_id = dialogue_id
        self._begin(entry.get("lines", []), entry.get("end", []))

    def start_lines(self, lines: list[dict], end=None):
        """Ad-hoc dialogue (used by the `say` action)."""
        self.current_id = None
        self._begin(lines, end or [])

    def _begin(self, lines, end):
        self._lines = list(lines)
        self._end = list(end)
        self._index = -1
        self._active = True
        self.advance()

    def advance(self):
        if not self._active:
            return
        self._index += 1
        self._choice_buttons = []
        if self._index >= len(self._lines):
            self._active = False
            if self.audio is not None:
                self.audio.stop_voice()
            end, self._end = self._end, []
            if end:
                self.run_actions(end)
            return
        line = self._lines[self._index]
        self._play_voice(line)
        if line.get("actions"):
            self.run_actions(line["actions"])
        if line.get("choices"):
            self._build_choices(line["choices"])

    def _play_voice(self, line):
        """Voice-over: `voice` names a file in assets/audio/voice/ (no extension needed).
        Recorded lines are optional; a missing file is silently skipped."""
        if self.audio is None:
            return
        self.audio.stop_voice()
        voice = line.get("voice")
        if not voice and self.current_id is not None:
            voice = f"{self.current_id}_{self._index + 1:02d}"
        if voice:
            self.audio.play_voice(voice)

    def _build_choices(self, choices):
        y = self.BOX.top + 70
        for choice in choices:
            btn = Button((self.BOX.left + 150, y, self.BOX.width - 190, 36), choice["text"],
                         callback=lambda c=choice: self._choose(c), color=(255, 230, 160), font_size=22)
            self._choice_buttons.append(btn)
            y += 42

    def _choose(self, choice):
        if choice.get("actions"):
            self.run_actions(choice["actions"])
        nxt = choice.get("next")
        if nxt:
            self.start(nxt)
        else:
            self._choice_buttons = []
            self.advance()

    def is_active(self) -> bool:
        return self._active

    def current_line(self) -> dict | None:
        if self._active and 0 <= self._index < len(self._lines):
            return self._lines[self._index]
        return None

    def current_speaker(self) -> str | None:
        line = self.current_line()
        return line.get("speaker") if line else None

    # Events ----------------------------------------------------------------
    def handle_event(self, event) -> bool:
        if not self._active:
            return False
        if self._choice_buttons:
            for btn in self._choice_buttons:
                if btn.handle_event(event):
                    return True
            return event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.advance()
            return True
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.advance()
            return True
        return event.type == pygame.MOUSEBUTTONDOWN

    # Drawing ---------------------------------------------------------------
    def update(self, dt):
        self.frame += 1

    def draw(self, screen):
        line = self.current_line()
        if not line:
            return
        draw_panel(screen, self.BOX)
        speaker_id = line.get("speaker", "baker")
        char = self.content.character(speaker_id)
        portrait = self.assets.portrait(speaker_id, 110)
        screen.blit(portrait, (self.BOX.left + 18, self.BOX.top + 18))
        name_font = self.assets.font(26, bold=True)
        draw_text(screen, char.get("name", speaker_id), name_font, tuple(char.get("color", INK)),
                  (self.BOX.left + 150, self.BOX.top + 16), shadow=(40, 40, 40))
        body_font = self.assets.font(26)
        if self._choice_buttons:
            draw_text(screen, line["text"], body_font, INK, (self.BOX.left + 150, self.BOX.top + 44),
                      max_width=self.BOX.width - 190)
            for btn in self._choice_buttons:
                btn.draw(screen, self.assets.font(22))
        else:
            draw_text(screen, line["text"], body_font, INK, (self.BOX.left + 150, self.BOX.top + 56),
                      max_width=self.BOX.width - 190)
            if (self.frame // 30) % 2 == 0:
                tip = self.assets.font(18).render("click to continue", True, (120, 120, 140))
                screen.blit(tip, tip.get_rect(bottomright=(self.BOX.right - 20, self.BOX.bottom - 12)))
