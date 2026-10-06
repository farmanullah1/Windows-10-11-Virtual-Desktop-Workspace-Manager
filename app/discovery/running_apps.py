"""
Discovery of currently active running applications with visible top-level windows.
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List
from app.providers.base import IProcessProvider, IWindowProvider, WindowInfo, ProcessInfo


@dataclass
class RunningAppInfo:
    """Represents a running application eligible for adding to a workspace."""
    name: str
    process_name: str
    pid: int
    executable: str
    window_title: str
    hwnd: int


class RunningAppDiscoverer:
    """Inspects running processes and their visible top-level windows."""

    def __init__(self, process_provider: IProcessProvider, window_provider: IWindowProvider):
        self.process_provider = process_provider
        self.window_provider = window_provider

    def discover_running_applications(self) -> List[RunningAppInfo]:
        """Returns list of running applications that currently have visible windows."""
        windows = self.window_provider.get_all_top_level_windows()
        results: List[RunningAppInfo] = []
        seen_pids = set()

        for win in windows:
            if not win.is_visible or not win.title:
                continue

            # Get process info
            proc_info = self.process_provider.get_process_info(win.pid)
            if not proc_info:
                continue

            exe_path = proc_info.executable_path or ""
            proc_name = proc_info.name or (os.path.basename(exe_path) if exe_path else "")

            # Filter out generic Windows system processes
            if proc_name.lower() in {"explorer.exe", "textinputhost.exe", "searchhost.exe"}:
                # Only include explorer if title indicates actual folder or window
                if proc_name.lower() == "explorer.exe" and win.title.lower() in {"program manager", ""}:
                    continue

            # Friendly application display name
            app_name = os.path.splitext(proc_name)[0]
            if app_name.lower() == "brave":
                app_name = "Brave Browser"
            elif app_name.lower() == "code":
                app_name = "Visual Studio Code"
            elif app_name.lower() == "ssms":
                app_name = "SQL Server Management Studio"
            elif app_name.lower() == "devenv":
                app_name = "Visual Studio"

            results.append(RunningAppInfo(
                name=app_name,
                process_name=proc_name,
                pid=win.pid,
                executable=exe_path,
                window_title=win.title,
                hwnd=win.hwnd
            ))

        return results
