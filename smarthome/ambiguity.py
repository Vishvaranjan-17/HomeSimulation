"""Ambiguity resolution and conversation context memory.

Strategy:
- single exact device match -> use it
- no device, but a recent device in (unexpired) context -> use that
- multiple/zero candidates -> emit a clarify request
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

CONTEXT_TTL_SECONDS = 120.0


@dataclass
class Context:
    last_device: Optional[str] = None
    last_updated: float = field(default_factory=time.time)

    def remember(self, device: Optional[str]) -> None:
        if device:
            self.last_device = device
            self.last_updated = time.time()

    def recent_device(self, now: Optional[float] = None) -> Optional[str]:
        now = time.time() if now is None else now
        if self.last_device and (now - self.last_updated) <= CONTEXT_TTL_SECONDS:
            return self.last_device
        return None


@dataclass
class Resolution:
    device: Optional[str]
    needs_clarification: bool
    message: Optional[str] = None
    candidates: List[str] = field(default_factory=list)


class AmbiguityHandler:
    """Resolve which device a command targets, using context as a fallback."""

    def resolve(
        self,
        extracted_device: Optional[str],
        all_devices: List[str],
        context: Context,
    ) -> Resolution:
        if extracted_device:
            return Resolution(device=extracted_device, needs_clarification=False)

        recent = context.recent_device()
        if recent:
            return Resolution(device=recent, needs_clarification=False)

        return Resolution(
            device=None,
            needs_clarification=True,
            message="Which device did you mean?",
            candidates=all_devices,
        )
