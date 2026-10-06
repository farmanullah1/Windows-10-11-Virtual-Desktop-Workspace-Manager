"""
Unit tests for configuration persistence, validation, migration, backups, and import/export.
Uses isolated temporary directories to guarantee zero effect on host system.
"""

import os
import json
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
from app.configuration.validator import ConfigValidator, ConfigValidationError
from app.configuration.migration import ConfigMigration


@pytest.fixture
def temp_config_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def test_default_config_creation(temp_config_dir):
    store = ConfigStore(config_dir=temp_config_dir)
    cfg = store.load()

    assert cfg.schema_version == 1
    assert len(cfg.profiles) >= 1
    active = cfg.get_active_profile()
    assert len(active.desktops) == 4
    assert len(active.apps) == 4
    assert active.desktops[0].name == "Browser"
    assert active.desktops[1].name == "Development"
    assert active.desktops[2].name == "Database"
    assert active.desktops[3].name == "API Development"


def test_config_atomic_save_and_backup(temp_config_dir):
    store = ConfigStore(config_dir=temp_config_dir)
    cfg = store.load()

    # Modify
    active = cfg.get_active_profile()
    active.desktops[0].name = "Web & Communication"
    store.save(cfg)

    # Reload and verify
    reloaded = store.load()
    assert reloaded.get_active_profile().desktops[0].name == "Web & Communication"

    # Verify backup exists
    assert store.backup_file.exists()


def test_malformed_config_recovery(temp_config_dir):
    store = ConfigStore(config_dir=temp_config_dir)
    cfg = store.load()
    store.save(cfg)

    # Corrupt main file
    store.config_file.write_text("CORRUPTED_JSON_NOT_VALID", encoding="utf-8")

    # Load should fallback to backup gracefully
    recovered = store.load()
    assert recovered is not None
    assert len(recovered.profiles) >= 1


def test_schema_migration_v0():
    old_data = {
        "apps": [
            {
                "id": "brave",
                "name": "Brave",
                "executable": "brave.exe",
                "desktop": 1,
                "launchIfMissing": True
            }
        ],
        "desktops": [
            {"number": 1, "name": "Web"}
        ]
    }
    migrated = ConfigMigration.migrate(old_data)
    assert migrated["schema_version"] == 1
    assert "profiles" in migrated
    assert len(migrated["profiles"]) == 1
    assert migrated["profiles"][0]["apps"][0]["launch_mode"] == LaunchMode.LAUNCH_IF_MISSING.value


def test_config_validation_rejection():
    # Duplicate app ID in same profile should raise validation error
    bad_profile = WorkspaceProfile(
        id="bad",
        name="Bad Profile",
        desktops=[DesktopConfig(number=1, name="D1")],
        apps=[
            AppConfig(id="dup", name="App1", desktop=1),
            AppConfig(id="dup", name="App2", desktop=1)
        ]
    )
    bad_cfg = WorkspaceConfig(profiles=[bad_profile])
    errors, warnings = ConfigValidator.validate_config(bad_cfg)
    assert any("Duplicate application ID 'dup'" in e for e in errors)


def test_profile_import_export(temp_config_dir):
    store = ConfigStore(config_dir=temp_config_dir)
    cfg = store.load()
    prof = cfg.get_active_profile()

    export_path = temp_config_dir / "exported_profile.json"
    store.export_profile(prof, export_path)
    assert export_path.exists()

    imported = store.import_profile(export_path)
    assert imported.id == prof.id
    assert len(imported.apps) == len(prof.apps)
    assert len(imported.desktops) == len(prof.desktops)
