"""
Acceptance Scenario Tests matching Section 106 and Section 68 specifications.
Uses isolated mock providers so tests run 100% safely without modifying host virtual desktops or applications.
"""

import tempfile
import pytest
from pathlib import Path

from app.models.workspace import (
    WorkspaceConfig,
    WorkspaceProfile,
    DesktopConfig,
    AppConfig,
    LaunchMode,
    WindowPolicy,
)
from app.configuration.config_store import ConfigStore
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockWindowProvider,
    MockProcessProvider,
    MockApplicationLauncher,
)
from app.providers.base import WindowInfo, ProcessInfo
from app.discovery.app_detector import AppDetector
from app.core.manager import WorkspaceManager
from app.core.execution_plan import WorkspaceExecutionPlan


@pytest.fixture
def test_setup():
    with tempfile.TemporaryDirectory() as td:
        store = ConfigStore(config_dir=Path(td))
        config = store.load()

        # Optimize timings for fast testing
        for app in config.get_active_profile().apps:
            app.launch_delay_ms = 0
            app.window_timeout_ms = 50

        desktop_prov = MockVirtualDesktopProvider(initial_desktop_count=2)
        window_prov = MockWindowProvider()
        process_prov = MockProcessProvider()
        launcher = MockApplicationLauncher(
            auto_create_window=True,
            window_provider=window_prov,
            process_provider=process_prov
        )

        manager = WorkspaceManager(
            config_store=store,
            desktop_provider=desktop_prov,
            window_provider=window_prov,
            process_provider=process_prov,
            launcher=launcher
        )
        # Isolate detection in tests
        manager.app_detector.shortcut_resolver._cache = []
        manager.app_detector.detect_executable = lambda app: (
            (None, "not_found") if "ghost" in app.executable
            else (f"C:\\Mock\\{app.id}.exe", "mock_test")
        )

        yield {
            "manager": manager,
            "desktop_prov": desktop_prov,
            "window_prov": window_prov,
            "process_prov": process_prov,
            "launcher": launcher,
            "store": store
        }


def test_scenario_1_create_missing_desktops(test_setup):
    """
    Scenario 1:
    User has 2 Virtual Desktops. Workspace requires 4.
    Result: 2 additional desktops created. Total is 4.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]

    assert dp.get_desktop_count() == 2
    report = m.launch_workspace()

    assert dp.get_desktop_count() == 4
    assert report.desktops_created == 2
    assert report.total_desktops_found == 4


def test_scenario_2_already_has_sufficient_desktops(test_setup):
    """
    Scenario 2:
    User already has 4 desktops.
    Result: No additional desktops created.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]
    dp.create_desktop()  # now 3
    dp.create_desktop()  # now 4
    assert dp.get_desktop_count() == 4

    report = m.launch_workspace()
    assert report.desktops_created == 0
    assert dp.get_desktop_count() == 4


def test_scenario_3_preserve_extra_desktops(test_setup):
    """
    Scenario 3:
    User has 6 desktops. Workspace requires 4.
    Result: Existing 6 desktops preserved. No desktops destroyed.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]
    for _ in range(4):
        dp.create_desktop()
    assert dp.get_desktop_count() == 6

    report = m.launch_workspace()
    assert report.desktops_created == 0
    assert dp.get_desktop_count() == 6


def test_scenario_4_reuse_existing_running_app(test_setup):
    """
    Scenario 4:
    Brave is already running.
    Result: No unnecessary duplicate launch. Existing window assigned to configured desktop.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]
    wp = test_setup["window_prov"]
    pp = test_setup["process_prov"]
    launcher = test_setup["launcher"]

    # Pre-populate running Brave process and window
    brave_proc = ProcessInfo(pid=1234, name="brave.exe", executable_path="C:\\Program Files\\Brave\\brave.exe", cmdline=[])
    pp.add_process(brave_proc)
    brave_win = WindowInfo(hwnd=999, title="Brave Browser - Home", pid=1234, executable="", is_visible=True, is_minimized=False, is_maximized=False)
    wp.add_window(brave_win)

    report = m.launch_workspace()

    # Verify Brave was NOT launched as a new process
    brave_launches = [c for c in launcher.launched_commands if "brave" in c["executable"].lower()]
    assert len(brave_launches) == 0

    # Verify window was moved to Desktop 1
    assert dp.window_assignments[999] == 1


def test_scenario_5_launch_missing_app(test_setup):
    """
    Scenario 5:
    Postman is not running.
    Result: Postman launched, window detected, window assigned to Desktop 4.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]
    launcher = test_setup["launcher"]

    # Set mock executable for postman so resolver finds it
    prof = m.config.get_active_profile()
    postman_app = next(a for a in prof.apps if a.id == "postman")
    postman_app.executable = "C:\\Tools\\Postman.exe"

    report = m.launch_workspace()

    # Verify Postman was launched
    postman_launches = [c for c in launcher.launched_commands if "postman" in c["executable"].lower()]
    assert len(postman_launches) == 1

    # Verify window was assigned to Desktop 4
    status = report.app_statuses.get("postman")
    assert status is not None
    assert status.window_moved is True
    assert status.target_desktop == 4


def test_scenario_6_missing_uninstalled_app_isolated(test_setup):
    """
    Scenario 6:
    An application is not installed / not found.
    Result: Warning displayed. Other applications continue (failure isolation).
    """
    m = test_setup["manager"]
    prof = m.config.get_active_profile()

    # Point postman to non-existent path
    postman_app = next(a for a in prof.apps if a.id == "postman")
    postman_app.executable = "C:\\NonExistentPath\\postman_ghost.exe"

    report = m.launch_workspace()

    # Verify other apps proceeded
    assert report.apps_configured == 4
    assert len(report.warnings) > 0
    # Process continues safely
    assert report.cancelled is False


def test_scenario_7_multiple_apps_on_one_desktop(test_setup):
    """
    Scenario 7:
    Desktop 2 contains multiple apps (Antigravity, VS Code, Git Bash).
    Result: All three can be assigned to Desktop 2.
    """
    m = test_setup["manager"]
    prof = m.config.get_active_profile()

    # Add VS Code and Git Bash to Desktop 2
    prof.apps.append(AppConfig(id="vscode", name="VS Code", executable="C:\\Code.exe", desktop=2, enabled=True))
    prof.apps.append(AppConfig(id="gitbash", name="Git Bash", executable="C:\\git-bash.exe", desktop=2, enabled=True))
    m.save_config()

    report = m.launch_workspace()
    desktop_2_apps = [s for s in report.app_statuses.values() if s.target_desktop == 2]
    assert len(desktop_2_apps) >= 3


def test_scenario_8_reassign_app_desktop(test_setup):
    """
    Scenario 8:
    User moves Brave from Desktop 1 to Desktop 4 in UI.
    Result: Configuration saved, future workspace launches use Desktop 4.
    """
    m = test_setup["manager"]
    success = m.reassign_app("brave", 4)
    assert success is True

    reloaded_prof = m.config.get_active_profile()
    brave_app = next(a for a in reloaded_prof.apps if a.id == "brave")
    assert brave_app.desktop == 4


def test_scenario_9_add_docker_desktop(test_setup):
    """
    Scenario 9:
    User adds Docker Desktop to Desktop 2.
    Result: Existing applications remain, Docker Desktop is added.
    """
    m = test_setup["manager"]
    initial_count = len(m.config.get_active_profile().apps)

    m.add_app_to_profile(AppConfig(
        id="docker",
        name="Docker Desktop",
        executable="C:\\Program Files\\Docker\\Docker Desktop.exe",
        desktop=2
    ))

    active_prof = m.config.get_active_profile()
    assert len(active_prof.apps) == initial_count + 1
    assert any(a.id == "docker" and a.desktop == 2 for a in active_prof.apps)


def test_scenario_10_idempotency_double_launch(test_setup):
    """
    Scenario 10:
    User runs Launch Workspace twice.
    Result: No unnecessary duplicate desktops, no duplicate processes.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]

    report1 = m.launch_workspace()
    desktops_after_run1 = dp.get_desktop_count()

    report2 = m.launch_workspace()
    desktops_after_run2 = dp.get_desktop_count()

    # Desktop count remains identical
    assert desktops_after_run1 == desktops_after_run2 == 4
    assert report2.desktops_created == 0


def test_scenario_11_sync_workspace_no_unnecessary_launches(test_setup):
    """
    Scenario 11:
    Sync Workspace reconciles window locations without launching unneeded instances.
    """
    m = test_setup["manager"]
    dp = test_setup["desktop_prov"]
    wp = test_setup["window_prov"]
    pp = test_setup["process_prov"]
    launcher = test_setup["launcher"]

    # Brave is running, but on Desktop 3 (wrong desktop)
    brave_proc = ProcessInfo(pid=5555, name="brave.exe", executable_path="C:\\brave.exe", cmdline=[])
    pp.add_process(brave_proc)
    brave_win = WindowInfo(hwnd=777, title="Brave", pid=5555, executable="", is_visible=True, is_minimized=False, is_maximized=False)
    wp.add_window(brave_win)
    dp.window_assignments[777] = 3  # placed on wrong desktop 3

    # Sync workspace
    report = m.sync_workspace()

    # Reconciled to Desktop 1!
    assert dp.window_assignments[777] == 1

    # In sync mode, apps not running are not launched
    assert len(launcher.launched_commands) == 0
