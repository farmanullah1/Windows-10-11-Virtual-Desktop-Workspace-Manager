"""
Providers package exports.
"""

from app.providers.base import (
    IVirtualDesktopProvider,
    IWindowProvider,
    IProcessProvider,
    IApplicationLauncher,
    DesktopInfo,
    WindowInfo,
    ProcessInfo,
)
from app.providers.windows_vda_provider import WindowsVdaProvider
from app.providers.official_com_provider import OfficialComDesktopManager
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockWindowProvider,
    MockProcessProvider,
    MockApplicationLauncher,
)
from app.providers.keyboard_fallback_provider import KeyboardFallbackProvider

__all__ = [
    "IVirtualDesktopProvider",
    "IWindowProvider",
    "IProcessProvider",
    "IApplicationLauncher",
    "DesktopInfo",
    "WindowInfo",
    "ProcessInfo",
    "WindowsVdaProvider",
    "OfficialComDesktopManager",
    "MockVirtualDesktopProvider",
    "MockWindowProvider",
    "MockProcessProvider",
    "MockApplicationLauncher",
    "KeyboardFallbackProvider",
]
