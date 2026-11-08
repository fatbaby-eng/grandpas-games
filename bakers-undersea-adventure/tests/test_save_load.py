import json

from game.engine.save_load import SaveManager
from game.engine.state import GameState


def make_state():
    state = GameState(start_scene="dark_cave", start_pos=(300, 555))
    state.set_flag("main_conch")
    state.set_flag("found_bill")
    state.inc("grandma_talks")
    state.inc("grandma_talks")
    state.inventory.add("lantern")
    state.inventory.add("cookie")
    state.hints_enabled = False
    state.minigames_done.add("bubble_catch")
    state.play_time = 123.4
    return state


def test_round_trip(tmp_path):
    saves = SaveManager(tmp_path / "save.json")
    assert not saves.exists()
    state = make_state()
    saves.save(state.to_dict())
    assert saves.exists()

    loaded = GameState.from_dict(saves.load())
    assert loaded.scene_id == "dark_cave"
    assert loaded.player_pos == [300, 555]
    assert loaded.inventory.items() == ["lantern", "cookie"]
    assert loaded.flags == {"main_conch", "found_bill"}
    assert loaded.counters == {"grandma_talks": 2}
    assert loaded.hints_enabled is False
    assert loaded.minigames_done == {"bubble_catch"}
    assert loaded.play_time == 123.4


def test_load_missing_returns_none(tmp_path):
    assert SaveManager(tmp_path / "nothing.json").load() is None


def test_corrupt_file_returns_none(tmp_path):
    path = tmp_path / "save.json"
    path.write_text("{not json")
    assert SaveManager(path).load() is None


def test_newer_version_is_rejected(tmp_path):
    path = tmp_path / "save.json"
    path.write_text(json.dumps({"version": 999}))
    assert SaveManager(path).load() is None


def test_delete(tmp_path):
    saves = SaveManager(tmp_path / "save.json")
    saves.save(GameState().to_dict())
    saves.delete()
    assert not saves.exists()
    saves.delete()      # idempotent


def test_save_is_valid_json_with_version(tmp_path):
    saves = SaveManager(tmp_path / "save.json")
    saves.save(GameState().to_dict())
    data = json.loads((tmp_path / "save.json").read_text())
    assert data["version"] == 1
    assert data["scene"] == "coral_reef"
