"""
Windows 10/11 Dynamic COM Provider & VTable Offset Resolver.
Provides build-resilient detection and dispatch across Windows major releases:
- Windows 10 (1809–22H2, Builds 17763–19045)
- Windows 11 21H2 (Build 22000)
- Windows 11 22H2/23H2 (Builds 22621/22631)
- Windows 11 24H2 (Build 26100+)
"""

from __future__ import annotations
import sys
import platform
from typing import List, Optional, Dict, Any
from app.providers.base import (
    IVirtualDesktopProvider,
    DesktopInfo,
)
from app.providers.windows_vda_provider import WindowsVdaProvider
from app.providers.official_com_provider import OfficialComDesktopManager
from app.providers.keyboard_fallback_provider import KeyboardFallbackProvider
from app.logging.logger import get_logger


# Known vtable method indices for IVirtualDesktopManagerInternal across Windows builds
VTABLE_PROFILES: Dict[str, Dict[str, int]] = {
    "win10": {
        "GetCount": 3,
        "GetCurrentDesktop": 6,
        "GetDesktops": 7,
        "CreateDesktop": 10,
        "SwitchDesktop": 9,
    },
    "win11_21h2": {
        "GetCount": 3,
        "GetCurrentDesktop": 6,
        "GetDesktops": 7,
        "CreateDesktop": 11,
        "SwitchDesktop": 9,
    },
    "win11_22h2": {
        "GetCount": 3,
        "GetCurrentDesktop": 6,
        "GetDesktops": 7,
        "CreateDesktop": 12,
        "SwitchDesktop": 9,
    },
    "win11_24h2": {
        "GetCount": 3,
        "GetCurrentDesktop": 6,
        "GetDesktops": 7,
        "CreateDesktop": 13,
        "SwitchDesktop": 10,
    },
}


class WindowsDynamicComProvider(IVirtualDesktopProvider):
    """
    Adaptive provider that detects current Windows OS build and dynamically selects
    the optimal COM wrapper or fallback chain.
    """

    def __init__(self, simulated_build: Optional[int] = None):
        self.logger = get_logger()
        self.build_number = simulated_build or self._detect_build_number()
        self.build_profile_name = self._resolve_profile_name(self.build_number)

        # Provider cascade
        self.vda_provider = WindowsVdaProvider()
        self.official_provider = OfficialComProvider()
        self.hotkey_provider = KeyboardFallbackProvider()

    @staticmethod
    def _detect_build_number() -> int:
        if sys.platform == "win32":
            try:
                ver = sys.getwindowsversion()
                return getattr(ver, "build", 19045)
            except Exception:
                pass
        return 19045  # Default to Windows 10 22H2

    @staticmethod
    def _resolve_profile_name(build: int) -> str:
        if build >= 26100:
            return "win11_24h2"
        elif build >= 22621:
            return "win11_22h2"
        elif build >= 22000:
            return "win11_21h2"
        else:
            return "win10"

    def get_vtable_offsets(self) -> Dict[str, int]:
        """Returns the vtable index mapping corresponding to the active Windows build."""
        return VTABLE_PROFILES.get(self.build_profile_name, VTABLE_PROFILES["win10"])

    def is_available(self) -> bool:
        return (
            self.vda_provider.is_available()
            or self.official_provider.is_available()
            or self.hotkey_provider.is_available()
        )

    def get_desktop_count(self) -> int:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.get_desktop_count()
            except Exception as ex:
                self.logger.debug(f"VDA get_desktop_count fallback: {ex}")
        return self.official_provider.get_desktop_count()

    def get_current_desktop_number(self) -> int:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.get_current_desktop_number()
            except Exception as ex:
                self.logger.debug(f"VDA get_current_desktop_number fallback: {ex}")
        return self.official_provider.get_current_desktop_number()

    def get_desktops(self) -> List[DesktopInfo]:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.get_desktops()
            except Exception as ex:
                self.logger.debug(f"VDA get_desktops fallback: {ex}")
        return self.official_provider.get_desktops()

    def create_desktop(self) -> DesktopInfo:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.create_desktop()
            except Exception as ex:
                self.logger.warning(f"VDA create_desktop failed, attempting hotkey creation: {ex}")
        return self.hotkey_provider.create_desktop()

    def switch_to_desktop(self, number: int) -> bool:
        if self.vda_provider.is_available():
            try:
                if self.vda_provider.switch_to_desktop(number):
                    return True
            except Exception as ex:
                self.logger.debug(f"VDA switch_to_desktop fallback: {ex}")
        return self.hotkey_provider.switch_to_desktop(number)

    def move_window_to_desktop(self, hwnd: int, desktop_number: int) -> bool:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.move_window_to_desktop(hwnd, desktop_number)
            except Exception as ex:
                self.logger.debug(f"VDA move_window_to_desktop fallback: {ex}")
        return self.official_provider.move_window_to_desktop(hwnd, desktop_number)

    def is_window_on_desktop(self, hwnd: int, desktop_number: int) -> Optional[bool]:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.is_window_on_desktop(hwnd, desktop_number)
            except Exception:
                pass
        return self.official_provider.is_window_on_desktop(hwnd, desktop_number)

    def is_window_on_current_desktop(self, hwnd: int) -> Optional[bool]:
        if self.vda_provider.is_available():
            try:
                return self.vda_provider.is_window_on_current_desktop(hwnd)
            except Exception:
                pass
        return self.official_provider.is_window_on_current_desktop(hwnd)
