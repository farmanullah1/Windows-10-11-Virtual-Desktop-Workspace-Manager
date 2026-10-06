"""
Resolves Windows shell shortcuts (.lnk) from Start Menu and Desktop.
"""

from __future__ import annotations
import os
import glob
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from app.logging.logger import get_logger

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False


@dataclass
class DiscoveredShortcut:
    """Represents a discovered application shortcut."""
    name: str
    target_path: str
    arguments: str
    shortcut_path: str


class ShortcutResolver:
    """Discovers and resolves .lnk shortcuts from standard Windows directories."""

    def __init__(self):
        self.logger = get_logger()
        self._shell = None
        self._cache: Optional[List[DiscoveredShortcut]] = None
        if WIN32COM_AVAILABLE:
            try:
                self._shell = win32com.client.Dispatch("WScript.Shell")
            except Exception as ex:
                self.logger.debug(f"WScript.Shell initialization note: {ex}")

    def get_search_directories(self) -> List[Path]:
        """Returns standard user and system Start Menu and Desktop paths."""
        dirs: List[Path] = []
        appdata = os.environ.get("APPDATA")
        programdata = os.environ.get("PROGRAMDATA")
        userprofile = os.environ.get("USERPROFILE")

        if appdata:
            dirs.append(Path(appdata) / r"Microsoft\Windows\Start Menu\Programs")
        if programdata:
            dirs.append(Path(programdata) / r"Microsoft\Windows\Start Menu\Programs")
        if userprofile:
            dirs.append(Path(userprofile) / "Desktop")
            dirs.append(Path(userprofile) / r"OneDrive\Desktop")

        public_desktop = os.environ.get("PUBLIC")
        if public_desktop:
            dirs.append(Path(public_desktop) / "Desktop")

        return [d for d in dirs if d.exists()]

    def discover_shortcuts(self, force_refresh: bool = False) -> List[DiscoveredShortcut]:
        """Scans standard shortcut locations and resolves executable targets."""
        if not self._shell:
            return []

        if self._cache is not None and not force_refresh:
            return self._cache

        results: List[DiscoveredShortcut] = []
        seen_targets = set()

        for base_dir in self.get_search_directories():
            try:
                for lnk in base_dir.rglob("*.lnk"):
                    try:
                        shortcut = self._shell.CreateShortcut(str(lnk))
                        target = shortcut.TargetPath
                        if target and target.lower().endswith(".exe") and os.path.exists(target):
                            norm = os.path.normpath(target).lower()
                            if norm not in seen_targets:
                                seen_targets.add(norm)
                                name = lnk.stem
                                results.append(DiscoveredShortcut(
                                    name=name,
                                    target_path=target,
                                    arguments=shortcut.Arguments or "",
                                    shortcut_path=str(lnk)
                                ))
                    except Exception:
                        continue
            except Exception as ex:
                self.logger.debug(f"Error scanning shortcuts in {base_dir}: {ex}")

        self._cache = results
        return results

    def find_shortcut_matching(self, name_query: str) -> Optional[DiscoveredShortcut]:
        """Finds the best shortcut matching a name query."""
        all_shortcuts = self.discover_shortcuts()
        query = name_query.lower()

        # Exact match
        for s in all_shortcuts:
            if s.name.lower() == query:
                return s

        # Substring match
        for s in all_shortcuts:
            if query in s.name.lower():
                return s

        return None
