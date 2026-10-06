"""
Windows Startup Service managing user-level Run registry entries safely without elevation.
"""

from __future__ import annotations
import sys
import winreg
from pathlib import Path
from typing import Optional
from app.logging.logger import get_logger

REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "VirtualDesktopWorkspaceManager"


class StartupService:
    """Manages user-level Windows startup entry in HKCU."""

    def __init__(self):
        self.logger = get_logger()

    def is_startup_enabled(self) -> bool:
        """Checks if application is registered in HKCU Run."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, APP_REG_NAME)
                return True
        except FileNotFoundError:
            return False
        except Exception as ex:
            self.logger.warning(f"Failed to query startup registry: {ex}")
            return False

    def enable_startup(self, auto_launch: bool = False) -> bool:
        """Registers the application to launch when the user logs in."""
        try:
            main_script = Path(__file__).resolve().parent.parent / "main.py"
            python_exe = sys.executable

            # Command string
            args = "--minimized"
            if auto_launch:
                args += " --autolaunch"

            cmd = f'"{python_exe}" "{main_script}" {args}'

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)

            self.logger.success("Registered in Windows startup (HKCU).")
            return True
        except Exception as ex:
            self.logger.error(f"Failed to enable startup: {ex}")
            return False

    def disable_startup(self) -> bool:
        """Removes the application from HKCU Run."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, APP_REG_NAME)
            self.logger.info("Removed from Windows startup.")
            return True
        except FileNotFoundError:
            return True  # Already not registered
        except Exception as ex:
            self.logger.error(f"Failed to remove from startup: {ex}")
            return False
