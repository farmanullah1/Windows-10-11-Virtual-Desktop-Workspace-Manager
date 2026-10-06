"""
Unit tests for ShortcutService (Desktop shortcuts management).
Guarantees 100% non-destructive isolated testing using temporary directories.
"""

import tempfile
from pathlib import Path
import pytest

from app.services.shortcut_service import (
    ShortcutService,
    SHORTCUT_CONFIG_NAME,
    SHORTCUT_RUN_NAME,
)


@pytest.fixture
def temp_desktop_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def test_shortcut_service_creation_and_check(temp_desktop_dir):
    service = ShortcutService(desktop_dir=temp_desktop_dir)

    # Initial state: shortcuts should not exist
    status = service.check_shortcuts_exist()
    assert status["config"] is False
    assert status["run"] is False

    # Create shortcuts
    dummy_project = temp_desktop_dir / "project"
    dummy_project.mkdir()
    (dummy_project / "main.py").write_text("# main", encoding="utf-8")

    res = service.create_desktop_shortcuts(project_dir=dummy_project)
    assert res["config"] is True
    assert res["run"] is True

    # Verify files created on desktop
    status = service.check_shortcuts_exist()
    assert status["config"] is True
    assert status["run"] is True
    assert (temp_desktop_dir / SHORTCUT_CONFIG_NAME).exists()
    assert (temp_desktop_dir / SHORTCUT_RUN_NAME).exists()


def test_shortcut_service_safe_removal_preserves_unrelated(temp_desktop_dir):
    service = ShortcutService(desktop_dir=temp_desktop_dir)

    # Place an unrelated user shortcut on Desktop
    unrelated_file = temp_desktop_dir / "Unrelated User App.lnk"
    unrelated_file.write_text("user data", encoding="utf-8")

    # Create manager shortcuts
    service.create_desktop_shortcuts(project_dir=temp_desktop_dir)
    assert (temp_desktop_dir / SHORTCUT_CONFIG_NAME).exists()
    assert (temp_desktop_dir / SHORTCUT_RUN_NAME).exists()
    assert unrelated_file.exists()

    # Remove shortcuts
    res = service.remove_desktop_shortcuts()
    assert res["config"] is True
    assert res["run"] is True

    # Verify owned shortcuts are removed
    assert not (temp_desktop_dir / SHORTCUT_CONFIG_NAME).exists()
    assert not (temp_desktop_dir / SHORTCUT_RUN_NAME).exists()

    # CRITICAL: Verify unrelated shortcut is completely untouched
    assert unrelated_file.exists()
    assert unrelated_file.read_text(encoding="utf-8") == "user data"
