"""Automatic Speech Recognition adapters.

Provides a fallback ``MockASR`` (text passthrough) that runs anywhere,
a ``WhisperASR`` adapter that wires in Whisper Medium when installed,
and a ``BrowserAudioASR`` that accepts raw audio bytes from the browser
microphone (via audio-recorder-streamlit) and transcribes them.
"""
from __future__ import annotations

import os
import tempfile
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


class BrowserAudioASR(ASRAdapter):
    """Accepts raw audio bytes from the browser microphone widget,
    writes them to a temp WAV file, and transcribes via WhisperASR.
    Falls back to MockASR if openai-whisper is not installed.
    """

    def __init__(self, model_size: str = "base") -> None:
        self._whisper_available = False
        try:
            self._backend = WhisperASR(model_size=model_size)
            self._whisper_available = True
        except ImportError:
            self._backend = MockASR()

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes captured from the browser."""
        if not self._whisper_available:
            return ""  # no text without Whisper; UI will show fallback message

        suffix = ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            return self._backend.transcribe(tmp_path)
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def transcribe(self, audio_or_text: str) -> str:
        """Passthrough for pipeline compatibility (text input fallback)."""
        return self._backend.transcribe(audio_or_text)
