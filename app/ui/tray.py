"""
System tray integration using pystray matching Section 60 specifications.
"""

from __future__ import annotations
import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw

try:
    import pystray
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class TrayIconManager:
    """Manages the background system tray icon and menu actions."""

    def __init__(
        self,
        on_open: Optional[Callable[[], None]] = None,
        on_launch_workspace: Optional[Callable[[], None]] = None,
        on_sync_workspace: Optional[Callable[[], None]] = None,
        on_toggle_pause: Optional[Callable[[], None]] = None,
        on_view_logs: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
        is_paused: bool = False
    ):
        self.on_open = on_open
        self.on_launch_workspace = on_launch_workspace
        self.on_sync_workspace = on_sync_workspace
        self.on_toggle_pause = on_toggle_pause
        self.on_view_logs = on_view_logs
        self.on_exit = on_exit
        self.is_paused = is_paused

        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _create_icon_image(self) -> Image.Image:
        """Generates a 64x64 desktop workspace manager icon."""
        image = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # Draw 4 desktop quadrants
        draw.rectangle([6, 6, 28, 28], fill="#0067c0", outline="#ffffff", width=2)
        draw.rectangle([34, 6, 56, 28], fill="#107c41", outline="#ffffff", width=2)
        draw.rectangle([6, 34, 28, 56], fill="#d83b01", outline="#ffffff", width=2)
        draw.rectangle([34, 34, 56, 56], fill="#5c2d91", outline="#ffffff", width=2)
        return image

    def start(self) -> None:
        """Starts the system tray icon in a dedicated daemon thread."""
        if not TRAY_AVAILABLE:
            return

        pause_label = "Resume Automation" if self.is_paused else "Pause Automation"

        menu = pystray.Menu(
            pystray.MenuItem("Open Manager", lambda: self.on_open() if self.on_open else None, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Launch Workspace", lambda: self.on_launch_workspace() if self.on_launch_workspace else None),
            pystray.MenuItem("Sync Workspace", lambda: self.on_sync_workspace() if self.on_sync_workspace else None),
            pystray.MenuItem(pause_label, lambda: self._toggle_pause_action()),
            pystray.MenuItem("View Logs", lambda: self.on_view_logs() if self.on_view_logs else None),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda: self.on_exit() if self.on_exit else None)
        )

        self._icon = pystray.Icon("VirtualDesktopWorkspaceManager", self._create_icon_image(), "Virtual Desktop Workspace Manager", menu)
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def _toggle_pause_action(self) -> None:
        if self.on_toggle_pause:
            self.on_toggle_pause()

    def stop(self) -> None:
        """Stops the system tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
