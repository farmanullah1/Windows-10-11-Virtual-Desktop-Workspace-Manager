"""
Production Window Service providing top-level window enumeration,
filtering of ghost/helper windows, and policy-based matching.
"""

from __future__ import annotations
import os
import re
from typing import List, Optional
from app.providers.base import IWindowProvider, WindowInfo
from app.models.workspace import WindowPolicy
from app.logging.logger import get_logger

try:
    import win32gui
    import win32process
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowService(IWindowProvider):
    """Enumerates and evaluates top-level application windows on Windows."""

    def __init__(self):
        self.logger = get_logger()

    def _is_usable_top_level_window(self, hwnd: int) -> bool:
        """Determines if HWND represents an actual user-facing application window."""
        if not WIN32_AVAILABLE:
            return False

        try:
            if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                return False

            # Exclude windows with empty titles or purely system classes
            title = win32gui.GetWindowText(hwnd).strip()
            if not title:
                return False

            # Check window rect (must not be 0x0)
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if width <= 0 or height <= 0:
                return False

            # Check styles
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

            # Ignore child windows
            if style & win32con.WS_CHILD:
                return False

            # Ignore tool windows unless explicitly marked as app window
            if (ex_style & win32con.WS_EX_TOOLWINDOW) and not (ex_style & win32con.WS_EX_APPWINDOW):
                return False

            # Ignore shell/system classes like Program Manager or Taskbar
            class_name = win32gui.GetClassName(hwnd)
            ignored_classes = {
                "Progman", "Shell_TrayWnd", "Windows.UI.Core.CoreWindow",
                "ApplicationFrameWindow", "NarratorHelperWindow"
            }
            if class_name in ignored_classes and not title:
                return False

            return True
        except Exception:
            return False

    def _build_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        try:
            if not self._is_usable_top_level_window(hwnd):
                return None

            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            placement = win32gui.GetWindowPlacement(hwnd)
            is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            is_maximized = placement[1] == win32con.SW_SHOWMAXIMIZED

            return WindowInfo(
                hwnd=hwnd,
                title=title,
                pid=pid,
                executable="",
                is_visible=True,
                is_minimized=is_minimized,
                is_maximized=is_maximized,
                class_name=class_name
            )
        except Exception:
            return None

    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        if not WIN32_AVAILABLE:
            return None
        return self._build_window_info(hwnd)

    def get_all_top_level_windows(self) -> List[WindowInfo]:
        if not WIN32_AVAILABLE:
            return []

        results: List[WindowInfo] = []

        def enum_callback(hwnd, _):
            try:
                info = self._build_window_info(hwnd)
                if info:
                    results.append(info)
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as ex:
            self.logger.debug(f"EnumWindows notice: {ex}")

        return results

    def find_windows_for_process(self, pid: int) -> List[WindowInfo]:
        """Finds all visible, top-level windows belonging to the given PID."""
        all_windows = self.get_all_top_level_windows()
        return [w for w in all_windows if w.pid == pid]

    def find_windows_for_processes(self, pids: List[int]) -> List[WindowInfo]:
        """Finds all visible, top-level windows belonging to any of the PIDs."""
        pid_set = set(pids)
        all_windows = self.get_all_top_level_windows()
        return [w for w in all_windows if w.pid in pid_set]

    def find_windows_by_title(self, title_query: str, is_regex: bool = False) -> List[WindowInfo]:
        all_windows = self.get_all_top_level_windows()
        results: List[WindowInfo] = []

        pattern = None
        if is_regex:
            try:
                pattern = re.compile(title_query, re.IGNORECASE)
            except re.error:
                pattern = None

        for w in all_windows:
            if pattern:
                if pattern.search(w.title):
                    results.append(w)
            else:
                if title_query.lower() in w.title.lower():
                    results.append(w)

        return results

    def select_windows_by_policy(
        self,
        candidate_windows: List[WindowInfo],
        policy: str = WindowPolicy.MAIN_ONLY.value,
        title_pattern: str = ""
    ) -> List[WindowInfo]:
        """Filters candidate windows based on application's WindowPolicy."""
        if not candidate_windows:
            return []

        if policy == WindowPolicy.ALL_MATCHING.value:
            return candidate_windows

        elif policy == WindowPolicy.TITLE_CONTAINS.value and title_pattern:
            return [w for w in candidate_windows if title_pattern.lower() in w.title.lower()]

        elif policy == WindowPolicy.TITLE_REGEX.value and title_pattern:
            try:
                rx = re.compile(title_pattern, re.IGNORECASE)
                return [w for w in candidate_windows if rx.search(w.title)]
            except re.error:
                return candidate_windows

        # Default: MAIN_ONLY -> pick the best main window
        # Sort by visible size if available, or first non-minimized window
        non_minimized = [w for w in candidate_windows if not w.is_minimized]
        if non_minimized:
            return [non_minimized[0]]
        return [candidate_windows[0]]
