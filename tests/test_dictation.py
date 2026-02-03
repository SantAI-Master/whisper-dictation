# tests/test_dictation.py
from unittest.mock import Mock, patch
import numpy as np
import time
from src.dictation import DictationService


def test_service_records_on_hotkey_press():
    with patch("src.dictation.AudioRecorder") as mock_recorder_class, \
         patch("src.dictation.WhisperTranscriber"), \
         patch("src.dictation.TextFormatter"), \
         patch("src.dictation.KeyboardTyper"), \
         patch("src.dictation.HotkeyListener"):

        mock_recorder = Mock()
        mock_recorder_class.return_value = mock_recorder

        service = DictationService(api_key="test-key")
        service._on_hotkey_press()

        mock_recorder.start.assert_called_once()


def test_service_transcribes_and_formats_on_release():
    with patch("src.dictation.AudioRecorder") as mock_recorder_class, \
         patch("src.dictation.WhisperTranscriber") as mock_transcriber_class, \
         patch("src.dictation.TextFormatter") as mock_formatter_class, \
         patch("src.dictation.KeyboardTyper") as mock_typer_class, \
         patch("src.dictation.HotkeyListener"):

        mock_recorder = Mock()
        mock_recorder.stop.return_value = np.zeros(16000, dtype=np.float32)
        mock_recorder_class.return_value = mock_recorder

        mock_transcriber = Mock()
        mock_transcriber.transcribe.return_value = "hello world how are you"
        mock_transcriber_class.return_value = mock_transcriber

        mock_formatter = Mock()
        mock_formatter.format.return_value = "Hello, world! How are you?"
        mock_formatter_class.return_value = mock_formatter

        mock_typer = Mock()
        mock_typer_class.return_value = mock_typer

        service = DictationService(api_key="test-key")
        service._on_hotkey_press()  # Start recording
        service._on_hotkey_release()  # Stop, transcribe, format

        # Wait for background thread
        time.sleep(0.1)

        mock_recorder.stop.assert_called_once()
        mock_transcriber.transcribe.assert_called_once()
        mock_formatter.format.assert_called_once_with("hello world how are you")
        mock_typer.type_text.assert_called_once_with("Hello, world! How are you?")
