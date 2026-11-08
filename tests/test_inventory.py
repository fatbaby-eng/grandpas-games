from game.engine.inventory import Inventory


def test_add_and_has():
    inv = Inventory()
    assert inv.add("gear")
    assert inv.has("gear")
    assert "gear" in inv
    assert len(inv) == 1


def test_add_duplicate_is_ignored():
    inv = Inventory()
    inv.add("gear")
    assert not inv.add("gear")
    assert inv.items() == ["gear"]


def test_remove():
    inv = Inventory()
    inv.add("gear")
    assert inv.remove("gear")
    assert not inv.has("gear")
    assert not inv.remove("gear")


def test_select_toggle_and_deselect():
    inv = Inventory()
    inv.add("gear")
    inv.add("lantern")
    inv.toggle_select("gear")
    assert inv.selected_item() == "gear"
    inv.toggle_select("gear")                 # click again -> deselect
    assert inv.selected_item() is None
    inv.toggle_select("gear")
    inv.toggle_select("lantern")               # click another -> switch selection
    assert inv.selected_item() == "lantern"
    inv.deselect()
    assert inv.selected_item() is None


def test_cannot_select_missing_item():
    inv = Inventory()
    inv.select("nothing")
    assert inv.selected_item() is None


def test_remove_selected_clears_selection():
    inv = Inventory()
    inv.add("gear")
    inv.select("gear")
    inv.remove("gear")
    assert inv.selected_item() is None


def test_on_change_callback_fires():
    calls = []
    inv = Inventory(on_change=lambda: calls.append(1))
    inv.add("gear")
    inv.remove("gear")
    inv.load_list(["a", "b", "a"])
    assert len(calls) == 3
    assert inv.items() == ["a", "b"]
