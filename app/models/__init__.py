"""
Models package exports.
"""

from app.models.workspace import (
    WindowPolicy,
    LaunchMode,
    AppConfig,
    DesktopConfig,
    WorkspaceProfile,
    GeneralSettings,
    ExecutionSettings,
    LoggingSettings,
    SafetySettings,
    WorkspaceConfig,
)
from app.models.event import EventType, WorkspaceEvent
from app.models.report import AppExecutionStatus, ExecutionReport
from app.models.error_codes import ErrorCategory, ErrorDefinition, ERROR_CATALOG, get_error

__all__ = [
    "WindowPolicy",
    "LaunchMode",
    "AppConfig",
    "DesktopConfig",
    "WorkspaceProfile",
    "GeneralSettings",
    "ExecutionSettings",
    "LoggingSettings",
    "SafetySettings",
    "WorkspaceConfig",
    "EventType",
    "WorkspaceEvent",
    "AppExecutionStatus",
    "ExecutionReport",
    "ErrorCategory",
    "ErrorDefinition",
    "ERROR_CATALOG",
    "get_error",
]
