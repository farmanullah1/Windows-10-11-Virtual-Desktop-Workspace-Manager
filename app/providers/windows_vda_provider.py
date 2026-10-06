"""
Windows Virtual Desktop Provider using the pyvda library.
Interacts with Windows 10/11 Virtual Desktop COM interfaces.
"""

from __future__ import annotations
from typing import List, Optional
from app.providers.base import IVirtualDesktopProvider, DesktopInfo
from app.logging.logger import get_logger

try:
    import pyvda
    from pyvda import VirtualDesktop, AppView, get_virtual_desktops
    PYVDA_AVAILABLE = True
except ImportError:
    PYVDA_AVAILABLE = False


class WindowsVdaProvider(IVirtualDesktopProvider):
    """Production provider integrating directly with Windows Virtual Desktop COM interfaces."""

    def __init__(self):
        self.logger = get_logger()
        self._available = PYVDA_AVAILABLE

    def is_available(self) -> bool:
        if not self._available:
            return False
        try:
            # Test read-only query
            desktops = get_virtual_desktops()
            return len(desktops) > 0
        except Exception as ex:
            self.logger.warning(f"pyvda COM interface not available or failed: {ex}")
            return False

    def get_desktop_count(self) -> int:
        if not self.is_available():
            return 1
        try:
            desktops = get_virtual_desktops()
            return len(desktops)
        except Exception as ex:
            self.logger.warning(f"Failed to get desktop count: {ex}")
            return 1

    def get_current_desktop_number(self) -> int:
        if not self.is_available():
            return 1
        try:
            curr = VirtualDesktop.current()
            return curr.number
        except Exception as ex:
            self.logger.warning(f"Failed to get current desktop number: {ex}")
            return 1

    def get_desktops(self) -> List[DesktopInfo]:
        if not self.is_available():
            return [DesktopInfo(number=1, id="default", name="Desktop 1")]
        try:
            desktops = get_virtual_desktops()
            res = []
            for d in desktops:
                d_name = getattr(d, "name", None) or f"Desktop {d.number}"
                res.append(DesktopInfo(number=d.number, id=str(d.id), name=str(d_name)))
            return res
        except Exception as ex:
            self.logger.error(f"Failed to enumerate virtual desktops: {ex}")
            return [DesktopInfo(number=1, id="default", name="Desktop 1")]

    def create_desktop(self) -> DesktopInfo:
        if not self.is_available():
            raise RuntimeError("Virtual desktop API is not available on this system.")
        try:
            new_vd = VirtualDesktop.create()
            d_name = getattr(new_vd, "name", None) or f"Desktop {new_vd.number}"
            self.logger.success(f"Desktop {new_vd.number} created (ID: {new_vd.id})")
            return DesktopInfo(number=new_vd.number, id=str(new_vd.id), name=str(d_name))
        except Exception as ex:
            self.logger.error(f"Failed to create virtual desktop: {ex}")
            raise RuntimeError(f"Desktop creation failed: {ex}") from ex

    def switch_to_desktop(self, number: int) -> bool:
        if not self.is_available():
            return False
        try:
            target = VirtualDesktop(number)
            target.go()
            self.logger.info(f"Switched view to Desktop {number}")
            return True
        except Exception as ex:
            self.logger.error(f"Failed to switch to Desktop {number}: {ex}")
            return False

    def move_window_to_desktop(self, hwnd: int, desktop_number: int) -> bool:
        if not self.is_available():
            return False
        try:
            app_view = AppView(hwnd)
            target_vd = VirtualDesktop(desktop_number)
            app_view.move(target_vd)
            self.logger.info(f"Moved HWND {hwnd} to Desktop {desktop_number}")
            return True
        except Exception as ex:
            self.logger.error(f"Failed to move HWND {hwnd} to Desktop {desktop_number}: {ex}")
            return False

    def is_window_on_desktop(self, hwnd: int, desktop_number: int) -> Optional[bool]:
        if not self.is_available():
            return None
        try:
            app_view = AppView(hwnd)
            target_vd = VirtualDesktop(desktop_number)
            return app_view.is_on_desktop(target_vd)
        except Exception as ex:
            self.logger.warning(f"Could not verify window {hwnd} desktop placement: {ex}")
            return None

    def is_window_on_current_desktop(self, hwnd: int) -> Optional[bool]:
        if not self.is_available():
            return None
        try:
            app_view = AppView(hwnd)
            return app_view.is_on_current_desktop()
        except Exception as ex:
            self.logger.warning(f"Could not verify window {hwnd} on current desktop: {ex}")
            return None
