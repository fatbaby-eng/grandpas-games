"""Drives the real Game object headlessly through the main quest (both the
helmet route and the lantern route) and every side quest, by calling the same
interaction code the mouse would. Proves there is no dead end."""
import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.engine.game import Game  # noqa: E402


@pytest.fixture
def game(tmp_path):
    g = Game(save_path=tmp_path / "save.json")
    g.new_game()
    yield g
    pygame.quit()


class Driver:
    def __init__(self, game):
        self.g = game

    def tick(self, n=1):
        for _ in range(n):
            self.g.update(1 / 60)
            self.g.draw()

    def finish_dialogue(self, choice_index=0):
        """Advance through the current dialogue, taking choice `choice_index` when asked."""
        guard = 0
        while self.g.dialogue.is_active():
            guard += 1
            assert guard < 100, "dialogue never ended"
            line = self.g.dialogue.current_line()
            if line.get("choices"):
                self.g.dialogue._choose(line["choices"][choice_index])
            else:
                self.g.dialogue.advance()
            if self.g.minigame is not None:
                self.finish_minigame()
        self.tick()

    def finish_minigame(self):
        mg = self.g.minigame
        assert mg is not None
        mg.finish()                      # the player "won"
        self.tick()

    def scene(self):
        return self.g.scenes.current

    def go(self, scene_id):
        self.g.scenes.switch(scene_id, instant=True)
        self.tick()

    def hs(self, hs_id):
        hs = self.scene().hotspot_by_id(hs_id)
        assert hs is not None, hs_id
        assert hs in self.scene().visible_hotspots(), f"{hs_id} not visible"
        return hs

    def _settle(self, choice):
        if self.g.minigame is not None:
            self.finish_minigame()
        self.finish_dialogue(choice)

    def click(self, hs_id, choice=0):
        self.scene().interact(self.hs(hs_id), None)
        self._settle(choice)

    def use(self, item, hs_id, choice=0):
        assert self.g.state.inventory.has(item), item
        self.scene().interact(self.hs(hs_id), item)
        self._settle(choice)

    def exit(self, hs_id):
        hs = self.hs(hs_id)
        before = self.g.state.scene_id
        self.scene().interact(hs, None)
        self.finish_dialogue()
        self.tick(40)                    # let the fade finish
        return self.g.state.scene_id != before

    def has(self, item):
        return self.g.state.inventory.has(item)

    def flag(self, f):
        return self.g.state.has_flag(f)


def test_main_quest_helmet_route(game):
    d = Driver(game)
    d.finish_dialogue()                                  # intro
    assert not d.exit("to_festival"), "festival should be locked"
    d.click("coral"); assert d.flag("main_conch")
    d.click("grandma"); assert d.flag("clue_kelp")
    assert d.exit("to_kelp")
    assert not d.exit("to_cave"), "cave needs light/air"
    d.click("puffer"); assert d.flag("met_puffer")
    d.click("gear"); assert d.has("gear")
    d.use("gear", "bubble_machine")
    assert d.flag("machine_fixed") and d.has("bubble_helmet") and not d.has("gear")
    assert d.exit("to_cave")
    d.finish_dialogue()                                  # cave_enter
    d.click("bill"); assert d.flag("found_bill")
    d.use("bubble_helmet", "stuck_shell")
    assert d.flag("shell_freed") and d.has("conch_shell")
    assert d.exit("to_kelp") and d.exit("to_reef")
    assert d.exit("to_festival")
    d.click("dj")                                        # return + DJ beat + ending
    assert d.flag("shell_returned") and d.flag("game_won")
    assert game.mode == "ending" and game.ending_slides
    for _ in range(len(game.ending_slides)):
        game._advance_ending()
    assert game.mode == "playing"
    assert not d.has("conch_shell")
    # Save/load after winning keeps the world consistent
    game.save_game(autosave=False)
    game.load_game()
    assert game.state.has_flag("game_won") and game.state.scene_id == "festival_grounds"


def test_main_quest_lantern_and_crowbar_route(game):
    d = Driver(game)
    d.finish_dialogue()
    d.click("coral"); d.click("grandma")
    d.go("sunken_ship")
    d.click("clam"); assert d.flag("met_clam")
    d.click("clam", choice=0)                            # joke contest -> key
    assert d.has("ship_key")
    d.use("ship_key", "treasure_door"); assert d.flag("treasure_room_open")
    d.click("lantern"); d.click("crowbar"); d.click("glasses")
    assert d.has("lantern") and d.has("crowbar") and d.has("glasses")
    d.go("kelp_forest")
    assert d.exit("to_cave"), "lantern alone must open the cave"
    d.finish_dialogue()
    d.click("stuck_shell")                               # before meeting Bill: polite nudge, no change
    assert not d.flag("shell_freed")
    d.click("bill")
    d.use("crowbar", "stuck_shell")
    assert d.has("conch_shell")


def test_all_side_quests(game):
    d = Driver(game)
    d.finish_dialogue()
    d.click("coral"); d.click("grandma")
    # Dance Like a Crab
    d.click("sidney"); assert d.flag("crab_dance_done") and d.has("dance_shoes")
    d.click("sidney")                                    # after-dialogue
    # Grandma's Recipe
    d.go("kelp_forest")
    d.click("recipe_page"); assert d.has("recipe_page")
    d.go("coral_reef")
    d.use("recipe_page", "grandma"); assert d.has("cookie") and d.flag("recipe_returned")
    d.use("cookie", "coral"); assert d.has("cookie"), "cookies are never used up"
    # Captain's Pearl via the chest puzzle
    d.go("sunken_ship")
    d.click("clam")
    d.click("chest"); assert d.flag("chest_open")
    d.click("pearl"); assert d.has("pearl")
    d.use("pearl", "clam"); assert d.flag("pearl_returned") and d.has("ship_key")
    d.click("clam")                                      # story
    d.use("ship_key", "treasure_door")
    d.click("glasses")
    # Shelly's Specs + Bubble Trouble + polish combo
    d.go("kelp_forest")
    d.click("shelly"); assert d.flag("met_shelly")
    d.use("glasses", "shelly"); assert d.flag("glasses_returned") and d.has("shell_polish")
    d.click("gear"); d.use("gear", "bubble_machine"); assert d.has("bubble_helmet")
    d.go("dark_cave"); d.finish_dialogue()
    d.click("bill"); d.use("bubble_helmet", "stuck_shell")
    game.use_item_on_item("shell_polish", "conch_shell"); d.finish_dialogue()
    assert d.flag("shell_shiny") and not d.has("shell_polish")
    # Festival extras
    d.go("festival_grounds")
    d.click("dance_floor"); d.click("cookie_table")
    d.use("conch_shell", "dj")
    assert d.flag("game_won")
    # the ending mentions every completed side quest
    texts = " ".join(s["text"] for s in game.ending_slides)
    for word in ("shine", "cookies", "Sidney", "Shelly", "Captain Clam"):
        assert word in texts


def test_wrong_item_never_consumes(game):
    d = Driver(game)
    d.finish_dialogue()
    d.click("coral"); d.click("grandma")
    d.go("kelp_forest"); d.click("gear")
    d.use("gear", "shelly")                              # nonsense use
    assert d.has("gear")
    d.use("gear", "puffer")                              # specific nudge
    assert d.has("gear")


def test_every_scene_renders_and_saves(game):
    d = Driver(game)
    d.finish_dialogue()
    for scene_id in game.content.scenes:
        d.go(scene_id)
        d.finish_dialogue()
        d.tick(5)
        for hs in d.scene().visible_hotspots():
            if hs["type"] == "humor":
                d.scene().interact(hs, None)
                d.finish_dialogue()
        game.hints.request_now()
        assert game.hints.text
        game.save_game(autosave=False)
        assert game.saves.load()["scene"] == scene_id


def test_hint_appears_after_inactivity(game):
    d = Driver(game)
    d.finish_dialogue()
    d.tick(2)
    game.hints.timer = 179.9
    d.tick(10)
    assert game.hints.visible
    game.hints.toggle()
    assert not game.hints.visible and not game.state.hints_enabled


def test_minigame_skip_rules(game):
    game.start_minigame("shell_puzzle", [{"set_flag": "reward"}])
    mg = game.minigame
    assert not mg.can_skip()
    mg.fails = 3
    assert mg.can_skip()
    mg.skip()
    assert game.minigame is None and game.state.has_flag("reward")
    game.start_minigame("bubble_catch", [{"set_flag": "reward2"}])
    game.minigame.time = 31
    game.minigame.skip()
    assert game.state.has_flag("reward2")
    game.start_minigame("crab_dance", [{"set_flag": "never"}], from_menu=True)
    game.minigame.finish()
    assert not game.state.has_flag("never"), "replays from the menu give no reward"
