# tests/test_keyboard.py
from unittest.mock import Mock, patch
from src.keyboard import KeyboardTyper


def test_typer_types_text():
    with patch("src.keyboard.Controller") as mock_controller_class:
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        typer = KeyboardTyper()
        typer.type_text("Hello")

        mock_controller.type.assert_called_once_with("Hello")


def test_typer_handles_empty_text():
    with patch("src.keyboard.Controller") as mock_controller_class:
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        typer = KeyboardTyper()
        typer.type_text("")

        mock_controller.type.assert_not_called()
