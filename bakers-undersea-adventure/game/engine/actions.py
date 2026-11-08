"""Interpreter for the little action lists used throughout the JSON content.

Supported actions (each is a one-key dict, optionally with extra keys):
    {"set_flag": "x"}                     {"clear_flag": "x"}
    {"give_item": "id"}                   {"remove_item": "id"}
    {"inc": "counter"}
    {"dialogue": "dialogue_id"}           start a dialogue from dialogue.json
    {"say": "text", "speaker": "baker"}   one-line ad-hoc dialogue
    {"goto": "scene_id", "spawn": [x, y]}
    {"minigame": "bubble_catch", "on_complete": [actions]}
    {"sound": "bubble"}                   {"music": "festival"}
    {"toast": "text"}
    {"ending": true}                      play the ending slides
    {"save": true}
    {"if": cond, "then": [actions], "else": [actions]}
"""
from .conditions import check


class ActionRunner:
    def __init__(self, game):
        self.game = game

    def run(self, actions, context=None):
        if not actions:
            return
        if isinstance(actions, dict):
            actions = [actions]
        for action in actions:
            self._run_one(action, context)

    def _run_one(self, action: dict, context):
        g = self.game
        state = g.state
        if "if" in action:
            branch = action.get("then") if check(action["if"], state) else action.get("else")
            self.run(branch, context)
            return
        if "set_flag" in action:
            state.set_flag(action["set_flag"])
        if "clear_flag" in action:
            state.clear_flag(action["clear_flag"])
        if "inc" in action:
            state.inc(action["inc"])
        if "give_item" in action:
            item_id = action["give_item"]
            if state.inventory.add(item_id):
                g.audio.play("pickup")
                g.toast.show(f"Got: {g.content.item(item_id)['name']}!")
        if "remove_item" in action:
            state.inventory.remove(action["remove_item"])
        if "sound" in action:
            g.audio.play(action["sound"])
        if "music" in action:
            g.audio.music(action["music"])
        if "toast" in action:
            g.toast.show(action["toast"])
        if "say" in action:
            g.dialogue.start_lines([{"speaker": action.get("speaker", "baker"), "text": action["say"],
                                     "voice": action.get("voice")}])
        if "dialogue" in action:
            g.dialogue.start(action["dialogue"])
        if "goto" in action:
            g.scenes.switch(action["goto"], action.get("spawn"))
        if "minigame" in action:
            g.start_minigame(action["minigame"], action.get("on_complete", []))
        if "ending" in action:
            g.start_ending()
        if "save" in action:
            g.save_game()
