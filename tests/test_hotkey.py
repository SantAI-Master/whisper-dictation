# tests/test_hotkey.py
from unittest.mock import Mock
from pynput.keyboard import Key
from src.hotkey import HotkeyListener


def test_listener_calls_on_press_for_combo():
    """Test that Ctrl+A combo triggers on_press."""
    on_press = Mock()
    on_release = Mock()
    listener = HotkeyListener(on_press=on_press, on_release=on_release, hotkey="ctrl_a")

    # Simulate Ctrl press, then A press
    listener._handle_press(Key.ctrl_l)
    on_press.assert_not_called()  # Not yet - need both keys

    listener._handle_press(listener._hotkey[1])  # Press 'a'
    on_press.assert_called_once()


def test_listener_calls_on_release_for_combo():
    """Test that releasing Ctrl or A triggers on_release."""
    on_press = Mock()
    on_release = Mock()
    listener = HotkeyListener(on_press=on_press, on_release=on_release, hotkey="ctrl_a")

    # Simulate full press cycle
    listener._handle_press(Key.ctrl_l)
    listener._handle_press(listener._hotkey[1])  # Press 'a'
    listener._handle_release(listener._hotkey[1])  # Release 'a'

    on_release.assert_called_once()


def test_listener_ignores_other_keys():
    """Test that non-hotkey keys are ignored."""
    on_press = Mock()
    on_release = Mock()
    listener = HotkeyListener(on_press=on_press, on_release=on_release, hotkey="ctrl_a")

    # Simulate different key
    listener._handle_press(Key.shift)
    on_press.assert_not_called()


def test_listener_single_key_mode():
    """Test single key mode (e.g., caps_lock)."""
    on_press = Mock()
    on_release = Mock()
    listener = HotkeyListener(on_press=on_press, on_release=on_release, hotkey="caps_lock")

    # Simulate caps lock press
    listener._handle_press(Key.caps_lock)
    on_press.assert_called_once()

    listener._handle_release(Key.caps_lock)
    on_release.assert_called_once()
