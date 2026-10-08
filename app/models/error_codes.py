"""
Standard internal error categories and codes.
Conforms to Section 59 (Error Codes and Supportability).
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ErrorCategory(str, Enum):
    VDM = "VDM"        # Virtual Desktop Management
    WIN = "WIN"        # Window Operations
    APP = "APP"        # Application Launch & Discovery
    CFG = "CFG"        # Configuration & Storage
    SETUP = "SETUP"    # Bootstrap, Installation & Shortcuts
    SEC = "SEC"        # Security & Permission Boundaries


@dataclass(frozen=True)
class ErrorDefinition:
    code: str
    category: ErrorCategory
    title: str
    user_message: str
    remediation_hint: str

    def format_log(self, detail: Optional[str] = None) -> str:
        base = f"[{self.code}] {self.title}"
        if detail:
            return f"{base}: {detail}"
        return base

    def format_user(self, detail: Optional[str] = None) -> str:
        msg = f"[{self.code}] {self.user_message}"
        if detail:
            msg += f"\nDetails: {detail}"
        if self.remediation_hint:
            msg += f"\nRecommendation: {self.remediation_hint}"
        return msg


# Error Code Registry
ERROR_CATALOG = {
    "VDM-001": ErrorDefinition(
        code="VDM-001",
        category=ErrorCategory.VDM,
        title="Virtual Desktop Provider Unavailable",
        user_message="Virtual Desktop COM provider is unavailable or unsupported on this Windows build.",
        remediation_hint="Verify pyvda COM integration or check Windows Virtual Desktop API compatibility."
    ),
    "VDM-002": ErrorDefinition(
        code="VDM-002",
        category=ErrorCategory.VDM,
        title="Desktop Identity Mismatch",
        user_message="Windows reported a different desktop identity than configured.",
        remediation_hint="Refresh desktop list or review Desktop Mapping in the manager."
    ),
    "VDM-003": ErrorDefinition(
        code="VDM-003",
        category=ErrorCategory.VDM,
        title="Desktop Creation Failed",
        user_message="Failed to create requested Virtual Desktop.",
        remediation_hint="Check if Windows Virtual Desktop creation limit has been reached."
    ),
    "VDM-004": ErrorDefinition(
        code="VDM-004",
        category=ErrorCategory.VDM,
        title="Desktop Switch Failed",
        user_message="Failed to switch to the target Virtual Desktop.",
        remediation_hint="Ensure the requested desktop index currently exists."
    ),
    "WIN-001": ErrorDefinition(
        code="WIN-001",
        category=ErrorCategory.WIN,
        title="Window No Longer Exists",
        user_message="The target window was closed or destroyed before placement.",
        remediation_hint="Verify the application process is running and its main window remains open."
    ),
    "WIN-002": ErrorDefinition(
        code="WIN-002",
        category=ErrorCategory.WIN,
        title="Window Move Failed",
        user_message="Windows did not confirm the requested Virtual Desktop window assignment.",
        remediation_hint="Run Health Check diagnostics or test window matching."
    ),
    "WIN-003": ErrorDefinition(
        code="WIN-003",
        category=ErrorCategory.WIN,
        title="Ambiguous Window Match",
        user_message="Multiple windows matched the application rule without unique selection.",
        remediation_hint="Refine the application window matching policy or title regex in Settings."
    ),
    "APP-001": ErrorDefinition(
        code="APP-001",
        category=ErrorCategory.APP,
        title="Executable Not Found",
        user_message="The configured executable path could not be located on disk.",
        remediation_hint="Edit the application configuration to specify a valid path or use auto-discovery."
    ),
    "APP-002": ErrorDefinition(
        code="APP-002",
        category=ErrorCategory.APP,
        title="Window Wait Timeout",
        user_message="Application was launched, but its window was not detected within the timeout window.",
        remediation_hint="Increase the window timeout setting or verify the app starts as a desktop window."
    ),
    "APP-003": ErrorDefinition(
        code="APP-003",
        category=ErrorCategory.APP,
        title="Process Failed to Start",
        user_message="Could not start the configured application process.",
        remediation_hint="Check execution permissions and working directory settings."
    ),
    "CFG-001": ErrorDefinition(
        code="CFG-001",
        category=ErrorCategory.CFG,
        title="Invalid Configuration",
        user_message="The configuration file is malformed or failed validation.",
        remediation_hint="Restore a previous configuration backup or reset to defaults."
    ),
    "CFG-002": ErrorDefinition(
        code="CFG-002",
        category=ErrorCategory.CFG,
        title="Configuration Schema Migration Failed",
        user_message="Unable to migrate legacy configuration file to current schema version.",
        remediation_hint="Inspect the backup file created in the config directory."
    ),
    "CFG-003": ErrorDefinition(
        code="CFG-003",
        category=ErrorCategory.CFG,
        title="Backup / Restore Failed",
        user_message="Could not create or restore configuration snapshot.",
        remediation_hint="Ensure the application directory has appropriate write permissions."
    ),
    "SETUP-001": ErrorDefinition(
        code="SETUP-001",
        category=ErrorCategory.SETUP,
        title="Setup Dependency Failure",
        user_message="Setup could not resolve or verify required Python dependencies.",
        remediation_hint="Run setup in an activated virtual environment with internet access for installation."
    ),
    "SETUP-002": ErrorDefinition(
        code="SETUP-002",
        category=ErrorCategory.SETUP,
        title="Shortcut Creation Failure",
        user_message="Desktop or Start Menu shortcut could not be created.",
        remediation_hint="Check Desktop folder write permissions or pywin32 COM registration."
    ),
    "SEC-001": ErrorDefinition(
        code="SEC-001",
        category=ErrorCategory.SEC,
        title="Security Boundary Violation",
        user_message="Operation was blocked because it attempted unauthorized system modification.",
        remediation_hint="The manager strictly prohibits process termination and arbitrary shell command execution."
    ),
}


def get_error(code: str) -> ErrorDefinition:
    """Retrieves an error definition by code, or returns a generic error."""
    if code in ERROR_CATALOG:
        return ERROR_CATALOG[code]
    return ErrorDefinition(
        code=code,
        category=ErrorCategory.CFG,
        title="Unknown Error",
        user_message=f"An uncataloged error occurred ({code}).",
        remediation_hint="Check application logs for details."
    )
