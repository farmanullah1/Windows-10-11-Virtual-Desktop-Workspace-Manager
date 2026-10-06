"""
Diagnostics service that generates comprehensive diagnostic reports
with strict privacy redactions for troubleshooting.
"""

from __future__ import annotations
import os
import re
import sys
import time
import platform
from typing import Dict, Any, List
from app import __version__
from app.models.workspace import WorkspaceConfig
from app.providers.base import IVirtualDesktopProvider, IProcessProvider, IWindowProvider
from app.logging.logger import get_buffer_handler


class DiagnosticsService:
    """Generates sanitized diagnostics reports for developers and troubleshooting."""

    def __init__(
        self,
        config: WorkspaceConfig,
        desktop_provider: IVirtualDesktopProvider,
        process_provider: IProcessProvider,
        window_provider: IWindowProvider
    ):
        self.config = config
        self.desktop_provider = desktop_provider
        self.process_provider = process_provider
        self.window_provider = window_provider

    def _sanitize(self, text: str) -> str:
        """Redacts sensitive tokens, passwords, API keys, and user profile paths."""
        if not text:
            return ""
        # Redact common auth token/password patterns
        text = re.sub(r"(token|auth|password|secret|bearer)=([^\s&]+)", r"\1=***REDACTED***", text, flags=re.IGNORECASE)
        # Redact usernames in file paths
        user_name = os.environ.get("USERNAME", "")
        if user_name:
            text = text.replace(user_name, "<USER>")
        return text

    def generate_report(self) -> str:
        """Assembles and formats a complete redacted diagnostic report."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        lines: List[str] = [
            "=" * 70,
            "VIRTUAL DESKTOP WORKSPACE MANAGER — DIAGNOSTIC REPORT",
            "=" * 70,
            f"Generated: {timestamp}",
            f"Manager Version: {__version__}",
            f"Python Version: {sys.version.split()[0]} ({platform.architecture()[0]})",
            f"OS: {platform.platform()}",
            f"Windows Build: {platform.version()}",
            "",
            "--- VIRTUAL DESKTOP SUBSYSTEM ---",
            f"Provider Active: {self.desktop_provider.__class__.__name__}",
            f"API Available: {self.desktop_provider.is_available()}",
            f"Current Desktop Count: {self.desktop_provider.get_desktop_count()}",
            f"Active Desktop Index: {self.desktop_provider.get_current_desktop_number()}",
            ""
        ]

        # Enumerate desktops
        try:
            desktops = self.desktop_provider.get_desktops()
            lines.append("Detected Desktops:")
            for d in desktops:
                lines.append(f"  - Position {d.number}: '{d.name}' (ID: {d.id})")
        except Exception as ex:
            lines.append(f"Desktop Enumeration Error: {ex}")

        # Active Profile Info
        profile = self.config.get_active_profile()
        lines.extend([
            "",
            "--- ACTIVE WORKSPACE PROFILE ---",
            f"Profile ID: {profile.id}",
            f"Profile Name: {profile.name}",
            f"Configured Desktops: {len(profile.desktops)}",
            f"Configured Apps: {len(profile.apps)}",
            ""
        ])

        # Applications details
        lines.append("Applications Inspection:")
        for app in profile.apps:
            expanded = self._sanitize(app.expanded_executable)
            exists = os.path.exists(app.expanded_executable) if app.executable else False
            running = False
            try:
                running = self.process_provider.is_process_running(app.expanded_executable)
                if not running and app.process_names:
                    running = any(self.process_provider.is_process_running(p) for p in app.process_names)
            except Exception:
                pass

            lines.append(f"  [{'ENABLED' if app.enabled else 'DISABLED'}] {app.name}")
            lines.append(f"    ID: {app.id}")
            lines.append(f"    Target Desktop: {app.desktop}")
            lines.append(f"    Executable: {expanded} (Exists: {exists})")
            lines.append(f"    Running: {running}")
            lines.append(f"    Policy: {app.window_policy}")
            lines.append(f"    Launch Mode: {app.launch_mode}")

        # Top-level windows inspection
        try:
            windows = self.window_provider.get_all_top_level_windows()
            lines.extend([
                "",
                "--- VISIBLE TOP-LEVEL WINDOWS ---",
                f"Total Visible Top-Level Windows: {len(windows)}"
            ])
            for w in windows[:20]:  # Limit to 20 for readability
                sanitized_title = self._sanitize(w.title)
                lines.append(f"  - HWND {w.hwnd} | PID {w.pid} | Title: '{sanitized_title}'")
            if len(windows) > 20:
                lines.append(f"  ... and {len(windows) - 20} more windows.")
        except Exception as ex:
            lines.append(f"Window enumeration error: {ex}")

        # Recent Log Records
        try:
            records = get_buffer_handler().get_records()
            recent_errors = [r for r in records if r.levelno >= 30]  # WARNING and ERROR
            lines.extend([
                "",
                "--- RECENT WARNINGS & ERRORS ---",
                f"Count: {len(recent_errors)}"
            ])
            for r in recent_errors[-15:]:
                lines.append(f"  [{r.levelname}] {self._sanitize(r.getMessage())}")
        except Exception as ex:
            lines.append(f"Log retrieval error: {ex}")

        lines.extend([
            "",
            "=" * 70,
            "END OF DIAGNOSTIC REPORT",
            "=" * 70
        ])

        return "\n".join(lines)
