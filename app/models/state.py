"""
Application and Operation lifecycle state machine definitions.
Conforms to Section 37 (State Model — Expanded) and Section 38 (Operation State Machine).
"""

from __future__ import annotations
from enum import Enum


class ApplicationState(str, Enum):
    """Explicit application states conforming to Section 37."""
    UNINITIALIZED = "UNINITIALIZED"
    SETUP_REQUIRED = "SETUP_REQUIRED"
    READY = "READY"
    CONFIGURATION_DIRTY = "CONFIGURATION_DIRTY"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    DRY_RUN = "DRY_RUN"
    PLANNING = "PLANNING"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"


class OperationPhase(str, Enum):
    """Operation lifecycle phases conforming to Section 38."""
    IDLE = "Idle"
    VALIDATE = "Validate"
    DISCOVER = "Discover"
    PLAN = "Plan"
    AWAIT_APPROVAL = "Await Approval"
    EXECUTE = "Execute"
    VERIFY = "Verify"
    REPORT = "Report"
    CANCELLED = "Cancelled"
    FAILED = "Failed"
