"""
Documented fallback provider utilizing simulated keyboard shortcuts.
Used strictly as a secondary fallback if Windows COM Virtual Desktop interfaces fail.
"""

from __future__ import annotations
import time
from typing import Optional
from app.logging.logger import get_logger

try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class KeyboardFallbackProvider:
    """
    Fallback mechanism using Win32 SendInput or key events.
    Isolate here to satisfy Section 25 and Section 100 requirements.
    """

    def __init__(self):
        self.logger = get_logger()

    def is_available(self) -> bool:
        return WIN32_AVAILABLE

    def switch_desktop_relative(self, steps: int) -> bool:
        """
        Sends Win+Ctrl+Left / Right keys to switch desktops relatively.
        Saves and restores focus.
        """
        if not WIN32_AVAILABLE or steps == 0:
            return False

        self.logger.warning("Using keyboard shortcut fallback to switch desktop.")
        try:
            fg_hwnd = win32gui.GetForegroundWindow()
            vk_direction = 0x27 if steps > 0 else 0x25  # VK_RIGHT or VK_LEFT

            for _ in range(abs(steps)):
                # Press Win + Ctrl
                win32api.keybd_event(win32con.VK_LWIN, 0, 0, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                # Press Direction
                win32api.keybd_event(vk_direction, 0, 0, 0)
                time.sleep(0.05)
                # Release Direction
                win32api.keybd_event(vk_direction, 0, win32con.KEYEVENTF_KEYUP, 0)
                # Release Win + Ctrl
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)

            # Restore focus
            if fg_hwnd and win32gui.IsWindow(fg_hwnd):
                win32gui.SetForegroundWindow(fg_hwnd)

            return True
        except Exception as ex:
            self.logger.error(f"Keyboard fallback switch failed: {ex}")
            return False
