"""Inventory model. Rendering of the inventory bar lives in ui.py."""


class Inventory:
    def __init__(self, on_change=None):
        self._items: list[str] = []
        self._selected: str | None = None
        self.on_change = on_change

    # Mutation -------------------------------------------------------------
    def add(self, item_id: str) -> bool:
        if item_id in self._items:
            return False
        self._items.append(item_id)
        self._changed()
        return True

    def remove(self, item_id: str) -> bool:
        if item_id not in self._items:
            return False
        self._items.remove(item_id)
        if self._selected == item_id:
            self._selected = None
        self._changed()
        return True

    def clear(self):
        self._items.clear()
        self._selected = None
        self._changed()

    # Queries --------------------------------------------------------------
    def has(self, item_id: str) -> bool:
        return item_id in self._items

    def items(self) -> list[str]:
        return list(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, item_id):
        return item_id in self._items

    # Selection ------------------------------------------------------------
    def selected_item(self) -> str | None:
        return self._selected

    def select(self, item_id: str | None):
        if item_id is not None and item_id not in self._items:
            return
        self._selected = item_id

    def deselect(self):
        self._selected = None

    def toggle_select(self, item_id: str):
        """Click an item to select it; click it again to deselect it."""
        if self._selected == item_id:
            self._selected = None
        else:
            self.select(item_id)

    # Persistence ----------------------------------------------------------
    def to_list(self) -> list[str]:
        return list(self._items)

    def load_list(self, items):
        self._items = list(dict.fromkeys(items))
        self._selected = None
        self._changed()

    def _changed(self):
        if self.on_change:
            self.on_change()
