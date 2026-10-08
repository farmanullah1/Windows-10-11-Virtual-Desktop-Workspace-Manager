"""
Abstract provider interfaces for Virtual Desktop, Window, Process, and Launcher operations.
Ensures zero coupling of business logic to specific Windows implementations and enables safe mocking.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class DesktopInfo:
    """Represents a virtual desktop."""
    number: int  # 1-indexed
    id: str      # GUID string
    name: str    # Desktop name


@dataclass
class WindowInfo:
    """Represents a top-level window."""
    hwnd: int
    title: str
    pid: int
    executable: str
    is_visible: bool
    is_minimized: bool
    is_maximized: bool
    class_name: str = ""


@dataclass
class MonitorInfo:
    """Represents a physical display monitor."""
    index: int  # 0-indexed
    x: int
    y: int
    width: int
    height: int
    is_primary: bool = False


@dataclass
class ProcessInfo:
    """Represents a running operating system process."""
    pid: int
    name: str
    executable_path: str
    cmdline: List[str]


class IVirtualDesktopProvider(ABC):
    """Interface for Windows Virtual Desktop interactions."""

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if virtual desktop APIs are supported on the current system."""
        pass

    @abstractmethod
    def get_desktop_count(self) -> int:
        """Returns the current number of available virtual desktops."""
        pass

    @abstractmethod
    def get_current_desktop_number(self) -> int:
        """Returns the 1-indexed number of the active virtual desktop."""
        pass

    @abstractmethod
    def get_desktops(self) -> List[DesktopInfo]:
        """Returns all virtual desktops in current order."""
        pass

    @abstractmethod
    def create_desktop(self) -> DesktopInfo:
        """Creates a new virtual desktop and returns its info."""
        pass

    @abstractmethod
    def switch_to_desktop(self, number: int) -> bool:
        """Switches the user view to the specified 1-indexed desktop number."""
        pass

    @abstractmethod
    def move_window_to_desktop(self, hwnd: int, desktop_number: int) -> bool:
        """Moves a window by HWND to the specified 1-indexed desktop number."""
        pass

    @abstractmethod
    def is_window_on_desktop(self, hwnd: int, desktop_number: int) -> Optional[bool]:
        """Verifies if a window is currently on the given desktop (None if verification unsupported)."""
        pass

    @abstractmethod
    def is_window_on_current_desktop(self, hwnd: int) -> Optional[bool]:
        """Checks if a window is on the active desktop."""
        pass


class IWindowProvider(ABC):
    """Interface for discovering and inspecting top-level windows."""

    @abstractmethod
    def find_windows_for_process(self, pid: int) -> List[WindowInfo]:
        """Enumerates usable top-level windows belonging to a process ID."""
        pass

    @abstractmethod
    def find_windows_by_title(self, title_query: str, is_regex: bool = False) -> List[WindowInfo]:
        """Finds top-level windows matching title query."""
        pass

    @abstractmethod
    def get_all_top_level_windows(self) -> List[WindowInfo]:
        """Returns all visible, usable top-level windows."""
        pass

    @abstractmethod
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """Fetches detailed window info by HWND."""
        pass

    @abstractmethod
    def get_monitors(self) -> List[MonitorInfo]:
        """Returns detected display monitors and their bounds."""
        pass

    @abstractmethod
    def snap_window(
        self,
        hwnd: int,
        snap_mode: str,
        monitor_index: int = 0,
        custom_rect: Optional[List[int]] = None
    ) -> bool:
        """Snaps/resizes window to target monitor and layout geometry."""
        pass


class IProcessProvider(ABC):
    """Interface for process detection and enumeration."""

    @abstractmethod
    def is_process_running(self, executable_name_or_path: str) -> bool:
        """Checks if a process with matching name or path is running."""
        pass

    @abstractmethod
    def get_running_processes_matching(self, names_or_paths: List[str]) -> List[ProcessInfo]:
        """Finds running processes matching any of the specified names or paths."""
        pass

    @abstractmethod
    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        """Gets process details by PID."""
        pass

    @abstractmethod
    def get_all_running_processes(self) -> List[ProcessInfo]:
        """Returns all running processes with executable paths."""
        pass


class IApplicationLauncher(ABC):
    """Interface for safely spawning processes without shell injection."""

    @abstractmethod
    def launch(self, executable: str, arguments: str = "", working_dir: Optional[str] = None) -> int:
        """Safely launches an executable and returns the new process ID."""
        pass
