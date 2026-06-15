"""Intent classification.

Supports: turn_on, turn_off, set_value, query_state, execute_routine, clarify.
Ships a rule/keyword classifier (fallback) behind an interface that a real
model (e.g. Nemotron Nano) can implement.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

INTENTS = (
    "turn_on",
    "turn_off",
    "set_value",
    "query_state",
    "execute_routine",
    "clarify",
)

CONFIDENCE_THRESHOLD = 0.4


@dataclass
class IntentResult:
    intent: str
    confidence: float


class IntentClassifier(ABC):
    @abstractmethod
    def classify(self, text: str, routine_names: Iterable[str] = ()) -> IntentResult:
        raise NotImplementedError


class RuleIntentClassifier(IntentClassifier):
    """Keyword/regex based classifier covering English + Hindi/Hinglish."""

    ON_WORDS = ("turn on", "switch on", "start", "open", "lock", "on karo", "chalu", "jalao", "khol")
    OFF_WORDS = ("turn off", "switch off", "stop", "close", "unlock", "band karo", "bandh", "bujhao", "off karo")
    QUERY_WORDS = ("what", "what's", "whats", "how", "is the", "status", "kya hai", "kitna", "batao")
    SET_WORDS = ("set", "change", "make it", "increase", "decrease", "raise", "lower", "reduce", "badha", "kam", "karo")

    def classify(self, text: str, routine_names: Iterable[str] = ()) -> IntentResult:
        t = (text or "").lower().strip()
        if not t:
            return IntentResult("clarify", 0.0)

        for name in routine_names:
            if name.lower() in t:
                return IntentResult("execute_routine", 0.95)

        if any(w in t for w in self.QUERY_WORDS) and "?" in t or t.startswith(("what", "how")):
            return IntentResult("query_state", 0.85)
        if any(w in t for w in self.QUERY_WORDS) and not any(w in t for w in self.SET_WORDS):
            return IntentResult("query_state", 0.7)

        has_number = bool(re.search(r"\d", t))
        if any(w in t for w in self.SET_WORDS) and has_number:
            return IntentResult("set_value", 0.85)

        if any(w in t for w in self.OFF_WORDS):
            return IntentResult("turn_off", 0.8)
        if any(w in t for w in self.ON_WORDS):
            return IntentResult("turn_on", 0.8)

        if any(w in t for w in self.SET_WORDS) and has_number:
            return IntentResult("set_value", 0.6)

        return IntentResult("clarify", 0.2)
