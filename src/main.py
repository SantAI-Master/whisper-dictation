# src/main.py
"""Main entry point for Whisper Dictation."""
import os
import sys
import uvicorn
from dotenv import load_dotenv
from src.dictation import DictationService
from src.tray import TrayIcon
from src import server


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set in .env file")
        sys.exit(1)

    hotkey = os.getenv("HOTKEY", "ctrl_a")
    format_mode = os.getenv("FORMAT_MODE", "single-line")  # "single-line" or "document"

    tray = TrayIcon()

    def on_status_change(status: str):
        tray.set_status(status)
        server.update_status(status)

    def on_transcription(raw: str, formatted: str):
        server.add_transcription(formatted)

    dictation = DictationService(
        api_key=api_key,
        hotkey=hotkey,
        format_mode=format_mode,
        on_status_change=on_status_change,
        on_transcription=on_transcription,
    )

    def on_quit():
        dictation.stop()
        os._exit(0)

    tray._on_quit = on_quit

    # Wire up mode change callbacks
    server.set_mode_callback(
        on_change=dictation.set_format_mode,
        get_mode=dictation.get_format_mode,
    )

    print(f"Starting Whisper Dictation...")
    print(f"Hotkey: {hotkey}")
    print(f"Format mode: {format_mode}")
    print(f"Dashboard: http://localhost:8765")
    print(f"Hold {hotkey} to record, release to transcribe.")

    tray.start()
    dictation.start()

    uvicorn.run(server.app, host="127.0.0.1", port=8765, log_level="warning")


if __name__ == "__main__":
    main()
