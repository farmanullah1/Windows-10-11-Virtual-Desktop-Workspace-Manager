"""
Direct COM implementation using Microsoft's officially documented IVirtualDesktopManager.
Used for verification and secondary window movement by GUID.
"""

from __future__ import annotations
import ctypes
from ctypes import wintypes
from typing import Optional
from app.logging.logger import get_logger

try:
    import comtypes
    import comtypes.client
    from comtypes import GUID, IUnknown, COMMETHOD, HRESULT

    # Official Microsoft IVirtualDesktopManager COM definitions
    CLSID_VirtualDesktopManager = GUID("{AA509086-5CA9-4C25-8F95-589D3C07B48A}")
    IID_IVirtualDesktopManager = GUID("{A5CD92EC-0168-4615-9106-96241F6412B9}")

    class IVirtualDesktopManager(IUnknown):
        _iid_ = IID_IVirtualDesktopManager
        _methods_ = [
            COMMETHOD(
                [],
                HRESULT,
                "IsWindowOnCurrentVirtualDesktop",
                (["in"], wintypes.HWND, "topLevelWindow"),
                (["out"], ctypes.POINTER(wintypes.BOOL), "onCurrentDesktop")
            ),
            COMMETHOD(
                [],
                HRESULT,
                "GetWindowDesktopId",
                (["in"], wintypes.HWND, "topLevelWindow"),
                (["out"], ctypes.POINTER(GUID), "desktopId")
            ),
            COMMETHOD(
                [],
                HRESULT,
                "MoveWindowToDesktop",
                (["in"], wintypes.HWND, "topLevelWindow"),
                (["in"], ctypes.POINTER(GUID), "desktopId")
            )
        ]
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


class OfficialComDesktopManager:
    """Provides direct official Windows COM queries for window-to-desktop status."""

    def __init__(self):
        self.logger = get_logger()
        self._manager = None
        if COM_AVAILABLE:
            try:
                self._manager = comtypes.client.CreateObject(
                    CLSID_VirtualDesktopManager,
                    interface=IVirtualDesktopManager
                )
            except Exception as ex:
                self.logger.debug(f"Official IVirtualDesktopManager initialization notice: {ex}")

    def is_available(self) -> bool:
        return self._manager is not None

    def is_window_on_current_desktop(self, hwnd: int) -> Optional[bool]:
        if not self._manager:
            return None
        try:
            return bool(self._manager.IsWindowOnCurrentVirtualDesktop(hwnd))
        except Exception:
            return None

    def get_window_desktop_id(self, hwnd: int) -> Optional[str]:
        if not self._manager:
            return None
        try:
            guid = self._manager.GetWindowDesktopId(hwnd)
            return str(guid)
        except Exception:
            return None

    def move_window_to_desktop_guid(self, hwnd: int, desktop_guid_str: str) -> bool:
        if not self._manager:
            return False
        try:
            target_guid = GUID(desktop_guid_str)
            self._manager.MoveWindowToDesktop(hwnd, ctypes.byref(target_guid))
            return True
        except Exception as ex:
            self.logger.error(f"MoveWindowToDesktop COM error for HWND {hwnd}: {ex}")
            return False
