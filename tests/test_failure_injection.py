"""
Failure injection test suite per Section 87 of Master Prompt.
Simulates:
- provider unavailable / exceptions
- window move failures
- executable missing / unresolvable
- window detection timeouts
- cancellation / emergency stop
- partial operation failure and isolation across multiple apps
- automation disabled safety guard
- configuration file corruption and recovery from backup/defaults
"""

import os
import json
import pytest
from pathlib import Path
from app.models.workspace import (
    WorkspaceConfig,
    WorkspaceProfile,
    AppConfig,
    DesktopConfig,
    LaunchMode,
    WindowPolicy,
)
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockWindowProvider,
    MockProcessProvider,
    MockApplicationLauncher,
)
from app.providers.base import WindowInfo, ProcessInfo
from app.discovery.app_detector import AppDetector
from app.core.execution_plan import WorkspaceExecutionPlan
from app.core.manager import WorkspaceManager
from app.configuration.config_store import ConfigStore


@pytest.fixture
def isolated_env(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    store = ConfigStore(config_dir=config_dir)
    return store


def test_failure_injection_desktop_creation_failure(isolated_env):
    """Simulates internal COM error when creating a virtual desktop."""
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=1)
    desktop_provider.should_fail_create = True  # Injects creation exception

    window_provider = MockWindowProvider()
    proc_provider = MockProcessProvider()
    launcher = MockApplicationLauncher(auto_create_window=True, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    detector.detect_executable = lambda app: (app.executable, "mock_test")

    profile = WorkspaceProfile(
        id="p-fail-desktop",
        name="Fail Desktop Profile",
        desktops=[
            DesktopConfig(number=1, name="D1"),
            DesktopConfig(number=2, name="D2"),  # Requires desktop creation
        ],
        apps=[
            AppConfig(id="a1", name="App 1", executable="C:\\Apps\\app1.exe", desktop=2, window_timeout_ms=50)
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

    report = plan.execute(is_sync_mode=False)

    # Execution plan caught the error and recorded in report.errors without crashing
    assert len(report.errors) > 0
    assert any("Mock simulated desktop creation failure" in err for err in report.errors)
    assert report.total_desktops_found == 1


def test_failure_injection_window_move_failure(isolated_env):
    """Simulates failure when moving window to target desktop."""
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=2)
    desktop_provider.should_fail_move = True  # Window movement fails

    window_provider = MockWindowProvider()
    proc_provider = MockProcessProvider()
    launcher = MockApplicationLauncher(auto_create_window=True, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    detector.detect_executable = lambda app: (app.executable, "mock_test")

    profile = WorkspaceProfile(
        id="p-move-fail",
        name="Move Fail Profile",
        desktops=[DesktopConfig(number=1, name="D1"), DesktopConfig(number=2, name="D2")],
        apps=[
            AppConfig(id="a1", name="App 1", executable="C:\\Apps\\app1.exe", desktop=2, window_timeout_ms=50)
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

    report = plan.execute(is_sync_mode=False)

    assert report.app_statuses["a1"].window_found is True
    assert report.app_statuses["a1"].window_moved is False
    assert len(report.errors) > 0
    assert any("Failed to move HWND" in err for err in report.errors)


def test_failure_injection_executable_missing(isolated_env):
    """Simulates missing executable that cannot be resolved via discovery."""
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=2)
    window_provider = MockWindowProvider()
    proc_provider = MockProcessProvider()
    launcher = MockApplicationLauncher(auto_create_window=True, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    # detector left untouched: real os.path.exists checks will fail for nonexistent paths

    profile = WorkspaceProfile(
        id="p-missing-exe",
        name="Missing Exe Profile",
        desktops=[DesktopConfig(number=1, name="D1")],
        apps=[
            AppConfig(
                id="a_missing",
                name="NonExistentApp",
                executable="C:\\NonExistentFolder\\DoesNotExist123.exe",
                desktop=1,
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

    report = plan.execute(is_sync_mode=False)

    assert len(report.warnings) > 0
    assert any("executable could not be resolved" in w or "Cannot launch" in w for w in report.warnings)
    assert report.apps_launched_or_reused == 0


def test_failure_injection_window_detection_timeout(isolated_env):
    """Simulates launched process that never produces a visible top-level window."""
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=2)
    window_provider = MockWindowProvider()
    proc_provider = MockProcessProvider()
    # Launcher will NOT create a window (e.g. background service or hung splash screen)
    launcher = MockApplicationLauncher(auto_create_window=False, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    detector.detect_executable = lambda app: (app.executable, "mock_test")

    profile = WorkspaceProfile(
        id="p-timeout",
        name="Timeout Profile",
        desktops=[DesktopConfig(number=1, name="D1")],
        apps=[
            AppConfig(
                id="a_hang",
                name="HangingWindowApp",
                executable="C:\\Apps\\hang.exe",
                desktop=1,
                window_timeout_ms=50  # fast timeout
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

    report = plan.execute(is_sync_mode=False)

    assert report.app_statuses["a_hang"].was_launched is True
    assert report.app_statuses["a_hang"].window_found is False
    assert any("Timed out waiting for visible window" in w for w in report.warnings)


def test_failure_injection_cancellation_during_execution(isolated_env):
    """Simulates user triggering cancellation / emergency stop during plan execution."""
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=2)
    window_provider = MockWindowProvider()
    proc_provider = MockProcessProvider()
    launcher = MockApplicationLauncher(auto_create_window=True, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    detector.detect_executable = lambda app: (app.executable, "mock_test")

    profile = WorkspaceProfile(
        id="p-cancel",
        name="Cancel Profile",
        desktops=[DesktopConfig(number=1, name="D1"), DesktopConfig(number=2, name="D2")],
        apps=[
            AppConfig(id="a1", name="App 1", executable="C:\\Apps\\app1.exe", desktop=1, window_timeout_ms=50),
            AppConfig(id="a2", name="App 2", executable="C:\\Apps\\app2.exe", desktop=2, window_timeout_ms=50),
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

    # Cancel immediately before execution starts
    plan.cancel()
    report = plan.execute(is_sync_mode=False)

    assert report.cancelled is True
    assert report.apps_launched_or_reused == 0


def test_failure_injection_partial_failure_isolation(isolated_env):
    """
    Validates failure isolation: when App 1 succeeds, App 2 fails with missing exe,
    App 3 must continue and succeed independently.
    """
    desktop_provider = MockVirtualDesktopProvider(initial_desktop_count=3)
    window_provider = MockWindowProvider()
    proc_provider = MockProcessProvider()
    launcher = MockApplicationLauncher(auto_create_window=True, window_provider=window_provider, process_provider=proc_provider)
    detector = AppDetector(proc_provider)
    detector.detect_executable = lambda app: (
        (None, "not_found") if "bad" in app.executable
        else (app.executable, "mock_test")
    )

    profile = WorkspaceProfile(
        id="p-multi-fail",
        name="Multi App Isolation",
        desktops=[
            DesktopConfig(number=1, name="D1"),
            DesktopConfig(number=2, name="D2"),
            DesktopConfig(number=3, name="D3"),
        ],
        apps=[
            AppConfig(id="app_good_1", name="Good App 1", executable="C:\\Apps\\good1.exe", desktop=1, window_timeout_ms=50),
            AppConfig(id="app_bad_2", name="Bad App 2", executable="C:\\Fake\\bad.exe", desktop=2, window_timeout_ms=50),
            AppConfig(id="app_good_3", name="Good App 3", executable="C:\\Apps\\good3.exe", desktop=3, window_timeout_ms=50),
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

    report = plan.execute(is_sync_mode=False)

    assert report.app_statuses["app_good_1"].window_moved is True
    assert report.app_statuses["app_bad_2"].window_found is False
    assert report.app_statuses["app_good_3"].window_moved is True


def test_failure_injection_automation_disabled_guard(isolated_env):
    """Simulates attempting to run operations while automation is disabled in safety settings."""
    cfg = isolated_env.load()
    cfg.safety.automation_enabled = False
    isolated_env.save(cfg)

    manager = WorkspaceManager(config_store=isolated_env, desktop_provider=MockVirtualDesktopProvider())

    with pytest.raises(RuntimeError, match="Automation is currently paused/disabled"):
        manager.launch_workspace()

    with pytest.raises(RuntimeError, match="Automation is currently paused/disabled"):
        manager.sync_workspace()


def test_failure_injection_config_corruption_recovery(tmp_path):
    """Simulates corrupt JSON file on disk; ConfigStore should fail safely and load defaults."""
    config_dir = tmp_path / "corrupt_cfg"
    config_dir.mkdir(parents=True, exist_ok=True)
    cfg_file = config_dir / "workspace.json"

    # Write corrupt JSON bytes
    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON CONTENT !!! ")

    store = ConfigStore(config_dir=config_dir)

    # Should safely recover and load a default valid config
    loaded_cfg = store.load()
    assert isinstance(loaded_cfg, WorkspaceConfig)
    assert len(loaded_cfg.profiles) >= 1


def test_failure_injection_config_backup_recovery(tmp_path):
    """Simulates corrupt workspace.json with a valid backup available."""
    config_dir = tmp_path / "backup_recovery_cfg"
    config_dir.mkdir(parents=True, exist_ok=True)
    cfg_file = config_dir / "workspace.json"
    backup_file = config_dir / "workspace.backup.json"

    # Write corrupted main config
    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON CONTENT !!! ")

    # Write valid backup
    backup_data = {
        "schema_version": 1,
        "profiles": [
            {
                "id": "p-recovered",
                "name": "Recovered Profile",
                "desktops": [{"number": 1, "name": "RecDesktop"}],
                "apps": []
            }
        ]
    }
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f)

    store = ConfigStore(config_dir=config_dir)
    recovered_cfg = store.load()

    assert recovered_cfg.profiles[0].id == "p-recovered"
    assert recovered_cfg.profiles[0].name == "Recovered Profile"
