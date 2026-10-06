"""
Single-instance guard for Virtual Desktop Workspace Manager.
Prevents duplicate background or GUI manager instances using Windows named mutex
or local file locks, and brings the existing window to the foreground.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Optional

from app.logging.logger import get_logger

MUTEX_NAME = "Local\\VirtualDesktopWorkspaceManager_SingleInstance_Mutex"


class SingleInstanceGuard:
    """Manages single-instance enforcement for the desktop manager."""

    def __init__(self, app_data_dir: Optional[Path] = None):
        self.logger = get_logger()
        self.app_data_dir = app_data_dir or (Path(os.environ.get("APPDATA", Path.home())) / "VirtualDesktopWorkspaceManager")
        self._mutex_handle = None
        self._lock_file = self.app_data_dir / "instance.lock"
        self._is_primary = False

    def acquire(self) -> bool:
        """
        Attempts to acquire the single-instance lock.
        Returns True if this is the only/primary instance, False if an instance is already running.
        """
        # 1. On Windows, try named Win32 mutex first
        if sys.platform == "win32":
            try:
                import win32event
                import win32api
                import winerror

                self._mutex_handle = win32event.CreateMutex(None, False, MUTEX_NAME)
                last_error = win32api.GetLastError()
                if last_error == winerror.ERROR_ALREADY_EXISTS:
                    if self._mutex_handle:
                        try:
                            win32api.CloseHandle(self._mutex_handle)
                        except Exception:
                            pass
                        self._mutex_handle = None
                    self.logger.warning("Another instance of Virtual Desktop Workspace Manager is already running.")
                    self._bring_existing_to_foreground()
                    return False

                self._is_primary = True
                return True
            except Exception as ex:
                self.logger.debug("Win32 CreateMutex unavailable (%s), using lockfile fallback.", ex)

        # 2. File lock fallback
        try:
            self.app_data_dir.mkdir(parents=True, exist_ok=True)
            if self._lock_file.exists():
                try:
                    pid_str = self._lock_file.read_text(encoding="utf-8").strip()
                    if pid_str.isdigit():
                        import psutil
                        old_pid = int(pid_str)
                        if psutil.pid_exists(old_pid):
                            # Check if the existing process is actually python/manager
                            proc = psutil.Process(old_pid)
                            if "python" in proc.name().lower() or "workspace" in proc.name().lower():
                                self.logger.warning("Existing manager running under PID %d.", old_pid)
                                self._bring_existing_to_foreground()
                                return False
                except Exception:
                    pass

            self._lock_file.write_text(str(os.getpid()), encoding="utf-8")
            self._is_primary = True
            return True
        except Exception as ex:
            self.logger.error("Could not establish instance lock: %s", ex)
            return True

    def _bring_existing_to_foreground(self) -> None:
        """Attempts to activate the already-running manager window."""
        if sys.platform == "win32":
            try:
                import win32gui
                import win32con

                hwnd = win32gui.FindWindow(None, "Virtual Desktop Workspace Manager")
                if hwnd and win32gui.IsWindow(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass

    def release(self) -> None:
        """Releases the instance lock upon clean exit."""
        if sys.platform == "win32" and self._mutex_handle:
            try:
                import win32api
                win32api.CloseHandle(self._mutex_handle)
            except Exception:
                pass
            self._mutex_handle = None

        if self._is_primary and self._lock_file.exists():
            try:
                self._lock_file.unlink()
            except Exception:
                pass
        self._is_primary = False
