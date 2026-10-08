"""
Unit tests for Operation History persistence (Section 29), State Machine (Section 37),
and Window Matching Test Tool (Section 43).
"""

import tempfile
from pathlib import Path
from app.models.report import ExecutionReport
from app.models.history import OperationHistoryRecord
from app.models.state import ApplicationState, OperationPhase
from app.models.workspace import AppConfig
from app.configuration.config_store import ConfigStore
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockProcessProvider,
    MockWindowProvider,
    MockApplicationLauncher,
)
from app.providers.base import ProcessInfo, WindowInfo
from app.core.manager import WorkspaceManager


def test_operation_state_enums():
    assert ApplicationState.READY.value == "READY"
    assert ApplicationState.RUNNING.value == "RUNNING"
    assert ApplicationState.CONFIGURATION_DIRTY.value == "CONFIGURATION_DIRTY"
    assert ApplicationState.COMPLETED_WITH_WARNINGS.value == "COMPLETED_WITH_WARNINGS"

    assert OperationPhase.IDLE.value == "Idle"
    assert OperationPhase.EXECUTE.value == "Execute"


def test_history_persistence():
    with tempfile.TemporaryDirectory() as td:
        store = ConfigStore(config_dir=Path(td))

        report = ExecutionReport(
            operation_type="Launch",
            total_desktops_target=4,
            total_desktops_found=4,
            desktops_created=0,
            apps_configured=3,
            apps_detected=3,
            apps_launched_or_reused=3,
            apps_assigned=3
        )
        report.finish()

        rec = OperationHistoryRecord.from_report(report, profile_name="Development")
        store.save_history_record(rec)

        records = store.get_history_records()
        assert len(records) == 1
        assert records[0].operation_type == "Launch"
        assert records[0].profile_name == "Development"
        assert records[0].result == "Success"

        # Clear history
        store.clear_history()
        assert len(store.get_history_records()) == 0


def test_test_match_app_diagnostic_tool():
    with tempfile.TemporaryDirectory() as td:
        store = ConfigStore(config_dir=Path(td))
        dp = MockVirtualDesktopProvider(initial_desktop_count=3)
        pp = MockProcessProvider()
        wp = MockWindowProvider()
        launcher = MockApplicationLauncher()

        # Add a running process and window
        proc = ProcessInfo(pid=5555, name="brave.exe", executable_path="C:\\Brave\\brave.exe", cmdline=[])
        pp.add_process(proc)
        win = WindowInfo(
            hwnd=1001,
            title="Brave Browser - GitHub Project",
            pid=5555,
            executable="C:\\Brave\\brave.exe",
            is_visible=True,
            is_minimized=False,
            is_maximized=False
        )
        wp.add_window(win)
        dp.move_window_to_desktop(1001, 2)

        mgr = WorkspaceManager(
            config_store=store,
            desktop_provider=dp,
            window_provider=wp,
            process_provider=pp,
            launcher=launcher
        )

        app = AppConfig(
            id="brave",
            name="Brave",
            executable="C:\\Brave\\brave.exe",
            process_names=["brave.exe"],
            title_pattern="GitHub",
            window_policy="title_contains"
        )

        results = mgr.test_match_app(app)

        assert len(results) == 1
        res = results[0]
        assert res["matched"] is True
        assert res["pid"] == 5555
        assert res["hwnd"] == "0x000003E9"
        assert "Desktop 2" in res["desktop"]
        assert "95%" in res["confidence"]
        assert res["pid_matched"] is True
        assert res["title_matched"] is True
