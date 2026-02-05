# src/dictation.py
"""Core dictation service orchestrating all components."""
import threading
import winsound
from typing import Callable, Optional
from src.audio import AudioRecorder
from src.transcribe import WhisperTranscriber
from src.formatter import TextFormatter
from src.keyboard import KeyboardTyper
from src.hotkey import HotkeyListener


class DictationService:
    """Main service that coordinates recording, transcription, formatting, and typing."""

    def __init__(
        self,
        api_key: str,
        hotkey: str = "ctrl_a",
        format_mode: str = "single-line",
        on_status_change: Optional[Callable[[str], None]] = None,
        on_transcription: Optional[Callable[[str, str], None]] = None,
    ):
        self._recorder = AudioRecorder()
        self._transcriber = WhisperTranscriber(api_key=api_key)
        self._formatter = TextFormatter(api_key=api_key, mode=format_mode)
        self._typer = KeyboardTyper()
        self._on_status_change = on_status_change or (lambda s: None)
        self._on_transcription = on_transcription or (lambda raw, fmt: None)

        self._hotkey_listener = HotkeyListener(
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release,
            hotkey=hotkey,
        )

    def _on_hotkey_press(self):
        """Called when hotkey is pressed - start recording."""
        # Start recording FIRST so audio capture is active before user hears the beep
        self._recorder.start()
        self._on_status_change("recording")
        # Play system asterisk sound asynchronously (instant, non-blocking)
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)

    def _on_hotkey_release(self):
        """Called when hotkey is released - stop, transcribe, format, type."""
        self._on_status_change("transcribing")
        audio = self._recorder.stop()

        if len(audio) < 1600:  # Less than 0.1 seconds
            self._on_status_change("idle")
            return

        # Transcribe and format in background to not block hotkey listener
        def transcribe_format_and_type():
            try:
                # Step 1: Transcribe audio to raw text
                raw_text = self._transcriber.transcribe(audio)
                if not raw_text:
                    return

                # Step 2: Format with GPT and type with streaming
                # Text appears as GPT generates it for faster perceived response
                self._on_status_change("formatting")
                formatted_text = self._formatter.format(
                    raw_text,
                    on_token=lambda token: self._typer.type_text(token)
                )

                # Notify transcription complete (for history)
                if formatted_text:
                    self._on_transcription(raw_text, formatted_text)
            finally:
                self._on_status_change("idle")

        threading.Thread(target=transcribe_format_and_type, daemon=True).start()

    def start(self):
        """Start the dictation service."""
        self._on_status_change("idle")
        self._hotkey_listener.start()

    def stop(self):
        """Stop the dictation service."""
        self._hotkey_listener.stop()

    def set_format_mode(self, mode: str):
        """Change the formatting mode at runtime."""
        self._formatter.set_mode(mode)

    def get_format_mode(self) -> str:
        """Get the current formatting mode."""
        return self._formatter.get_mode()
