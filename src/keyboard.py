# src/keyboard.py
"""Keyboard simulation for typing transcribed text."""
from pynput.keyboard import Controller


class KeyboardTyper:
    """Types text into the active window."""

    def __init__(self):
        self._controller = Controller()

    def type_text(self, text: str):
        """Type the given text into the active window.

        Args:
            text: The text to type
        """
        if not text:
            return
        self._controller.type(text)
