# src/audio.py
"""Audio recording from microphone."""
import numpy as np
import sounddevice as sd
from threading import Lock


class AudioRecorder:
    """Records audio from the default microphone."""

    SAMPLE_RATE = 16000  # Whisper expects 16kHz
    CHANNELS = 1

    def __init__(self):
        self.is_recording = False
        self._audio_chunks: list[np.ndarray] = []
        self._lock = Lock()
        self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio chunk."""
        if self.is_recording:
            with self._lock:
                self._audio_chunks.append(indata.copy())

    def start(self):
        """Start recording audio."""
        self._audio_chunks = []
        self.is_recording = True
        self._stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype=np.float32,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return the audio data."""
        self.is_recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._audio_chunks:
                return np.array([], dtype=np.float32)
            return np.concatenate(self._audio_chunks, axis=0).flatten()
