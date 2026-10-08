"""
Persistent configuration store with atomic updates, automated backups,
retention management, crash detection markers, and import/export capabilities.
"""

from __future__ import annotations
import os
import json
import time
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
from app.models.workspace import WorkspaceConfig, WorkspaceProfile
from app.models.history import OperationHistoryRecord
from app.configuration.validator import ConfigValidator, ConfigValidationError
from app.configuration.migration import ConfigMigration
from app.logging.logger import get_logger


def get_default_config_dir() -> Path:
    """Returns %APPDATA%/VirtualDesktopWorkspaceManager or local fallback."""
    app_data = os.environ.get("APPDATA")
    if app_data:
        cfg_dir = Path(app_data) / "VirtualDesktopWorkspaceManager"
    else:
        cfg_dir = Path.home() / ".virtual_desktop_manager"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


class ConfigStore:
    """Handles loading, saving, backing up, and importing/exporting configuration."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir if config_dir else get_default_config_dir()
        self.config_file = self.config_dir / "workspace.json"
        self.backup_file = self.config_dir / "workspace.backup.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.config_dir / "history.json"
        self.crash_marker_file = self.config_dir / "operation_in_progress.marker"
        self.logger = get_logger()

    # -------------------------------------------------------------
    # Crash Marker / Recovery Support
    # -------------------------------------------------------------

    def set_operation_marker(self, operation_name: str) -> None:
        """Sets a marker indicating an operation is actively in-flight."""
        try:
            marker_data = {
                "operation": operation_name,
                "timestamp": time.time(),
                "time_str": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.crash_marker_file.write_text(json.dumps(marker_data), encoding="utf-8")
        except Exception as ex:
            self.logger.warning(f"Failed to write crash marker: {ex}")

    def clear_operation_marker(self) -> None:
        """Clears the in-flight marker upon graceful completion."""
        try:
            if self.crash_marker_file.exists():
                self.crash_marker_file.unlink(missing_ok=True)
        except Exception as ex:
            self.logger.warning(f"Failed to clear crash marker: {ex}")

    def check_incomplete_operation(self) -> Optional[dict]:
        """Returns details if a previous workspace operation did not complete cleanly."""
        if self.crash_marker_file.exists():
            try:
                data = json.loads(self.crash_marker_file.read_text(encoding="utf-8"))
                return data
            except Exception:
                return {"operation": "unknown", "time_str": "unknown"}
        return None

    # -------------------------------------------------------------
    # Load / Save
    # -------------------------------------------------------------

    def load(self) -> WorkspaceConfig:
        """Loads configuration from disk, performing migrations and validation."""
        if not self.config_file.exists():
            self.logger.info("Configuration file not found. Initializing default configuration.")
            config = WorkspaceConfig(
                profiles=[WorkspaceConfig.create_default_profile()]
            )
            self.save(config, create_backup=False)
            return config

        try:
            raw_text = self.config_file.read_text(encoding="utf-8")
            raw_data = json.loads(raw_text)
            migrated_data = ConfigMigration.migrate(raw_data)
            config = WorkspaceConfig.from_dict(migrated_data)

            # Validate loaded config
            errors, warnings = ConfigValidator.validate_config(config)
            for w in warnings:
                self.logger.warning(f"Config warning: {w}")
            if errors:
                for e in errors:
                    self.logger.error(f"Config error: {e}")

            return config

        except Exception as ex:
            self.logger.error(f"Failed to load configuration from {self.config_file}: {ex}")
            # Try recovering from backup
            if self.backup_file.exists():
                self.logger.warning("Attempting recovery from workspace.backup.json...")
                try:
                    raw_text = self.backup_file.read_text(encoding="utf-8")
                    raw_data = json.loads(raw_text)
                    return WorkspaceConfig.from_dict(ConfigMigration.migrate(raw_data))
                except Exception as b_ex:
                    self.logger.error(f"Backup recovery also failed: {b_ex}")

            # Return fresh default if all else fails
            return WorkspaceConfig(profiles=[WorkspaceConfig.create_default_profile()])

    def save(self, config: WorkspaceConfig, create_backup: bool = True) -> None:
        """Atomically saves configuration to disk with optional backup."""
        # Validate before saving
        errors, warnings = ConfigValidator.validate_config(config)
        if errors:
            raise ConfigValidationError(f"Cannot save invalid configuration: {'; '.join(errors)}")

        config_data = config.to_dict()
        json_text = json.dumps(config_data, indent=2, ensure_ascii=False)

        # Create backup of current file before overwriting
        if create_backup and self.config_file.exists():
            self._create_backup()

        # Atomic write: write to temp file then rename
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(self.config_dir),
            prefix="workspace_",
            suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(json_text)
            shutil.move(tmp_path, str(self.config_file))
        except Exception as ex:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise IOError(f"Failed to save configuration: {ex}") from ex

    def _create_backup(self) -> None:
        """Creates workspace.backup.json and a timestamped backup with retention of 5."""
        try:
            shutil.copy2(str(self.config_file), str(self.backup_file))

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            ts_backup = self.backup_dir / f"workspace_{timestamp}.backup.json"
            shutil.copy2(str(self.config_file), str(ts_backup))

            # Maintain maximum of 5 timestamped backups
            backups = sorted(self.backup_dir.glob("workspace_*.backup.json"), key=os.path.getmtime)
            if len(backups) > 5:
                for old in backups[:-5]:
                    old.unlink(missing_ok=True)
        except Exception as ex:
            self.logger.warning(f"Could not create configuration backup: {ex}")

    # -------------------------------------------------------------
    # Import / Export
    # -------------------------------------------------------------

    def export_profile(self, profile: WorkspaceProfile, target_path: Path) -> None:
        """Exports a single profile as clean JSON."""
        data = profile.to_dict()
        text = json.dumps(data, indent=2, ensure_ascii=False)
        target_path.write_text(text, encoding="utf-8")

    def import_profile(self, source_path: Path) -> WorkspaceProfile:
        """Validates and imports a profile from a JSON file."""
        text = source_path.read_text(encoding="utf-8")
        raw = json.loads(text)
        profile = WorkspaceProfile.from_dict(raw)
        errors, warnings = ConfigValidator.validate_profile(profile)
        if errors:
            raise ConfigValidationError(f"Invalid profile in {source_path.name}: {'; '.join(errors)}")
        return profile

    def export_all(self, target_path: Path, config: WorkspaceConfig) -> None:
        """Exports full configuration to user-specified path."""
        data = config.to_dict()
        text = json.dumps(data, indent=2, ensure_ascii=False)
        target_path.write_text(text, encoding="utf-8")

    def import_all(self, source_path: Path) -> WorkspaceConfig:
        """Validates and imports full configuration."""
        text = source_path.read_text(encoding="utf-8")
        raw = json.loads(text)
        migrated = ConfigMigration.migrate(raw)
        config = WorkspaceConfig.from_dict(migrated)
        errors, warnings = ConfigValidator.validate_config(config)
        if errors:
            raise ConfigValidationError(f"Invalid workspace configuration: {'; '.join(errors)}")
        return config

    # -------------------------------------------------------------
    # Operation History Persistence (Section 29)
    # -------------------------------------------------------------

    def save_history_record(self, record: OperationHistoryRecord) -> None:
        """Atomically prepends an operation history record, retaining at most 100 entries."""
        try:
            records = self.get_history_records(limit=100)
            records.insert(0, record)
            # Retain maximum 100 entries
            records = records[:100]

            data = [r.to_dict() for r in records]
            json_text = json.dumps(data, indent=2, ensure_ascii=False)

            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=str(self.config_dir),
                prefix="history_",
                suffix=".tmp"
            )
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(json_text)
            shutil.move(tmp_path, str(self.history_file))
        except Exception as ex:
            self.logger.warning(f"Could not save operation history record: {ex}")

    def get_history_records(self, limit: int = 50) -> List[OperationHistoryRecord]:
        """Loads past operation history records up to the specified limit."""
        if not self.history_file.exists():
            return []
        try:
            raw_text = self.history_file.read_text(encoding="utf-8")
            raw_data = json.loads(raw_text)
            if not isinstance(raw_data, list):
                return []
            records = [OperationHistoryRecord.from_dict(item) for item in raw_data if isinstance(item, dict)]
            return records[:limit]
        except Exception as ex:
            self.logger.warning(f"Could not load operation history records: {ex}")
            return []

    def clear_history(self) -> None:
        """Clears all historical operation records."""
        try:
            if self.history_file.exists():
                self.history_file.unlink(missing_ok=True)
        except Exception as ex:
            self.logger.warning(f"Could not clear operation history: {ex}")
