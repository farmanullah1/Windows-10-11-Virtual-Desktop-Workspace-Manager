"""
Tests for Multi-Monitor Display Awareness & Window Layout Snapping / Tiling.
"""

import pytest
from app.models.workspace import (
    AppConfig,
    WorkspaceProfile,
    DesktopConfig,
    WindowSnap,
)
from app.providers.base import MonitorInfo, WindowInfo
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockWindowProvider,
    MockProcessProvider,
    MockApplicationLauncher,
)
from app.discovery.app_detector import AppDetector
from app.core.execution_plan import WorkspaceExecutionPlan
from app.configuration.validator import ConfigValidator
from app.services.window_service import WindowService


def test_monitor_info_and_mock_enumeration():
    """Verifies display monitors can be queried through provider."""
    monitors = [
        MonitorInfo(index=0, x=0, y=0, width=1920, height=1080, is_primary=True),
        MonitorInfo(index=1, x=1920, y=0, width=2560, height=1440, is_primary=False),
    ]
    provider = MockWindowProvider(initial_monitors=monitors)

    retrieved = provider.get_monitors()
    assert len(retrieved) == 2
    assert retrieved[0].is_primary is True
    assert retrieved[1].x == 1920
    assert retrieved[1].width == 2560


def test_app_config_snap_serialization():
    """Verifies AppConfig serializes and deserializes monitor and snap settings."""
    app = AppConfig(
        id="app_snap",
        name="Tiled Browser",
        desktop=2,
        monitor_index=1,
        window_snap=WindowSnap.LEFT_HALF.value,
        custom_rect=[100, 100, 800, 600]
    )
    data = app.to_dict()
    assert data["monitor_index"] == 1
    assert data["window_snap"] == "left_half"
    assert data["custom_rect"] == [100, 100, 800, 600]

    reloaded = AppConfig.from_dict(data)
    assert reloaded.monitor_index == 1
    assert reloaded.window_snap == "left_half"
    assert reloaded.custom_rect == [100, 100, 800, 600]


def test_execution_plan_snaps_window_after_placement():
    """Verifies execution plan moves window to target desktop and snaps layout."""
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=2)
    win = WindowInfo(
        hwnd=9901,
        title="Code Editor",
        pid=123,
        executable="code.exe",
        is_visible=True,
        is_minimized=False,
        is_maximized=False
    )
    window_provider = MockWindowProvider([win])
    proc_provider = MockProcessProvider()
    launcher = MockApplicationLauncher(auto_create_window=False, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    detector.detect_executable = lambda app: (app.executable, "mock_test")

    profile = WorkspaceProfile(
        id="p-snap",
        name="Snap Profile",
        desktops=[DesktopConfig(number=1, name="D1"), DesktopConfig(number=2, name="D2")],
        apps=[
            AppConfig(
                id="a_snap",
                name="Code Editor",
                executable="C:\\Apps\\code.exe",
                desktop=2,
                monitor_index=1,
                window_snap=WindowSnap.RIGHT_HALF.value,
                window_timeout_ms=50
            )
        ]
    )

    plan = WorkspaceExecutionPlan(
        profile=profile,
        desktop_provider=desktop_provider,
        window_provider=window_provider,
        process_provider=proc_provider,
        launcher=launcher,
        app_detector=detector
    )

    # Put process as already running so it uses existing window
    from app.providers.base import ProcessInfo
    proc_provider.add_process(ProcessInfo(pid=123, name="code.exe", executable_path="C:\\Apps\\code.exe", cmdline=[]))

    report = plan.execute(is_sync_mode=True)

    status = report.app_statuses["a_snap"]
    assert status.window_moved is True
    assert status.window_snapped is True
    assert 9901 in window_provider.snapped_windows
    assert window_provider.snapped_windows[9901]["snap_mode"] == WindowSnap.RIGHT_HALF.value
    assert window_provider.snapped_windows[9901]["monitor_index"] == 1


def test_validator_rejects_negative_monitor_index():
    """Verifies validator flags invalid negative monitor index."""
    app = AppConfig(id="bad_mon", name="Bad Mon App", desktop=1, monitor_index=-2)
    errors, _ = ConfigValidator.validate_app(app)
    assert any("target monitor index must be >= 0" in e for e in errors)


def test_window_service_get_monitors_safe():
    """Verifies WindowService.get_monitors returns at least one monitor without crashing."""
    service = WindowService()
    monitors = service.get_monitors()
    assert len(monitors) >= 1
    assert isinstance(monitors[0], MonitorInfo)
    assert monitors[0].width > 0
    assert monitors[0].height > 0
