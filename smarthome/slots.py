"""Slot extraction.

Produces the slot schema: device, value, unit (optional), and a
relative/absolute flag. Fallback is regex/keyword based; a real model
(e.g. Nemotron Super) can implement ``SlotExtractor``.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

RELATIVE_UP = ("increase", "raise", "badha", "up", "more", "zyada")
RELATIVE_DOWN = ("decrease", "lower", "reduce", "kam", "down", "less")


@dataclass
class Slots:
    device: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    relative: bool = False
    direction: int = 0  # +1 up, -1 down, 0 absolute


class SlotExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, device_names: Sequence[str]) -> Slots:
        raise NotImplementedError


class RuleSlotExtractor(SlotExtractor):
    """Regex/keyword slot extractor with relative-value handling."""

    UNIT_WORDS = {
        "degree": "degrees", "degrees": "degrees", "celsius": "degrees",
        "volume": "volume", "speed": "speed", "percent": "percent", "%": "percent",
    }

    def extract(self, text: str, device_names: Sequence[str]) -> Slots:
        t = (text or "").lower()
        slots = Slots()

        # Device: longest matching registered name wins.
        match = None
        for name in sorted(device_names, key=len, reverse=True):
            if name.lower() in t:
                match = name
                break
        slots.device = match

        # Value
        num = re.search(r"-?\d+(?:\.\d+)?", t)
        if num:
            slots.value = float(num.group())
            if slots.value.is_integer():
                slots.value = int(slots.value)

        # Unit
        for word, unit in self.UNIT_WORDS.items():
            if word in t:
                slots.unit = unit
                break

        # Relative / absolute
        if any(w in t for w in RELATIVE_UP):
            slots.relative = True
            slots.direction = 1
        elif any(w in t for w in RELATIVE_DOWN):
            slots.relative = True
            slots.direction = -1

        return slots
