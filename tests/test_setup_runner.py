"""
Tests for root-level run.py SetupRunner (Sections 83B-83L, 148A, 149).

Ensures:
- run.py performs setup/bootstrap only and never executes workspaces or apps.
- All operations are isolated in temporary directories.
- Idempotency: repeated setup creates no duplicates.
- Non-destructive diagnostics: --check modifies zero files.
- Setup state is persisted separately from workspace configuration.
"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from run import SetupRunner, parse_args, SETUP_VERSION


@pytest.fixture
def temp_env():
    """Provides isolated temporary application data and desktop directories."""
    with tempfile.TemporaryDirectory() as temp_app_data, tempfile.TemporaryDirectory() as temp_desktop:
        app_dir = Path(temp_app_data)
        desktop_dir = Path(temp_desktop)
        runner = SetupRunner(app_data_dir=app_dir, desktop_dir=desktop_dir)
        try:
            yield runner, app_dir, desktop_dir
        finally:
            runner.close()


def test_platform_check(temp_env):
    runner, _, _ = temp_env
    res = runner.check_platform()
    assert "supported" in res
    assert "os" in res
    assert "architecture" in res
    assert "python" in res
    assert isinstance(res["supported"], bool)


def test_verify_dependencies(temp_env):
    runner, _, _ = temp_env
    res = runner.verify_dependencies()
    assert "satisfied" in res
    assert "details" in res
    assert "win32gui" in res["details"]
    assert "psutil" in res["details"]


def test_init_directories_check_only(temp_env):
    runner, app_dir, _ = temp_env
    created = runner.init_directories(check_only=True)
    assert len(created) > 0
    # In check_only mode, directories should NOT be created
    assert not (app_dir / "logs").exists()
    assert not (app_dir / "state").exists()
    assert not (app_dir / "backups").exists()


def test_init_directories_execution(temp_env):
    runner, app_dir, _ = temp_env
    created = runner.init_directories(check_only=False)
    assert len(created) > 0
    assert (app_dir / "logs").exists()
    assert (app_dir / "state").exists()
    assert (app_dir / "backups").exists()

    # Second call should be idempotent (nothing created)
    created_again = runner.init_directories(check_only=False)
    assert len(created_again) == 0


def test_init_configuration_default_and_preservation(temp_env):
    runner, app_dir, _ = temp_env
    runner.init_directories(check_only=False)

    # First call initializes default
    res = runner.init_configuration(check_only=False)
    assert res["created"] is True
    assert res["valid"] is True
    cfg_file = app_dir / "workspace.json"
    assert cfg_file.exists()

    # Read content to ensure preservation
    original_content = cfg_file.read_text(encoding="utf-8")

    # Second call preserves configuration
    res_second = runner.init_configuration(check_only=False)
    assert res_second["created"] is False
    assert res_second["valid"] is True
    assert cfg_file.read_text(encoding="utf-8") == original_content


def test_save_setup_state(temp_env):
    runner, app_dir, _ = temp_env
    runner.init_directories(check_only=False)
    runner.save_setup_state(status="complete")

    state_file = app_dir / "state" / "setup.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert data["setupSchemaVersion"] == 1
    assert data["applicationVersion"] == SETUP_VERSION
    assert data["setupStatus"] == "complete"
    assert "pythonVersion" in data
    assert "lastSetupTime" in data


def test_setup_shortcuts_in_mock_environment(temp_env):
    runner, _, desktop_dir = temp_env
    res = runner.setup_shortcuts(repair=False, check_only=False)
    assert "config_shortcut" in res
    assert "run_shortcut" in res

    # Shortcuts must exist in desktop_dir
    assert (desktop_dir / "Virtual Desktop Workspace Manager — Configure.lnk").exists()
    assert (desktop_dir / "Virtual Desktop Workspace Manager — Run Workspace.lnk").exists()


def test_run_check_non_destructive(temp_env):
    runner, app_dir, _ = temp_env
    # run_check should run without modifying the disk
    with patch("builtins.print"):
        result = runner.run_check()
        assert isinstance(result, bool)

    # State file should NOT have been created by run_check
    assert not (app_dir / "state" / "setup.json").exists()


def test_run_setup_end_to_end(temp_env):
    runner, app_dir, desktop_dir = temp_env
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.11.0"}):
        with patch("builtins.print"):
            success = runner.run_setup(repair=False)
            assert success is True

    # Directories, configuration, shortcuts, and state must exist
    assert (app_dir / "logs").exists()
    assert (app_dir / "state" / "setup.json").exists()
    assert (app_dir / "workspace.json").exists()
    assert (desktop_dir / "Virtual Desktop Workspace Manager — Configure.lnk").exists()
    assert (desktop_dir / "Virtual Desktop Workspace Manager — Run Workspace.lnk").exists()


def test_run_setup_repair_mode(temp_env):
    runner, app_dir, desktop_dir = temp_env
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.11.0"}):
        with patch("builtins.print"):
            # Run repair mode
            success = runner.run_setup(repair=True)
            assert success is True

    assert (desktop_dir / "Virtual Desktop Workspace Manager — Configure.lnk").exists()
    assert (desktop_dir / "Virtual Desktop Workspace Manager — Run Workspace.lnk").exists()


def test_run_py_has_zero_workspace_execution_calls():
    """Architectural invariant: run.py must never call workspace execution APIs."""
    run_file = Path(__file__).resolve().parent.parent / "run.py"
    content = run_file.read_text(encoding="utf-8")

    # Invariants from Section 83B & 151
    forbidden_calls = [
        "WorkspaceManager(",
        "execute_workspace",
        "sync_workspace",
        "MockVirtualDesktopProvider",
        "VirtualDesktopService(",
        "ApplicationLauncher(",
        "subprocess.Popen([\"brave\"",
    ]
    for forbidden in forbidden_calls:
        assert forbidden not in content, f"Forbidden execution call '{forbidden}' detected in run.py"


def test_cli_argument_parsing():
    """Verify supported CLI options in run.py."""
    with patch.object(sys, "argv", ["run.py", "--check"]):
        args = parse_args()
        assert args.check is True
        assert args.repair is False
        assert args.version is False

    with patch.object(sys, "argv", ["run.py", "--repair"]):
        args = parse_args()
        assert args.repair is True
        assert args.check is False

    with patch.object(sys, "argv", ["run.py", "--version"]):
        args = parse_args()
        assert args.version is True

    with patch.object(sys, "argv", ["run.py", "--setup"]):
        args = parse_args()
        assert args.setup is True
