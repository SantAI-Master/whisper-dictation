# tests/test_formatter.py
import pytest
from unittest.mock import Mock, patch
from src.formatter import TextFormatter


def test_formatter_requires_api_key():
    with pytest.raises(ValueError, match="API key"):
        TextFormatter(api_key="")


def test_formatter_cleans_up_text():
    with patch("src.formatter.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hello, world! How are you?"))]
        mock_client.chat.completions.create.return_value = mock_response

        formatter = TextFormatter(api_key="test-key")
        result = formatter.format("hello world how are you")

        assert result == "Hello, world! How are you?"
        mock_client.chat.completions.create.assert_called_once()


def test_formatter_handles_empty_text():
    with patch("src.formatter.OpenAI"):
        formatter = TextFormatter(api_key="test-key")
        result = formatter.format("")
        assert result == ""
