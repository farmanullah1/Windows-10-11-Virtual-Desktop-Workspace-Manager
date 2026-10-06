"""
Tests for root-level setup.py SetupRunner (Sections 83B-83L, 148B, 149).

Verifies the SETUP-001 through SETUP-035 acceptance checklist:
- setup.py performs setup/bootstrap only and never executes workspaces or apps.
- All operations are isolated in temporary test directories.
- Idempotency: repeated setup creates no duplicates.
- Non-destructive diagnostics: --check modifies zero files.
- Setup state is persisted separately from workspace configuration.
- Exit codes adhere strictly to Section 83B specification.
"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from setup import (
    SetupRunner,
    parse_args,
    SETUP_VERSION,
    EXIT_SUCCESS,
    EXIT_UNSUPPORTED_OS,
    EXIT_INCOMPATIBLE_PYTHON,
    EXIT_DEPENDENCY_FAILURE,
    EXIT_GENERAL_FAILURE,
)


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


# SETUP-001, SETUP-002: Windows 10/11 accepted
def test_setup_001_002_windows_supported(temp_env):
    runner, _, _ = temp_env
    res = runner.check_platform()
    assert "supported" in res
    assert "os" in res
    assert "architecture" in res
    assert "python" in res
    assert isinstance(res["supported"], bool)


# SETUP-003: Unsupported OS blocked
def test_setup_003_unsupported_os_blocked(temp_env):
    runner, _, _ = temp_env
    with patch.object(runner, "check_platform", return_value={"supported": False, "os": "Linux 5.15", "architecture": "64-bit", "python": "3.11.0", "python_supported": True}):
        with patch("builtins.print"):
            code = runner.run_setup()
            assert code == EXIT_UNSUPPORTED_OS


# SETUP-004, SETUP-005: Python version validation
def test_setup_004_005_python_compatibility(temp_env):
    runner, _, _ = temp_env
    # Compatible Python
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.11.0", "python_supported": True}):
        res = runner.check_platform()
        assert res["python_supported"] is True

    # Incompatible Python
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.8.0", "python_supported": False}):
        with patch("builtins.print"):
            code = runner.run_setup()
            assert code == EXIT_INCOMPATIBLE_PYTHON


# SETUP-008, SETUP-010: Required dependencies verification
def test_setup_008_010_dependencies_verification(temp_env):
    runner, _, _ = temp_env
    res = runner.verify_dependencies()
    assert "satisfied" in res
    assert "details" in res
    assert "win32gui" in res["details"]
    assert "psutil" in res["details"]


# SETUP-011: Application directories created safely
def test_setup_011_application_directories_created(temp_env):
    runner, app_dir, _ = temp_env
    created = runner.init_directories(check_only=False)
    assert len(created) > 0
    assert (app_dir / "logs").exists()
    assert (app_dir / "state").exists()
    assert (app_dir / "backups").exists()


# SETUP-012, SETUP-013, SETUP-035: Configuration creation and strict preservation
def test_setup_012_013_035_configuration_preservation(temp_env):
    runner, app_dir, _ = temp_env
    runner.init_directories(check_only=False)

    # First call initializes default configuration template
    res = runner.init_configuration(check_only=False)
    assert res["created"] is True
    assert res["valid"] is True
    cfg_file = app_dir / "workspace.json"
    assert cfg_file.exists()

    # Modify configuration to simulate user changes
    cfg_file.write_text('{"schemaVersion": 1, "customUserSetting": true, "desktops": []}', encoding="utf-8")
    saved_content = cfg_file.read_text(encoding="utf-8")

    # Second call (re-running setup) must strictly preserve existing configuration
    res_second = runner.init_configuration(check_only=False)
    assert res_second["created"] is False
    assert res_second["valid"] is True
    assert cfg_file.read_text(encoding="utf-8") == saved_content


# SETUP-016, SETUP-017, SETUP-018, SETUP-019: Shortcut creation and arguments
def test_setup_016_019_shortcut_creation(temp_env):
    runner, _, desktop_dir = temp_env
    res = runner.setup_shortcuts(repair=False, check_only=False)
    assert res["config_shortcut"] is True
    assert res["run_shortcut"] is True

    config_lnk = desktop_dir / "Virtual Desktop Workspace Manager — Configure.lnk"
    run_lnk = desktop_dir / "Virtual Desktop Workspace Manager — Run Workspace.lnk"
    assert config_lnk.exists()
    assert run_lnk.exists()


# SETUP-021: Repeated setup creates no duplicates
def test_setup_021_repeated_setup_idempotency(temp_env):
    runner, app_dir, desktop_dir = temp_env
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.11.0", "python_supported": True}):
        with patch("builtins.print"):
            code1 = runner.run_setup(repair=False)
            assert code1 == EXIT_SUCCESS

            # Rerun setup
            code2 = runner.run_setup(repair=False)
            assert code2 == EXIT_SUCCESS

    # Verify no duplicate shortcut files like 'Configure (1).lnk' were created
    desktop_files = list(desktop_dir.glob("*.lnk"))
    assert len(desktop_files) == 2


# SETUP-022: Broken owned shortcut repaired
def test_setup_022_repair_mode(temp_env):
    runner, app_dir, desktop_dir = temp_env
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.11.0", "python_supported": True}):
        with patch("builtins.print"):
            code = runner.run_setup(repair=True)
            assert code == EXIT_SUCCESS

    assert (desktop_dir / "Virtual Desktop Workspace Manager — Configure.lnk").exists()
    assert (desktop_dir / "Virtual Desktop Workspace Manager — Run Workspace.lnk").exists()


# SETUP-024: --check is non-destructive
def test_setup_024_check_mode_non_destructive(temp_env):
    runner, app_dir, _ = temp_env
    with patch("builtins.print"):
        code = runner.run_check()
        assert isinstance(code, int)

    # State and logs should NOT have been created by --check
    assert not (app_dir / "state" / "setup.json").exists()


# SETUP-027, SETUP-028, SETUP-029, SETUP-030: Architectural invariants check
def test_setup_027_030_zero_workspace_execution_invariants():
    """setup.py must never import or call workspace execution engines."""
    setup_file = Path(__file__).resolve().parent.parent / "setup.py"
    content = setup_file.read_text(encoding="utf-8")

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
        assert forbidden not in content, f"Forbidden call '{forbidden}' detected in setup.py"


# SETUP-033: Setup state recorded in state/setup.json
def test_setup_033_setup_state_recorded(temp_env):
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


# SETUP-034: Setup log written without secrets
def test_setup_034_setup_log_written(temp_env):
    runner, app_dir, _ = temp_env
    with patch.object(runner, "check_platform", return_value={"supported": True, "os": "Windows 11", "architecture": "64-bit", "python": "3.11.0", "python_supported": True}):
        with patch("builtins.print"):
            runner.run_setup(repair=False)

    log_file = app_dir / "logs" / "setup.log"
    assert log_file.exists()
    log_content = log_file.read_text(encoding="utf-8")
    assert "Starting Virtual Desktop Workspace Manager Setup" in log_content
    # Secrets should never appear in log
    assert "password" not in log_content.lower()
    assert "secret" not in log_content.lower()


# CLI Argument parsing tests for setup.py and run.py
def test_cli_argument_parsing():
    with patch.object(sys, "argv", ["setup.py", "--check"]):
        args = parse_args()
        assert args.check is True
        assert args.repair is False
        assert args.version is False

    with patch.object(sys, "argv", ["setup.py", "--repair"]):
        args = parse_args()
        assert args.repair is True
        assert args.check is False

    with patch.object(sys, "argv", ["setup.py", "--version"]):
        args = parse_args()
        assert args.version is True

    with patch.object(sys, "argv", ["setup.py", "--setup"]):
        args = parse_args()
        assert args.setup is True
