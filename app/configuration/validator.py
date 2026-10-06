"""
Validation engine for workspace configurations and applications.
"""

from __future__ import annotations
import os
import re
from typing import List, Tuple
from app.models.workspace import WorkspaceConfig, WorkspaceProfile, AppConfig


class ConfigValidationError(Exception):
    """Exception raised when configuration is fatally invalid."""
    pass


class ConfigValidator:
    """Validates workspace configurations, reporting errors and warnings."""

    @staticmethod
    def validate_app(app: AppConfig) -> Tuple[List[str], List[str]]:
        """
        Validates a single application configuration.
        Returns (errors, warnings).
        """
        errors: List[str] = []
        warnings: List[str] = []

        if not app.id or not app.id.strip():
            errors.append("Application ID cannot be empty.")

        if not app.name or not app.name.strip():
            errors.append(f"Application '{app.id}' has an empty name.")

        if app.desktop < 1:
            errors.append(f"Application '{app.name or app.id}' target desktop must be >= 1.")

        if app.launch_delay_ms < 0 or app.launch_delay_ms > 60000:
            errors.append(f"Application '{app.name}' launch delay must be between 0 and 60,000 ms.")

        if app.window_timeout_ms < 1000 or app.window_timeout_ms > 120000:
            errors.append(f"Application '{app.name}' window timeout must be between 1,000 and 120,000 ms.")

        # Check executable path if configured
        if app.executable:
            expanded = app.expanded_executable
            if not os.path.exists(expanded):
                warnings.append(
                    f"Executable for '{app.name}' not found at '{expanded}'."
                )

        # Safety check: ensure arguments don't contain dangerous shell piping/chaining
        if app.arguments:
            dangerous_chars = ["|", "&", ";", ">", "<", "`", "$"]
            for ch in dangerous_chars:
                if ch in app.arguments:
                    warnings.append(
                        f"Arguments for '{app.name}' contain character '{ch}' which may be unsafe."
                    )
                    break

        return errors, warnings

    @classmethod
    def validate_profile(cls, profile: WorkspaceProfile) -> Tuple[List[str], List[str]]:
        """Validates a workspace profile."""
        errors: List[str] = []
        warnings: List[str] = []

        if not profile.name or not profile.name.strip():
            errors.append("Profile name cannot be empty.")

        app_ids = set()
        for app in profile.apps:
            if app.id in app_ids:
                errors.append(f"Duplicate application ID '{app.id}' found in profile '{profile.name}'.")
            app_ids.add(app.id)

            app_errs, app_warns = cls.validate_app(app)
            errors.extend(app_errs)
            warnings.extend(app_warns)

        desktop_nums = set()
        for d in profile.desktops:
            if d.number in desktop_nums:
                errors.append(f"Duplicate desktop number '{d.number}' in profile '{profile.name}'.")
            desktop_nums.add(d.number)

        # Check if any app points to a desktop not defined in desktops list
        for app in profile.apps:
            if profile.desktops and app.desktop not in desktop_nums:
                warnings.append(
                    f"Application '{app.name}' is assigned to Desktop {app.desktop}, which is not defined in desktops list."
                )

        return errors, warnings

    @classmethod
    def validate_config(cls, config: WorkspaceConfig) -> Tuple[List[str], List[str]]:
        """Validates entire workspace configuration."""
        errors: List[str] = []
        warnings: List[str] = []

        if config.schema_version < 1:
            errors.append(f"Invalid schema version: {config.schema_version}")

        if not config.profiles:
            errors.append("Configuration must contain at least one profile.")

        profile_ids = set()
        for p in config.profiles:
            if p.id in profile_ids:
                errors.append(f"Duplicate profile ID '{p.id}'.")
            profile_ids.add(p.id)

            p_errs, p_warns = cls.validate_profile(p)
            errors.extend(p_errs)
            warnings.extend(p_warns)

        # Check active profile exists
        if not any(p.id == config.general.active_profile_id for p in config.profiles):
            warnings.append(
                f"Active profile '{config.general.active_profile_id}' not found; will default to first profile."
            )

        return errors, warnings

    @classmethod
    def validate(cls, config: WorkspaceConfig) -> None:
        """Validates configuration and raises ConfigValidationError if fatal errors are found."""
        errors, _ = cls.validate_config(config)
        if errors:
            raise ConfigValidationError("; ".join(errors))
