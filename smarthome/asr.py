"""Automatic Speech Recognition adapters.

Provides a fallback ``MockASR`` (text passthrough) that runs anywhere, and a
``WhisperASR`` adapter stub that wires in Whisper Medium when installed.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ASRAdapter(ABC):
    """Interface for speech-to-text engines."""

    @abstractmethod
    def transcribe(self, audio_or_text: str) -> str:
        """Return recognized text for the given audio path or raw text."""
        raise NotImplementedError


class MockASR(ASRAdapter):
    """Fallback ASR that treats its input as already-transcribed text."""

    def transcribe(self, audio_or_text: str) -> str:
        return (audio_or_text or "").strip()


class WhisperASR(ASRAdapter):
    """Adapter for OpenAI Whisper. Requires ``openai-whisper`` to be installed."""

    def __init__(self, model_size: str = "medium") -> None:
        try:
            import whisper  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "openai-whisper is not installed. Install it or use MockASR."
            ) from exc
        self._model = whisper.load_model(model_size)

    def transcribe(self, audio_or_text: str) -> str:  # pragma: no cover
        result = self._model.transcribe(audio_or_text)
        return str(result.get("text", "")).strip()
