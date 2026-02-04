# Whisper Dictation

A Windows voice-to-text application that lets you dictate text anywhere using OpenAI's Whisper for transcription and GPT for intelligent formatting.

## What Problem Does This Solve?

Typing can be slow and tedious, especially for long messages, emails, or documents. Voice dictation tools exist, but they often produce messy output with poor punctuation, no paragraph breaks, and grammatical errors.

**Whisper Dictation** solves this by:
1. Recording your voice with a simple hold-to-talk hotkey
2. Transcribing your speech using OpenAI's Whisper (highly accurate)
3. Automatically formatting the text with GPT (proper grammar, punctuation, paragraphs, bullet points)
4. Typing the polished result directly into any application

Just hold Caps Lock, speak naturally, and release. Your formatted text appears wherever your cursor is.

## Features

- **Hold-to-Talk Recording** - Hold Caps Lock (or custom hotkey) to record, release to process
- **Whisper Transcription** - Industry-leading speech recognition via OpenAI's Whisper API
- **GPT Formatting** - Automatic grammar, punctuation, capitalization, and paragraph formatting
- **Universal Typing** - Works in any application (Word, browser, Notepad, etc.)
- **System Tray Icon** - Color-coded status indicator (gray=idle, red=recording, orange=transcribing, green=formatting)
- **Web Dashboard** - Real-time status and transcription history at `http://localhost:8765`
- **Audio Feedback** - Sound notification when recording starts
- **Auto-Start Option** - Can be configured to start with Windows

## Requirements

- **Windows 10/11** (uses Windows-specific features)
- **Python 3.10+**
- **OpenAI API Key** (required - you must provide your own)
- **Microphone**

## Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/YOUR_USERNAME/whisper-dictation.git
cd whisper-dictation
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure API Key

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in a text editor and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   HOTKEY=caps_lock
   ```

> **Important:** You must provide your own OpenAI API key. Get one at [platform.openai.com](https://platform.openai.com/api-keys). This app uses the Whisper API for transcription and GPT-4o-mini for formatting. Costs are typically a few cents per use.

## Usage

### Starting the App

```bash
python -m src.main
```

You should see:
```
Starting Whisper Dictation...
Hotkey: caps_lock
Dashboard: http://localhost:8765
Hold caps_lock to record, release to transcribe.
```

### Using Dictation

1. Place your cursor where you want text to appear
2. **Hold** Caps Lock (you'll hear a beep)
3. **Speak** naturally
4. **Release** Caps Lock
5. Wait a moment while it transcribes and formats
6. Your text appears automatically!

### Status Indicators

The system tray icon shows the current status:
- **Gray** - Idle, ready to record
- **Red** - Recording your voice
- **Orange** - Transcribing with Whisper
- **Green** - Formatting with GPT

### Web Dashboard

Open `http://localhost:8765` in your browser to see:
- Real-time status
- Recent transcription history

### Changing the Hotkey

Edit `.env` and change the `HOTKEY` value:
```
HOTKEY=caps_lock    # Default
HOTKEY=ctrl_r       # Right Ctrl key
HOTKEY=f13          # F13 key (if your keyboard has it)
```

### Auto-Start with Windows (Optional)

1. Copy `start.vbs.example` to `start.vbs`
2. Edit `start.vbs` and update the path to your installation folder
3. Press `Win+R`, type `shell:startup`, press Enter
4. Create a shortcut to `start.vbs` in the Startup folder

## Project Structure

```
whisper-dictation/
├── src/
│   ├── __init__.py       # Package marker
│   ├── main.py           # Entry point
│   ├── dictation.py      # Core orchestration service
│   ├── audio.py          # Microphone recording (16kHz)
│   ├── transcribe.py     # Whisper API client
│   ├── formatter.py      # GPT text formatting
│   ├── keyboard.py       # Keyboard simulation
│   ├── hotkey.py         # Global hotkey listener
│   ├── tray.py           # System tray icon
│   └── server.py         # FastAPI web dashboard
├── static/
│   ├── index.html        # Dashboard HTML
│   ├── style.css         # Dashboard styles
│   └── app.js            # Dashboard JavaScript
├── tests/                # Unit tests
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── start.vbs.example     # Windows launcher template
└── README.md             # This file
```

## How It Works

1. **Hotkey Detection** (`hotkey.py`) - Listens for global key events using `pynput`
2. **Audio Recording** (`audio.py`) - Captures microphone input at 16kHz using `sounddevice`
3. **Transcription** (`transcribe.py`) - Sends audio to OpenAI Whisper API as WAV
4. **Formatting** (`formatter.py`) - Sends raw text to GPT-4o-mini with formatting instructions
5. **Typing** (`keyboard.py`) - Simulates keyboard input to type the result
6. **Status Updates** - Tray icon and web dashboard update in real-time via WebSocket

## Dependencies

| Package | Purpose |
|---------|---------|
| `pynput` | Global hotkey listening and keyboard simulation |
| `sounddevice` | Microphone audio capture |
| `numpy` | Audio data processing |
| `openai` | Whisper and GPT API client |
| `fastapi` | Web dashboard server |
| `uvicorn` | ASGI server |
| `websockets` | Real-time dashboard updates |
| `pystray` | System tray icon |
| `Pillow` | Icon image generation |
| `python-dotenv` | Environment variable loading |

## Troubleshooting

### "OPENAI_API_KEY not set"
Make sure you created a `.env` file with your API key (see Installation Step 5).

### No sound when recording starts
Check that your system sounds are enabled. The app plays the Windows "Asterisk" sound.

### Text appears in ALL CAPS
The app automatically turns off Caps Lock before typing. If this still happens, try using a different hotkey like `ctrl_r`.

### Recording doesn't start
- Make sure no other app is using the hotkey
- Check that your microphone is working and set as default
- Try running as Administrator

### Transcription is inaccurate
- Speak clearly and at a normal pace
- Reduce background noise
- Get closer to your microphone

## API Costs

This app uses OpenAI's APIs which have usage-based pricing:
- **Whisper**: ~$0.006 per minute of audio
- **GPT-4o-mini**: ~$0.00015 per 1K input tokens, $0.0006 per 1K output tokens

A typical 30-second dictation costs less than $0.01.

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- [OpenAI](https://openai.com) for Whisper and GPT APIs
- [pynput](https://github.com/moses-palmer/pynput) for keyboard handling
- [FastAPI](https://fastapi.tiangolo.com) for the web framework
