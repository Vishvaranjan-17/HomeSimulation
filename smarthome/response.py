"""Response generation and TTS adapters.

``TemplateResponder`` builds natural replies (fallback). ``MockTTS`` returns
the text; ``GTTSAdapter`` is a stub for real speech synthesis via gTTS.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class Responder:
    """Turn an outcome message into a user-facing reply."""

    def generate(self, message: str, ok: bool = True) -> str:
        if not ok:
            return f"Sorry, {message}."
        return f"{message}."


class TTSAdapter(ABC):
    @abstractmethod
    def speak(self, text: str) -> str:
        """Render text to speech. Returns the text (or output path)."""
        raise NotImplementedError


class MockTTS(TTSAdapter):
    def speak(self, text: str) -> str:
        return text


class GTTSAdapter(TTSAdapter):  # pragma: no cover - optional dependency
    def __init__(self, lang: str = "en") -> None:
        try:
            from gtts import gTTS  # type: ignore  # noqa: F401
        except ImportError as exc:
            raise ImportError("gTTS is not installed. Install it or use MockTTS.") from exc
        self._lang = lang

    def speak(self, text: str, out_path: str = "response.mp3") -> str:
        from gtts import gTTS  # type: ignore

        gTTS(text=text, lang=self._lang).save(out_path)
        return out_path
