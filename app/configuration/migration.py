"""
Configuration migration engine for backward and forward compatibility.
"""

from __future__ import annotations
from typing import Dict, Any

CURRENT_SCHEMA_VERSION = 1


class ConfigMigration:
    """Migrates older configuration schemas to the current schema version."""

    @classmethod
    def migrate(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        version = raw_data.get("schema_version") or raw_data.get("schemaVersion") or 0

        # Migration from legacy v0 or unversioned format
        if version < 1:
            raw_data = cls._migrate_v0_to_v1(raw_data)

        raw_data["schema_version"] = CURRENT_SCHEMA_VERSION
        return raw_data

    @staticmethod
    def _migrate_v0_to_v1(data: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrades unversioned or legacy config to version 1."""
        upgraded = dict(data)
        upgraded["schema_version"] = 1

        # If data was a single flat list of apps
        if "apps" in upgraded and "profiles" not in upgraded:
            from app.models.workspace import AppConfig
            raw_apps = upgraded.pop("apps")
            desktops = upgraded.pop("desktops", [])
            converted_apps = [AppConfig.from_dict(a).to_dict() for a in raw_apps]

            upgraded["profiles"] = [{
                "id": "default",
                "name": "Default Workspace",
                "description": "Migrated workspace",
                "desktops": desktops,
                "apps": converted_apps
            }]

        if "general" not in upgraded:
            upgraded["general"] = {}
        if "execution" not in upgraded:
            upgraded["execution"] = {}
        if "logging" not in upgraded:
            upgraded["logging"] = {}
        if "safety" not in upgraded:
            upgraded["safety"] = {}

        return upgraded
