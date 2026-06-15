"""Device State Store.

Loads the registry JSON, maintains device state, validates value ranges,
and answers queries.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

DEFAULT_REGISTRY = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "device_registry.json"
)


@dataclass
class ActionResult:
    ok: bool
    message: str
    device: Optional[str] = None


class DeviceStore:
    def __init__(self, registry_path: str = DEFAULT_REGISTRY) -> None:
        with open(registry_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self._devices: Dict[str, dict] = {d["id"]: d for d in data["devices"]}
        self.routines: Dict[str, list] = data.get("routines", {})
        # name -> id lookup
        self._by_name = {d["name"].lower(): d["id"] for d in data["devices"]}

    # -- lookups -------------------------------------------------------
    def device_names(self) -> List[str]:
        return [d["name"] for d in self._devices.values()]

    def resolve_id(self, name_or_id: str) -> Optional[str]:
        if name_or_id in self._devices:
            return name_or_id
        return self._by_name.get((name_or_id or "").lower())

    def get(self, name_or_id: str) -> Optional[dict]:
        did = self.resolve_id(name_or_id)
        return self._devices.get(did) if did else None

    def snapshot(self) -> Dict[str, dict]:
        return {d["name"]: dict(d["state"]) for d in self._devices.values()}

    # -- actions -------------------------------------------------------
    def set_power(self, name_or_id: str, on: bool) -> ActionResult:
        dev = self.get(name_or_id)
        if not dev:
            return ActionResult(False, f"Unknown device: {name_or_id}")
        dev["state"]["power"] = "on" if on else "off"
        verb = "on" if on else "off"
        return ActionResult(True, f"{dev['name']} turned {verb}", dev["name"])

    def set_value(
        self, name_or_id: str, value: float, relative: bool = False, direction: int = 0
    ) -> ActionResult:
        dev = self.get(name_or_id)
        if not dev:
            return ActionResult(False, f"Unknown device: {name_or_id}")
        if "value" not in dev.get("value", {}) and "value" not in dev.get("state", {}):
            return ActionResult(False, f"{dev['name']} does not support values", dev["name"])

        spec = dev.get("value", {})
        current = dev["state"].get("value", spec.get("min", 0))
        target = current + direction * value if relative else value

        lo, hi = spec.get("min"), spec.get("max")
        if lo is not None and hi is not None and not (lo <= target <= hi):
            return ActionResult(
                False,
                f"{dev['name']} value must be between {lo} and {hi} {spec.get('unit','')}".strip(),
                dev["name"],
            )
        dev["state"]["value"] = target
        unit = spec.get("unit", "")
        return ActionResult(True, f"{dev['name']} set to {target} {unit}".strip(), dev["name"])

    def query(self, name_or_id: str) -> ActionResult:
        dev = self.get(name_or_id)
        if not dev:
            return ActionResult(False, f"Unknown device: {name_or_id}")
        state = dev["state"]
        if "value" in state:
            unit = dev.get("value", {}).get("unit", "")
            return ActionResult(True, f"{dev['name']} is {state['value']} {unit}".strip(), dev["name"])
        return ActionResult(True, f"{dev['name']} is {state.get('power','unknown')}", dev["name"])
