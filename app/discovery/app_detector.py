"""
Layered application detection service implementing the 7-layer resolution strategy.
"""

from __future__ import annotations
import os
import glob
import winreg
from pathlib import Path
from typing import Optional, List, Tuple
from app.models.workspace import AppConfig
from app.discovery.app_templates import get_template_by_id, APPLICATION_TEMPLATES
from app.discovery.shortcut_resolver import ShortcutResolver
from app.providers.base import IProcessProvider
from app.logging.logger import get_logger


class AppDetector:
    """
    Resolves application executables using the strict 7-layer resolution strategy:
    1. User-configured executable
    2. Currently running process
    3. Start Menu / Desktop shortcut
    4. Windows App Paths registry
    5. Known template installation paths
    6. Environment variable expansion
    7. Controlled directory wildcard scan (e.g. versioned Postman/SSMS)
    """

    def __init__(self, process_provider: IProcessProvider):
        self.process_provider = process_provider
        self.shortcut_resolver = ShortcutResolver()
        self.logger = get_logger()

    def detect_executable(self, app_config: AppConfig) -> Tuple[Optional[str], str]:
        """
        Attempts to resolve the real executable path for the given AppConfig.
        Returns (resolved_path, source_description).
        """
        # 1. User-configured executable
        if app_config.executable:
            expanded = os.path.expandvars(app_config.executable)
            if os.path.exists(expanded):
                return expanded, "configured_path"

        # 2. Currently running process
        candidate_names = list(app_config.process_names)
        if app_config.executable:
            candidate_names.append(os.path.basename(app_config.executable))
        if app_config.name:
            candidate_names.append(f"{app_config.name}.exe")

        running_procs = self.process_provider.get_running_processes_matching(candidate_names)
        for proc in running_procs:
            if proc.executable_path and os.path.exists(proc.executable_path):
                return proc.executable_path, "running_process"

        # 3. Start Menu / Desktop shortcut
        shortcut = self.shortcut_resolver.find_shortcut_matching(app_config.name)
        if shortcut and os.path.exists(shortcut.target_path):
            return shortcut.target_path, "start_menu_shortcut"

        # 4. Windows App Paths registry
        reg_path = self._query_app_paths_registry(candidate_names)
        if reg_path and os.path.exists(reg_path):
            return reg_path, "windows_app_paths"

        # 5. Known template installation paths
        template = get_template_by_id(app_config.id)
        if not template:
            # Try matching template by name
            for t in APPLICATION_TEMPLATES:
                if t.name.lower() == app_config.name.lower():
                    template = t
                    break

        if template:
            for path_pattern in template.candidate_paths:
                expanded_cand = os.path.expandvars(path_pattern)
                # If wildcard present, resolve (e.g. Postman app-*)
                if "*" in expanded_cand:
                    matches = sorted(glob.glob(expanded_cand), reverse=True)
                    if matches and os.path.exists(matches[0]):
                        return matches[0], "known_versioned_path"
                elif os.path.exists(expanded_cand):
                    return expanded_cand, "known_template_path"

        # 6. Controlled wildcard search for special apps (Postman / SSMS)
        special_path = self._detect_special_app(app_config.id, app_config.name)
        if special_path:
            return special_path, "controlled_filesystem_search"

        return None, "not_found"

    def _query_app_paths_registry(self, candidate_exes: List[str]) -> Optional[str]:
        """Queries HKLM and HKCU App Paths for an executable name."""
        roots = [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]
        for root in roots:
            for exe_name in candidate_exes:
                if not exe_name.lower().endswith(".exe"):
                    exe_name += ".exe"
                key_path = fr"Software\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}"
                try:
                    with winreg.OpenKey(root, key_path, 0, winreg.KEY_READ) as key:
                        val, _ = winreg.QueryValueEx(key, "")
                        if val and os.path.exists(val):
                            return val
                except (FileNotFoundError, OSError):
                    continue
        return None

    def _detect_special_app(self, app_id: str, app_name: str) -> Optional[str]:
        """Handles versioned searches for Postman, SSMS, Antigravity."""
        lower_id = app_id.lower()
        lower_name = app_name.lower()

        # Postman: %LocalAppData%\Postman\app-*\Postman.exe
        if "postman" in lower_id or "postman" in lower_name:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                postman_dir = Path(local_app_data) / "Postman"
                if postman_dir.exists():
                    # Direct Postman.exe
                    direct = postman_dir / "Postman.exe"
                    if direct.exists():
                        return str(direct)
                    # app-* pattern
                    matches = sorted(postman_dir.glob("app-*/Postman.exe"), reverse=True)
                    if matches:
                        return str(matches[0])

        # SSMS: check versions 18, 19, 20, 21, 22
        if "ssms" in lower_id or "sql server management studio" in lower_name:
            prog_files_x86 = os.environ.get("ProgramFiles(x86)")
            prog_files = os.environ.get("ProgramFiles")
            for base in [prog_files_x86, prog_files]:
                if base:
                    for v in [22, 21, 20, 19, 18]:
                        cand = Path(base) / f"Microsoft SQL Server Management Studio {v}" / "Common7" / "IDE" / "Ssms.exe"
                        if cand.exists():
                            return str(cand)

        # Google Antigravity
        if "antigravity" in lower_id or "antigravity" in lower_name:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                candidates = [
                    Path(local_app_data) / "Programs" / "Google Antigravity" / "Google Antigravity.exe",
                    Path(local_app_data) / "Google" / "Antigravity" / "antigravity.exe",
                    Path(local_app_data) / "Programs" / "Antigravity" / "antigravity.exe"
                ]
                for c in candidates:
                    if c.exists():
                        return str(c)

        return None
