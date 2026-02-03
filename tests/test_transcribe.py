# tests/test_transcribe.py
import numpy as np
import pytest
from unittest.mock import Mock, patch
from src.transcribe import WhisperTranscriber


def test_transcriber_requires_api_key():
    with pytest.raises(ValueError, match="API key"):
        WhisperTranscriber(api_key="")


def test_transcriber_sends_audio_to_api():
    with patch("src.transcribe.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = Mock(text="Hello world")

        transcriber = WhisperTranscriber(api_key="test-key")

        # Create fake audio data (1 second of silence)
        audio = np.zeros(16000, dtype=np.float32)
        result = transcriber.transcribe(audio)

        assert result == "Hello world"
        mock_client.audio.transcriptions.create.assert_called_once()
