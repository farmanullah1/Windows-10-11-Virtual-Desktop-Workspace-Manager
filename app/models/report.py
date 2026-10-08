"""
Execution reports and summary models for workspace runs.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AppExecutionStatus:
    """Status record for a single application during workspace operation."""
    app_id: str
    app_name: str
    target_desktop: int
    was_running: bool = False
    was_launched: bool = False
    window_found: bool = False
    window_moved: bool = False
    window_snapped: bool = False
    verified: bool = False
    error: Optional[str] = None
    warning: Optional[str] = None
    duration_ms: int = 0


@dataclass
class ExecutionReport:
    """Comprehensive operation report matching Section 102 specifications."""
    operation_type: str  # "Launch" or "Sync" or "DryRun"
    started_at: float = field(default_factory=time.time)
    ended_at: float = 0.0
    duration_seconds: float = 0.0
    total_desktops_target: int = 0
    total_desktops_found: int = 0
    desktops_created: int = 0
    apps_configured: int = 0
    apps_detected: int = 0
    apps_launched_or_reused: int = 0
    apps_assigned: int = 0
    apps_skipped: int = 0
    apps_failed: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    app_statuses: Dict[str, AppExecutionStatus] = field(default_factory=dict)
    cancelled: bool = False

    @property
    def success(self) -> bool:
        """True if the operation completed without cancellation or fatal errors."""
        return not self.cancelled and len(self.errors) == 0

    def finish(self) -> None:
        self.ended_at = time.time()
        self.duration_seconds = round(self.ended_at - self.started_at, 2)

    def summary_text(self) -> str:
        status_line = "CANCELLED" if self.cancelled else ("WITH WARNINGS/ERRORS" if (self.errors or self.warnings) else "COMPLETE")
        lines = [
            f"Workspace Operation {status_line}",
            "",
            "Virtual Desktops:",
            f"  {self.total_desktops_found} available / {self.total_desktops_target} target (Created: {self.desktops_created})",
            "",
            "Applications:",
            f"  {self.apps_configured} configured",
            f"  {self.apps_detected} detected",
            f"  {self.apps_launched_or_reused} launched/reused",
            f"  {self.apps_assigned} assigned",
            f"  {self.apps_skipped} skipped",
            f"  {self.apps_failed} failed",
            "",
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
            f"Duration: {self.duration_seconds:.2f} seconds"
        ]
        if self.warnings:
            lines.append("\nWarnings detail:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        if self.errors:
            lines.append("\nErrors detail:")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)
