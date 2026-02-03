# src/tray.py
"""System tray icon for status indication."""
from typing import Callable, Optional
import pystray
from PIL import Image, ImageDraw
import threading


class TrayIcon:
    """System tray icon showing dictation status."""

    COLORS = {
        "idle": "#808080",        # Gray
        "recording": "#ff4444",   # Red
        "transcribing": "#ffaa00",  # Orange
        "formatting": "#44ff44",  # Green
    }

    def __init__(
        self,
        on_quit: Optional[Callable[[], None]] = None,
    ):
        self._on_quit = on_quit or (lambda: None)
        self._status = "idle"
        self._icon: Optional[pystray.Icon] = None

    def _create_icon_image(self, color: str) -> Image.Image:
        """Create a simple colored circle icon."""
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, size - 4, size - 4], fill=color)
        return image

    def _create_menu(self):
        """Create the tray icon menu."""
        return pystray.Menu(
            pystray.MenuItem("Whisper Dictation", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: self._quit()),
        )

    def _quit(self):
        """Handle quit menu item."""
        self._on_quit()
        if self._icon:
            self._icon.stop()

    def set_status(self, status: str):
        """Update the tray icon to reflect current status."""
        self._status = status
        color = self.COLORS.get(status, self.COLORS["idle"])
        if self._icon:
            self._icon.icon = self._create_icon_image(color)

    def start(self):
        """Start the system tray icon."""
        self._icon = pystray.Icon(
            "whisper-dictation",
            self._create_icon_image(self.COLORS["idle"]),
            "Whisper Dictation",
            menu=self._create_menu(),
        )
        # Run in separate thread to not block
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        """Stop the system tray icon."""
        if self._icon:
            self._icon.stop()
