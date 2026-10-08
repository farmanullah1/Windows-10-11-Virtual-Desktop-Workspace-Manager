"""
Production Window Service providing top-level window enumeration,
filtering of ghost/helper windows, and policy-based matching.
"""

from __future__ import annotations
import os
import re
from typing import List, Optional
from app.providers.base import IWindowProvider, WindowInfo, MonitorInfo
from app.models.workspace import WindowPolicy, WindowSnap
from app.logging.logger import get_logger

try:
    import win32gui
    import win32process
    import win32con
    import win32api
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

    def get_monitors(self) -> List[MonitorInfo]:
        """Detects physical displays and their work areas (excluding taskbar)."""
        if not WIN32_AVAILABLE:
            return [MonitorInfo(index=0, x=0, y=0, width=1920, height=1080, is_primary=True)]
        try:
            monitors: List[MonitorInfo] = []
            for i, h_mon in enumerate(win32api.EnumDisplayMonitors()):
                info = win32api.GetMonitorInfo(h_mon[0])
                rc_work = info.get("Work", (0, 0, 1920, 1080))
                is_pri = bool(info.get("Flags", 0) & 1)
                monitors.append(MonitorInfo(
                    index=i,
                    x=rc_work[0],
                    y=rc_work[1],
                    width=rc_work[2] - rc_work[0],
                    height=rc_work[3] - rc_work[1],
                    is_primary=is_pri
                ))
            return monitors or [MonitorInfo(index=0, x=0, y=0, width=1920, height=1080, is_primary=True)]
        except Exception as ex:
            self.logger.debug(f"EnumDisplayMonitors exception: {ex}")
            return [MonitorInfo(index=0, x=0, y=0, width=1920, height=1080, is_primary=True)]

    def snap_window(
        self,
        hwnd: int,
        snap_mode: str,
        monitor_index: int = 0,
        custom_rect: Optional[List[int]] = None
    ) -> bool:
        """Snaps or tiles window to target monitor and layout geometry."""
        if not WIN32_AVAILABLE or not win32gui.IsWindow(hwnd):
            return False

        if snap_mode == WindowSnap.DEFAULT.value:
            return True
        elif snap_mode == WindowSnap.MAXIMIZE.value:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        elif snap_mode == WindowSnap.MINIMIZE.value:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True

        monitors = self.get_monitors()
        mon = monitors[monitor_index] if 0 <= monitor_index < len(monitors) else monitors[0]

        try:
            # Restore if currently minimized or maximized before moving
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            x, y, w, h = mon.x, mon.y, mon.width, mon.height
            if snap_mode == WindowSnap.LEFT_HALF.value:
                tx, ty, tw, th = x, y, w // 2, h
            elif snap_mode == WindowSnap.RIGHT_HALF.value:
                tx, ty, tw, th = x + (w // 2), y, w // 2, h
            elif snap_mode == WindowSnap.TOP_HALF.value:
                tx, ty, tw, th = x, y, w, h // 2
            elif snap_mode == WindowSnap.BOTTOM_HALF.value:
                tx, ty, tw, th = x, y + (h // 2), w, h // 2
            elif snap_mode == WindowSnap.CENTER.value:
                cw, ch = int(w * 0.75), int(h * 0.75)
                tx, ty, tw, th = x + (w - cw) // 2, y + (h - ch) // 2, cw, ch
            elif snap_mode == WindowSnap.CUSTOM.value and custom_rect and len(custom_rect) == 4:
                tx, ty, tw, th = custom_rect
            else:
                return True

            win32gui.SetWindowPos(
                hwnd, 0, tx, ty, tw, th,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
            return True
        except Exception as ex:
            self.logger.warning(f"Failed to snap window HWND {hwnd}: {ex}")
            return False
