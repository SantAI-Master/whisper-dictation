# tests/test_audio.py
import numpy as np
from src.audio import AudioRecorder


def test_recorder_starts_and_stops():
    recorder = AudioRecorder()
    recorder.start()
    assert recorder.is_recording is True
    recorder.stop()
    assert recorder.is_recording is False


def test_recorder_captures_audio_data():
    recorder = AudioRecorder()
    recorder.start()
    # Record for a brief moment
    import time
    time.sleep(0.5)
    audio_data = recorder.stop()
    assert audio_data is not None
    assert isinstance(audio_data, np.ndarray)
    assert len(audio_data) > 0
