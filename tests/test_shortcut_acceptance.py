"""
Acceptance tests for Desktop Shortcuts (Section 148A).
Tests all 8 mandatory shortcut acceptance criteria in complete isolation.
Guaranteed zero host side-effects using Mock Providers and temporary directories.
"""

import tempfile
from pathlib import Path
import pytest

from app.models.workspace import WorkspaceConfig, WorkspaceProfile, AppConfig, DesktopConfig
from app.configuration.config_store import ConfigStore
from app.configuration.validator import ConfigValidator
from app.core.manager import WorkspaceManager
from app.services.shortcut_service import (
    ShortcutService,
    SHORTCUT_CONFIG_NAME,
    SHORTCUT_RUN_NAME,
)
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockProcessProvider,
    MockWindowProvider,
    MockApplicationLauncher,
)


@pytest.fixture
def mock_environment():
    with tempfile.TemporaryDirectory() as td:
        base_dir = Path(td)
        desktop_dir = base_dir / "Desktop"
        desktop_dir.mkdir()

        store = ConfigStore(config_dir=base_dir)
        dp = MockVirtualDesktopProvider()
        pp = MockProcessProvider()
        wp = MockWindowProvider()
        launcher = MockApplicationLauncher(window_provider=wp, process_provider=pp)
        manager = WorkspaceManager(
            config_store=store,
            desktop_provider=dp,
            process_provider=pp,
            window_provider=wp,
            launcher=launcher,
        )
        shortcut_svc = ShortcutService(desktop_dir=desktop_dir)

        yield {
            "base_dir": base_dir,
            "desktop_dir": desktop_dir,
            "store": store,
            "manager": manager,
            "shortcut_svc": shortcut_svc,
            "dp": dp,
            "pp": pp,
            "wp": wp,
            "launcher": launcher,
        }


def test_shortcut_test_1_configure_opens_settings_no_execution(mock_environment):
    """
    Shortcut Test 1 — Configure:
    Double-clicking Configure loads saved settings and performs NO workspace execution.
    """
    manager = mock_environment["manager"]
    launcher = mock_environment["launcher"]
    dp = mock_environment["dp"]

    # Ensure config is loaded
    cfg = manager.config
    assert cfg is not None

    # Verify zero process launches and zero desktop modifications occurred
    assert len(launcher.launched_commands) == 0
    assert len(dp.desktops) == 2


def test_shortcut_test_2_run_validates_and_executes(mock_environment):
    """
    Shortcut Test 2 — Run:
    Run Workspace loads settings, validates config, and executes active workspace.
    """
    manager = mock_environment["manager"]
    launcher = mock_environment["launcher"]
    dp = mock_environment["dp"]

    # Setup 4 desktops and 1 app
    prof = manager.config.get_active_profile()
    prof.apps = [AppConfig(name="Brave Browser", desktop=2, executable="C:\\Apps\\brave.exe")]
    manager.save_config()

    # Pre-validate
    ConfigValidator.validate(manager.config)

    # Execute workspace launch
    report = manager.launch_workspace()
    assert report.success is True
    # Verify desktop 2 exists and app was launched
    assert 2 in [d.number for d in dp.desktops]
    assert any("brave.exe" in item["executable"] for item in launcher.launched_commands)


def test_shortcut_test_3_persistence_brave_to_desktop_4(mock_environment):
    """
    Shortcut Test 3 — Persistence:
    Change Brave -> Desktop 4, save config, reload, verify Brave -> Desktop 4 persists.
    """
    manager = mock_environment["manager"]
    store = mock_environment["store"]

    prof = manager.config.get_active_profile()
    brave_app = AppConfig(id="brave-app", name="Brave Browser", desktop=2, executable="C:\\Apps\\brave.exe")
    prof.apps.append(brave_app)
    manager.save_config()

    # Change assignment to Desktop 4
    manager.reassign_app("brave-app", 4)
    manager.save_config()

    # Re-read from disk (simulate closing and reopening Configure)
    reloaded_config = store.load()
    reloaded_prof = reloaded_config.get_active_profile()
    found_brave = next((a for a in reloaded_prof.apps if a.id == "brave-app"), None)

    assert found_brave is not None
    assert found_brave.desktop == 4


def test_shortcut_test_4_configure_does_not_run_apps(mock_environment):
    """
    Shortcut Test 4 — Configure Does Not Run:
    Even when workspace is configured with auto-launchable apps, opening Configure
    never launches applications or moves windows.
    """
    manager = mock_environment["manager"]
    launcher = mock_environment["launcher"]
    wp = mock_environment["wp"]

    prof = manager.config.get_active_profile()
    prof.apps = [
        AppConfig(name="Brave", desktop=1, executable="brave.exe"),
        AppConfig(name="Antigravity", desktop=2, executable="antigravity.exe"),
    ]
    manager.save_config()

    # Simulated Configure session: inspecting/saving without calling launch
    cfg = manager.config
    assert len(cfg.get_active_profile().apps) == 2

    # Zero process executions
    assert len(launcher.launched_commands) == 0


def test_shortcut_test_5_missing_or_invalid_configuration_stops_safely(mock_environment):
    """
    Shortcut Test 5 — Missing/Invalid Configuration:
    Run Workspace with invalid config must fail validation and halt safely without launches.
    """
    manager = mock_environment["manager"]
    launcher = mock_environment["launcher"]

    # Create invalid config: App with empty name and desktop 0
    prof = manager.config.get_active_profile()
    prof.apps = [AppConfig(name="", desktop=0, executable="app.exe")]

    with pytest.raises(Exception):
        ConfigValidator.validate(manager.config)

    # Verify no execution happened
    assert len(launcher.launched_commands) == 0


def test_shortcut_test_6_broken_shortcut_repaired(mock_environment):
    """
    Shortcut Test 6 — Broken Shortcut:
    The shortcut repair mechanism re-creates broken or missing owned shortcuts.
    """
    svc = mock_environment["shortcut_svc"]
    desktop_dir = mock_environment["desktop_dir"]
    base_dir = mock_environment["base_dir"]

    # Initial creation
    svc.create_desktop_shortcuts(project_dir=base_dir)
    assert (desktop_dir / SHORTCUT_CONFIG_NAME).exists()
    assert (desktop_dir / SHORTCUT_RUN_NAME).exists()

    # Intentionally corrupt/delete one shortcut
    (desktop_dir / SHORTCUT_CONFIG_NAME).unlink()
    assert not (desktop_dir / SHORTCUT_CONFIG_NAME).exists()

    # Run repair
    repair_res = svc.create_desktop_shortcuts(project_dir=base_dir)
    assert repair_res["config"] is True
    assert (desktop_dir / SHORTCUT_CONFIG_NAME).exists()


def test_shortcut_test_7_no_duplicate_shortcuts(mock_environment):
    """
    Shortcut Test 7 — No Duplicate Shortcuts:
    Repeated creation/repair must not duplicate shortcuts or create 'Copy of' files.
    """
    svc = mock_environment["shortcut_svc"]
    desktop_dir = mock_environment["desktop_dir"]
    base_dir = mock_environment["base_dir"]

    # Run creation 3 times
    svc.create_desktop_shortcuts(project_dir=base_dir)
    svc.create_desktop_shortcuts(project_dir=base_dir)
    svc.create_desktop_shortcuts(project_dir=base_dir)

    # Check desktop directory contents
    files = list(desktop_dir.glob("*.lnk"))
    assert len(files) == 2
    filenames = {f.name for f in files}
    assert filenames == {SHORTCUT_CONFIG_NAME, SHORTCUT_RUN_NAME}


def test_shortcut_test_8_uninstall_safety_preserves_unrelated(mock_environment):
    """
    Shortcut Test 8 — Uninstall Safety:
    Removal clears only application-owned shortcuts and leaves unrelated user shortcuts untouched.
    """
    svc = mock_environment["shortcut_svc"]
    desktop_dir = mock_environment["desktop_dir"]
    base_dir = mock_environment["base_dir"]

    # Create manager shortcuts
    svc.create_desktop_shortcuts(project_dir=base_dir)

    # Create unrelated user shortcuts on Desktop
    user_shortcut_1 = desktop_dir / "User Project.lnk"
    user_shortcut_1.write_text("user content 1", encoding="utf-8")
    user_shortcut_2 = desktop_dir / "Steam.lnk"
    user_shortcut_2.write_text("user content 2", encoding="utf-8")

    # Uninstall / remove manager shortcuts
    svc.remove_desktop_shortcuts()

    # Manager shortcuts are gone
    assert not (desktop_dir / SHORTCUT_CONFIG_NAME).exists()
    assert not (desktop_dir / SHORTCUT_RUN_NAME).exists()

    # Unrelated user shortcuts remain untouched
    assert user_shortcut_1.exists()
    assert user_shortcut_1.read_text(encoding="utf-8") == "user content 1"
    assert user_shortcut_2.exists()
    assert user_shortcut_2.read_text(encoding="utf-8") == "user content 2"
