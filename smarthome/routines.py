"""Routines as macros: expand a routine name into device actions."""
from __future__ import annotations

from typing import Dict, List, Optional


class RoutineEngine:
    def __init__(self, routines: Dict[str, list]) -> None:
        self._routines = {k.lower(): v for k, v in routines.items()}

    def names(self) -> List[str]:
        return list(self._routines.keys())

    def expand(self, text: str) -> Optional[list]:
        """Return the action list for the first routine named in ``text``."""
        t = (text or "").lower()
        for name, actions in self._routines.items():
            if name in t:
                return actions
        return None
