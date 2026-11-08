"""Tiny declarative condition language used throughout the JSON content.

A condition is None (always true) or a dict with one or more of:
    {"flag": "x"}            flag x is set
    {"not_flag": "x"}        flag x is not set
    {"has": "item"}          item is in inventory
    {"not_has": "item"}      item is not in inventory
    {"counter_gte": ["name", n]}
    {"counter_lt": ["name", n]}
    {"all": [cond, ...]}
    {"any": [cond, ...]}
    {"not": cond}
Several keys in one dict are ANDed together.
"""


def check(cond, state) -> bool:
    if cond is None or cond == {}:
        return True
    if isinstance(cond, list):          # bare list == all
        return all(check(c, state) for c in cond)
    for key, value in cond.items():
        if key == "flag":
            if not state.has_flag(value):
                return False
        elif key == "not_flag":
            if state.has_flag(value):
                return False
        elif key == "has":
            if not state.inventory.has(value):
                return False
        elif key == "not_has":
            if state.inventory.has(value):
                return False
        elif key == "counter_gte":
            name, n = value
            if state.counters.get(name, 0) < n:
                return False
        elif key == "counter_lt":
            name, n = value
            if state.counters.get(name, 0) >= n:
                return False
        elif key == "all":
            if not all(check(c, state) for c in value):
                return False
        elif key == "any":
            if not any(check(c, state) for c in value):
                return False
        elif key == "not":
            if check(value, state):
                return False
        else:
            raise ValueError(f"Unknown condition key: {key!r}")
    return True


def pick(options, state, key="if"):
    """Return the first entry of `options` whose condition passes.

    `options` may be a plain value (returned as-is) or a list of dicts each
    optionally carrying a condition under `key`.
    """
    if not isinstance(options, list):
        return options
    for option in options:
        if isinstance(option, dict) and check(option.get(key), state):
            return option
    return None
