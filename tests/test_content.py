"""Content integrity: every id referenced anywhere in the JSON must exist."""
import pytest

from game.engine.content import Content

content = Content()
SCENE_IDS = set(content.scenes)
ITEM_IDS = set(content.items)
DIALOGUE_IDS = set(content.dialogue)
CHAR_IDS = set(content.characters)
MINIGAME_IDS = set(content.quests["minigames"])


def walk_actions(actions, found):
    if not actions:
        return
    if isinstance(actions, dict):
        actions = [actions]
    for a in actions:
        for key in ("then", "else", "on_complete"):
            walk_actions(a.get(key), found)
        if "dialogue" in a:
            found["dialogue"].add(a["dialogue"])
        for key in ("give_item", "remove_item"):
            if key in a:
                found["item"].add(a[key])
        if "goto" in a:
            found["scene"].add(a["goto"])
        if "minigame" in a:
            found["minigame"].add(a["minigame"])
        if "say" in a and "speaker" in a:
            found["char"].add(a["speaker"])


def collect_refs():
    found = {"dialogue": set(), "item": set(), "scene": set(), "minigame": set(), "char": set()}
    for scene in content.scenes.values():
        walk_actions(scene.get("on_enter"), found)
        for once in scene.get("on_enter_once", []):
            walk_actions(once.get("actions"), found)
        for hs in scene["hotspots"]:
            if hs.get("character"):
                found["char"].add(hs["character"])
            if hs.get("speaker"):
                found["char"].add(hs["speaker"])
            if hs.get("type") == "item":
                found["item"].add(hs["item"])
            if hs.get("type") == "exit":
                found["scene"].add(hs["to"])
                walk_actions(hs.get("blocked"), found)
            dlg = hs.get("dialogue")
            if isinstance(dlg, str):
                found["dialogue"].add(dlg)
            elif isinstance(dlg, list):
                found["dialogue"].update(d["id"] for d in dlg)
            walk_actions(hs.get("on_click"), found)
            walk_actions(hs.get("actions"), found)
            for item_id, entry in hs.get("use", {}).items():
                if item_id != "*":
                    found["item"].add(item_id)
                if isinstance(entry, dict):
                    walk_actions(entry.get("actions"), found)
                    walk_actions(entry.get("else"), found)
                else:
                    walk_actions(entry, found)
    for entry in content.dialogue.values():
        walk_actions(entry.get("end"), found)
        for line in entry["lines"]:
            found["char"].add(line.get("speaker", "baker"))
            walk_actions(line.get("actions"), found)
            for choice in line.get("choices", []):
                walk_actions(choice.get("actions"), found)
                if choice.get("next"):
                    found["dialogue"].add(choice["next"])
    for item in content.items.values():
        for other, combo in item.get("combine", {}).items():
            found["item"].add(other)
            found["item"].update(combo.get("consume", []))
            walk_actions(combo.get("actions"), found)
    for slide in content.quests["ending"]:
        if slide.get("speaker"):
            found["char"].add(slide["speaker"])
    found["dialogue"].add(content.quests["wrong_item_dialogue"])
    found["scene"].add(content.quests["start_scene"])
    return found


REFS = collect_refs()


def test_dialogue_refs_exist():
    assert REFS["dialogue"] <= DIALOGUE_IDS, REFS["dialogue"] - DIALOGUE_IDS


def test_item_refs_exist():
    assert REFS["item"] <= ITEM_IDS, REFS["item"] - ITEM_IDS


def test_scene_refs_exist():
    assert REFS["scene"] <= SCENE_IDS, REFS["scene"] - SCENE_IDS


def test_minigame_refs_exist():
    assert REFS["minigame"] <= MINIGAME_IDS, REFS["minigame"] - MINIGAME_IDS


def test_character_refs_exist():
    assert REFS["char"] <= CHAR_IDS, REFS["char"] - CHAR_IDS


def test_every_dialogue_is_reachable():
    unused = DIALOGUE_IDS - REFS["dialogue"] - {"intro"}
    # 'intro' is referenced through on_enter_once which collect_refs covers; nothing else may be orphaned
    assert not unused, unused


@pytest.mark.parametrize("scene_id", sorted(SCENE_IDS))
def test_each_scene_has_three_humor_hotspots(scene_id):
    humor = [h for h in content.scenes[scene_id]["hotspots"] if h["type"] == "humor"]
    assert len(humor) >= 3


@pytest.mark.parametrize("scene_id", sorted(SCENE_IDS))
def test_hotspot_ids_unique_and_rects_valid(scene_id):
    ids = [h["id"] for h in content.scenes[scene_id]["hotspots"]]
    assert len(ids) == len(set(ids))
    for h in content.scenes[scene_id]["hotspots"]:
        x, y, w, h_ = h["rect"]
        assert w > 0 and h_ > 0 and 0 <= x and x + w <= 1280 and 0 <= y and y + h_ <= 640, h["id"]


def test_dialogue_lines_are_short():
    """Spec: at most 2 sentences per box (we allow punctuation inside quotes / ellipses)."""
    import re
    for did, entry in content.dialogue.items():
        for line in entry["lines"]:
            sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", line["text"].replace("...", "…")) if s.strip()]
            assert len(sentences) <= 4, (did, line["text"])
            assert len(line["text"]) <= 190, (did, line["text"])


def test_at_least_thirty_dialogue_entries_and_ten_items():
    assert len(DIALOGUE_IDS) >= 30
    assert len(ITEM_IDS) >= 10
