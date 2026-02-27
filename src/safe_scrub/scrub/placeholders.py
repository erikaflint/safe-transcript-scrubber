from __future__ import annotations

from collections import defaultdict


class PlaceholderAssigner:
    def __init__(self) -> None:
        self._value_to_placeholder: dict[tuple[str, str], str] = {}
        self._counts: defaultdict[str, int] = defaultdict(int)

    def assign(self, label: str, original_value: str) -> str:
        key = (label, original_value)
        if key not in self._value_to_placeholder:
            self._counts[label] += 1
            self._value_to_placeholder[key] = f"[{label}_{self._counts[label]}]"
        return self._value_to_placeholder[key]
