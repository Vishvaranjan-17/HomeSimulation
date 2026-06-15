"""Tests for the smart home pipeline using the fallback implementations."""
import json
import os

import pytest

from smarthome.devices import DeviceStore
from smarthome.pipeline import Pipeline

DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test_commands.json")


def load_cases():
    with open(DATA, "r", encoding="utf-8") as fh:
        return json.load(fh)["commands"]


def test_registry_has_min_devices():
    store = DeviceStore()
    assert len(store.device_names()) >= 8


def test_turn_on_off():
    p = Pipeline()
    on = p.handle("Turn on bedroom light")
    assert on.intent == "turn_on" and on.success
    assert p.store.get("bedroom light")["state"]["power"] == "on"
    off = p.handle("Turn off bedroom light")
    assert off.intent == "turn_off"
    assert p.store.get("bedroom light")["state"]["power"] == "off"


def test_set_absolute_value():
    p = Pipeline()
    out = p.handle("Set AC to 22 degrees")
    assert out.intent == "set_value" and out.success
    assert p.store.get("AC")["state"]["value"] == 22


def test_set_relative_value():
    p = Pipeline()
    p.handle("Set AC to 24 degrees")
    out = p.handle("increase AC by 2 degrees")
    assert out.slots["relative"] is True
    assert p.store.get("AC")["state"]["value"] == 26


def test_out_of_range_rejected():
    p = Pipeline()
    out = p.handle("Set AC to 99 degrees")
    assert out.success is False


def test_query_state():
    p = Pipeline()
    out = p.handle("What's the AC temperature?")
    assert out.intent == "query_state" and out.success


def test_context_memory_resolves_pronoun():
    p = Pipeline()
    p.handle("Turn on the TV")
    out = p.handle("Turn it off")  # no device named
    assert out.success
    assert p.store.get("TV")["state"]["power"] == "off"


def test_ambiguous_without_context_clarifies():
    p = Pipeline()
    out = p.handle("Turn it off")
    assert out.success is False


def test_routine_goodnight():
    p = Pipeline()
    out = p.handle("Goodnight")
    assert out.intent == "execute_routine" and out.success
    assert p.store.get("bedroom light")["state"]["power"] == "off"
    assert p.store.get("door lock")["state"]["power"] == "on"


def test_hinglish_turn_off():
    p = Pipeline()
    out = p.handle("bedroom light band karo")
    assert out.intent == "turn_off"
    assert p.store.get("bedroom light")["state"]["power"] == "off"


@pytest.mark.parametrize("case", load_cases())
def test_intent_accuracy(case):
    p = Pipeline()
    # seed context for ambiguous cases so they resolve
    if case.get("ambiguous"):
        p.handle("Turn on the AC")
    out = p.handle(case["text"])
    assert out.intent == case["intent"], f"{case['text']}: {out.intent} != {case['intent']}"
