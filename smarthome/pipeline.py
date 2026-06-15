"""End-to-end orchestrator wiring all components together."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .ambiguity import AmbiguityHandler, Context
from .asr import ASRAdapter, MockASR
from .devices import DeviceStore
from .intent import IntentClassifier, RuleIntentClassifier
from .response import MockTTS, Responder, TTSAdapter
from .routines import RoutineEngine
from .slots import RuleSlotExtractor, SlotExtractor


@dataclass
class TurnResult:
    text: str
    intent: str
    confidence: float
    slots: Dict[str, Any]
    success: bool
    response: str
    state_changes: List[str] = field(default_factory=list)


class Pipeline:
    def __init__(
        self,
        store: Optional[DeviceStore] = None,
        asr: Optional[ASRAdapter] = None,
        intent: Optional[IntentClassifier] = None,
        slots: Optional[SlotExtractor] = None,
        responder: Optional[Responder] = None,
        tts: Optional[TTSAdapter] = None,
    ) -> None:
        self.store = store or DeviceStore()
        self.asr = asr or MockASR()
        self.intent = intent or RuleIntentClassifier()
        self.slots = slots or RuleSlotExtractor()
        self.ambiguity = AmbiguityHandler()
        self.routines = RoutineEngine(self.store.routines)
        self.responder = responder or Responder()
        self.tts = tts or MockTTS()
        self.context = Context()

    def handle(self, audio_or_text: str) -> TurnResult:
        text = self.asr.transcribe(audio_or_text)
        intent_res = self.intent.classify(text, self.routines.names())
        slots = self.slots.extract(text, self.store.device_names())
        slot_dict = {
            "device": slots.device,
            "value": slots.value,
            "unit": slots.unit,
            "relative": slots.relative,
            "direction": slots.direction,
        }
        changes: List[str] = []

        # Routines
        if intent_res.intent == "execute_routine":
            actions = self.routines.expand(text)
            if not actions:
                return self._finish(text, intent_res, slot_dict, False, "unknown routine")
            for act in actions:
                changes.append(self._apply_action(act["intent"], act["device"], act.get("value")))
            return self._finish(text, intent_res, slot_dict, True, "routine complete", changes)

        # Low confidence / unrecognized
        if intent_res.intent == "clarify":
            return self._finish(text, intent_res, slot_dict, False, "I didn't understand that")

        # Resolve device (with context fallback)
        res = self.ambiguity.resolve(slots.device, self.store.device_names(), self.context)
        if res.needs_clarification:
            return self._finish(text, intent_res, slot_dict, False, res.message or "please clarify")
        device = res.device
        self.context.remember(device)

        if intent_res.intent == "turn_on":
            r = self.store.set_power(device, True)
        elif intent_res.intent == "turn_off":
            r = self.store.set_power(device, False)
        elif intent_res.intent == "set_value":
            if slots.value is None:
                return self._finish(text, intent_res, slot_dict, False, "no value provided")
            r = self.store.set_value(device, slots.value, slots.relative, slots.direction)
        elif intent_res.intent == "query_state":
            r = self.store.query(device)
        else:  # pragma: no cover - defensive
            return self._finish(text, intent_res, slot_dict, False, "unsupported intent")

        if r.ok:
            changes.append(r.message)
        return self._finish(text, intent_res, slot_dict, r.ok, r.message, changes)

    def _apply_action(self, intent: str, device: str, value: Optional[float]) -> str:
        if intent == "turn_on":
            return self.store.set_power(device, True).message
        if intent == "turn_off":
            return self.store.set_power(device, False).message
        if intent == "set_value" and value is not None:
            return self.store.set_value(device, value).message
        return f"skipped {intent} on {device}"

    def _finish(self, text, intent_res, slot_dict, ok, message, changes=None) -> TurnResult:
        reply = self.responder.generate(message, ok)
        self.tts.speak(reply)
        return TurnResult(
            text=text,
            intent=intent_res.intent,
            confidence=intent_res.confidence,
            slots=slot_dict,
            success=ok,
            response=reply,
            state_changes=changes or [],
        )


def _demo() -> None:
    p = Pipeline()
    for cmd in [
        "Turn on bedroom light",
        "Set AC to 24 degrees",
        "increase AC by 2 degrees",
        "What's the AC temperature?",
        "Goodnight",
        "bedroom light band karo",
    ]:
        out = p.handle(cmd)
        print(f"> {cmd}\n  intent={out.intent} ({out.confidence:.2f}) slots={out.slots}\n  {out.response}\n")


if __name__ == "__main__":
    _demo()
