# src/keyboard.py
"""Keyboard simulation for typing transcribed text."""
import ctypes
from pynput.keyboard import Controller, Key


class KeyboardTyper:
    """Types text into the active window."""

    def __init__(self):
        self._controller = Controller()

    def _is_caps_lock_on(self) -> bool:
        """Check if Caps Lock is currently on (Windows only)."""
        try:
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        except Exception:
            return False

    def _turn_off_caps_lock(self):
        """Turn off Caps Lock if it's on."""
        if self._is_caps_lock_on():
            self._controller.press(Key.caps_lock)
            self._controller.release(Key.caps_lock)

    def type_text(self, text: str):
        """Type the given text into the active window.

        Args:
            text: The text to type
        """
        if not text:
            return
        # Ensure Caps Lock is off before typing
        self._turn_off_caps_lock()
        self._controller.type(text)
