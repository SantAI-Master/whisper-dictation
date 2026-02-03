# src/transcribe.py
"""Whisper API transcription client."""
import io
import numpy as np
from openai import OpenAI
import wave


class WhisperTranscriber:
    """Transcribes audio using OpenAI Whisper API."""

    SAMPLE_RATE = 16000

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self._client = OpenAI(api_key=api_key)

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio data to text.

        Args:
            audio: Float32 numpy array of audio samples at 16kHz

        Returns:
            Transcribed text string
        """
        # Convert float32 to int16 WAV format
        audio_int16 = (audio * 32767).astype(np.int16)

        # Create in-memory WAV file
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(self.SAMPLE_RATE)
            wav.writeframes(audio_int16.tobytes())

        buffer.seek(0)
        buffer.name = "audio.wav"

        # Send to Whisper API
        response = self._client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            response_format="text",
        )

        return response.strip() if isinstance(response, str) else response.text.strip()
