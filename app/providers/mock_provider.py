"""
Isolated Mock Providers for 100% safe, non-destructive testing and dry-run execution.
Guarantees tests will never modify host desktops or spawn real applications.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from app.providers.base import (
    IVirtualDesktopProvider,
    IWindowProvider,
    IProcessProvider,
    IApplicationLauncher,
    DesktopInfo,
    WindowInfo,
    ProcessInfo,
)


class MockVirtualDesktopProvider(IVirtualDesktopProvider):
    """In-memory mock virtual desktop manager."""

    def __init__(self, initial_desktop_count: int = 2):
        self.desktops: List[DesktopInfo] = [
            DesktopInfo(number=i, id=f"guid-mock-desktop-{i}", name=f"Desktop {i}")
            for i in range(1, initial_desktop_count + 1)
        ]
        self.current_desktop: int = 1
        self.window_assignments: Dict[int, int] = {}  # hwnd -> desktop_number
        self.should_fail_create: bool = False
        self.should_fail_move: bool = False
        self.allow_verification: bool = True

    def is_available(self) -> bool:
        return True

    def get_desktop_count(self) -> int:
        return len(self.desktops)

    def get_current_desktop_number(self) -> int:
        return self.current_desktop

    def get_desktops(self) -> List[DesktopInfo]:
        return list(self.desktops)

    def create_desktop(self) -> DesktopInfo:
        if self.should_fail_create:
            raise RuntimeError("Mock simulated desktop creation failure.")
        next_num = len(self.desktops) + 1
        new_desktop = DesktopInfo(
            number=next_num,
            id=f"guid-mock-desktop-{next_num}",
            name=f"Desktop {next_num}"
        )
        self.desktops.append(new_desktop)
        return new_desktop

    def switch_to_desktop(self, number: int) -> bool:
        if 1 <= number <= len(self.desktops):
            self.current_desktop = number
            return True
        return False

    def move_window_to_desktop(self, hwnd: int, desktop_number: int) -> bool:
        if self.should_fail_move:
            return False
        if 1 <= desktop_number <= len(self.desktops):
            self.window_assignments[hwnd] = desktop_number
            return True
        return False

    def is_window_on_desktop(self, hwnd: int, desktop_number: int) -> Optional[bool]:
        if not self.allow_verification:
            return None
        return self.window_assignments.get(hwnd) == desktop_number

    def is_window_on_current_desktop(self, hwnd: int) -> Optional[bool]:
        if not self.allow_verification:
            return None
        return self.window_assignments.get(hwnd) == self.current_desktop

    def get_window_desktop(self, hwnd: int) -> Optional[int]:
        """Returns the 1-indexed desktop number the window is assigned to."""
        return self.window_assignments.get(hwnd)


class MockWindowProvider(IWindowProvider):
    """In-memory mock window discovery provider."""

    def __init__(self, initial_windows: Optional[List[WindowInfo]] = None):
        self.windows: List[WindowInfo] = initial_windows or []

    def add_window(self, win: WindowInfo) -> None:
        self.windows.append(win)

    def find_windows_for_process(self, pid: int) -> List[WindowInfo]:
        return [w for w in self.windows if w.pid == pid and w.is_visible]

    def find_windows_by_title(self, title_query: str, is_regex: bool = False) -> List[WindowInfo]:
        import re
        results = []
        for w in self.windows:
            if not w.is_visible:
                continue
            if is_regex:
                if re.search(title_query, w.title, re.IGNORECASE):
                    results.append(w)
            else:
                if title_query.lower() in w.title.lower():
                    results.append(w)
        return results

    def get_all_top_level_windows(self) -> List[WindowInfo]:
        return [w for w in self.windows if w.is_visible]

    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        for w in self.windows:
            if w.hwnd == hwnd:
                return w
        return None


class MockProcessProvider(IProcessProvider):
    """In-memory mock process provider."""

    def __init__(self, initial_processes: Optional[List[ProcessInfo]] = None):
        self.processes: List[ProcessInfo] = initial_processes or []

    def add_process(self, proc: ProcessInfo) -> None:
        self.processes.append(proc)

    def is_process_running(self, executable_name_or_path: str) -> bool:
        target = executable_name_or_path.lower()
        for p in self.processes:
            if p.name.lower() == target or p.executable_path.lower() == target:
                return True
        return False

    def get_running_processes_matching(self, names_or_paths: List[str]) -> List[ProcessInfo]:
        targets = {x.lower() for x in names_or_paths}
        results = []
        for p in self.processes:
            if p.name.lower() in targets or p.executable_path.lower() in targets:
                results.append(p)
        return results

    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        for p in self.processes:
            if p.pid == pid:
                return p
        return None

    def get_all_running_processes(self) -> List[ProcessInfo]:
        return list(self.processes)


class MockApplicationLauncher(IApplicationLauncher):
    """In-memory application launcher mock that records launches without executing processes."""

    def __init__(
        self,
        auto_create_window: bool = True,
        window_provider: Optional[MockWindowProvider] = None,
        process_provider: Optional[MockProcessProvider] = None
    ):
        self.launched_commands: List[Dict[str, Any]] = []
        self.next_pid: int = 10000
        self.next_hwnd: int = 50000
        self.auto_create_window = auto_create_window
        self.window_provider = window_provider
        self.process_provider = process_provider

    def launch(self, executable: str, arguments: str = "", working_dir: Optional[str] = None) -> int:
        self.next_pid += 1
        pid = self.next_pid
        self.launched_commands.append({
            "executable": executable,
            "arguments": arguments,
            "working_dir": working_dir,
            "pid": pid
        })

        if self.process_provider:
            self.process_provider.add_process(ProcessInfo(
                pid=pid,
                name=executable.split("\\")[-1],
                executable_path=executable,
                cmdline=[]
            ))

        # Optionally auto-create simulated top-level window in the mock window provider
        if self.auto_create_window and self.window_provider:
            self.next_hwnd += 1
            win_name = executable.split("\\")[-1].replace(".exe", "")
            self.window_provider.add_window(WindowInfo(
                hwnd=self.next_hwnd,
                title=f"{win_name} Application",
                pid=pid,
                executable=executable,
                is_visible=True,
                is_minimized=False,
                is_maximized=False
            ))

        return pid
