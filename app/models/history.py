"""
Operation history model for tracking and auditing past workspace runs.
Conforms to Section 29 (Operation History UX).
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from app.models.report import ExecutionReport


@dataclass
class OperationHistoryRecord:
    """A persistent record of a completed, cancelled, or failed workspace run."""
    operation_id: str
    timestamp: float
    time_str: str
    profile_name: str
    operation_type: str  # "Launch", "Sync", "Dry Run"
    result: str          # "Success", "Warning", "Error", "Cancelled"
    duration_seconds: float
    desktops_target: int
    desktops_found: int
    apps_count: int
    warnings_count: int
    errors_count: int
    summary: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @classmethod
    def from_report(
        cls,
        report: ExecutionReport,
        profile_name: str,
        operation_id: Optional[str] = None
    ) -> OperationHistoryRecord:
        op_id = operation_id or f"OP-{time.strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:4]}"
        t_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(report.started_at))

        if report.cancelled:
            res = "Cancelled"
        elif report.errors:
            res = "Error"
        elif report.warnings:
            res = "Warning"
        else:
            res = "Success"

        return cls(
            operation_id=op_id,
            timestamp=report.started_at,
            time_str=t_str,
            profile_name=profile_name,
            operation_type=report.operation_type,
            result=res,
            duration_seconds=report.duration_seconds,
            desktops_target=report.total_desktops_target,
            desktops_found=report.total_desktops_found,
            apps_count=report.apps_configured,
            warnings_count=len(report.warnings),
            errors_count=len(report.errors),
            summary=report.summary_text(),
            warnings=list(report.warnings),
            errors=list(report.errors),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OperationHistoryRecord:
        return cls(
            operation_id=data.get("operation_id", ""),
            timestamp=data.get("timestamp", time.time()),
            time_str=data.get("time_str", ""),
            profile_name=data.get("profile_name", ""),
            operation_type=data.get("operation_type", "Unknown"),
            result=data.get("result", "Unknown"),
            duration_seconds=data.get("duration_seconds", 0.0),
            desktops_target=data.get("desktops_target", 0),
            desktops_found=data.get("desktops_found", 0),
            apps_count=data.get("apps_count", 0),
            warnings_count=data.get("warnings_count", 0),
            errors_count=data.get("errors_count", 0),
            summary=data.get("summary", ""),
            warnings=data.get("warnings", []),
            errors=data.get("errors", []),
        )
