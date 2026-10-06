"""
Traceable lifecycle events for workspace operations.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional


class EventType(str, Enum):
    WORKSPACE_LAUNCH_STARTED = "WorkspaceLaunchStarted"
    DESKTOP_DISCOVERY_COMPLETED = "DesktopDiscoveryCompleted"
    DESKTOP_CREATED = "DesktopCreated"
    APPLICATION_DISCOVERY_STARTED = "ApplicationDiscoveryStarted"
    APPLICATION_LAUNCH_STARTED = "ApplicationLaunchStarted"
    APPLICATION_ALREADY_RUNNING = "ApplicationAlreadyRunning"
    WINDOW_DETECTED = "WindowDetected"
    WINDOW_MOVE_STARTED = "WindowMoveStarted"
    WINDOW_MOVE_COMPLETED = "WindowMoveCompleted"
    VERIFICATION_COMPLETED = "VerificationCompleted"
    WORKSPACE_LAUNCH_COMPLETED = "WorkspaceLaunchCompleted"
    WORKSPACE_SYNC_STARTED = "WorkspaceSyncStarted"
    WORKSPACE_SYNC_COMPLETED = "WorkspaceSyncCompleted"
    WORKSPACE_OPERATION_CANCELLED = "WorkspaceOperationCancelled"
    ERROR_OCCURRED = "ErrorOccurred"
    WARNING_ISSUED = "WarningIssued"


@dataclass
class WorkspaceEvent:
    """An event recording an occurrence during workspace execution."""
    event_type: EventType
    timestamp: float = field(default_factory=time.time)
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    app_id: Optional[str] = None
    desktop_number: Optional[int] = None

    def formatted_time(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
