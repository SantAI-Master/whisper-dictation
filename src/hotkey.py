# src/hotkey.py
"""Global hotkey listener for hold-to-talk."""
from typing import Callable
from pynput.keyboard import Key, Listener, KeyCode


class HotkeyListener:
    """Listens for global hotkey press/release events."""

    def __init__(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        hotkey: str = "ctrl_a",
    ):
        self._on_press = on_press
        self._on_release = on_release
        self._hotkey = self._parse_hotkey(hotkey)
        self._is_combo = isinstance(self._hotkey, tuple)
        self._ctrl_pressed = False
        self._is_pressed = False
        self._listener = None

    def _parse_hotkey(self, hotkey: str):
        """Convert hotkey string to pynput Key or KeyCode."""
        # Special keys
        special_keys = {
            "caps_lock": Key.caps_lock,
            "ctrl_r": Key.ctrl_r,
            "ctrl_l": Key.ctrl_l,
            "alt_r": Key.alt_r,
            "f13": Key.f13,
        }

        # Handle combo keys like "ctrl_a"
        if hotkey == "ctrl_a":
            return ("ctrl", KeyCode.from_char('a'))

        return special_keys.get(hotkey, Key.caps_lock)

    def _handle_press(self, key):
        """Handle key press event."""
        if self._is_combo:
            # For combo like Ctrl+A, track modifier and key separately
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self._ctrl_pressed = True
            elif self._ctrl_pressed and key == self._hotkey[1]:
                if not self._is_pressed:
                    self._is_pressed = True
                    self._on_press()
        else:
            if key == self._hotkey and not self._is_pressed:
                self._is_pressed = True
                self._on_press()

    def _handle_release(self, key):
        """Handle key release event."""
        if self._is_combo:
            # Release on Ctrl release or A release
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self._ctrl_pressed = False
                if self._is_pressed:
                    self._is_pressed = False
                    self._on_release()
            elif key == self._hotkey[1] and self._is_pressed:
                self._is_pressed = False
                self._on_release()
        else:
            if key == self._hotkey and self._is_pressed:
                self._is_pressed = False
                self._on_release()

    def start(self):
        """Start listening for hotkey events."""
        self._listener = Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
            suppress=False,
        )
        self._listener.start()

    def stop(self):
        """Stop listening for hotkey events."""
        if self._listener:
            self._listener.stop()
            self._listener = None
