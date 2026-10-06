"""
Workspace synchronization service. Reconciles actual running window positions
with desired desktop configurations without unnecessary launches.
"""

from __future__ import annotations
from typing import Optional, Callable
from app.models.workspace import WorkspaceProfile
from app.models.event import WorkspaceEvent
from app.models.report import ExecutionReport
from app.providers.base import (
    IVirtualDesktopProvider,
    IWindowProvider,
    IProcessProvider,
    IApplicationLauncher,
)
from app.discovery.app_detector import AppDetector
from app.core.execution_plan import WorkspaceExecutionPlan


class WorkspaceSynchronizer:
    """Reconciles the state of existing windows to match the workspace definition."""

    def __init__(
        self,
        desktop_provider: IVirtualDesktopProvider,
        window_provider: IWindowProvider,
        process_provider: IProcessProvider,
        launcher: IApplicationLauncher,
        app_detector: AppDetector
    ):
        self.desktop_provider = desktop_provider
        self.window_provider = window_provider
        self.process_provider = process_provider
        self.launcher = launcher
        self.app_detector = app_detector

    def synchronize(
        self,
        profile: WorkspaceProfile,
        event_callback: Optional[Callable[[WorkspaceEvent], None]] = None
    ) -> ExecutionReport:
        """Runs the workspace plan in sync mode (is_sync_mode=True)."""
        plan = WorkspaceExecutionPlan(
            profile=profile,
            desktop_provider=self.desktop_provider,
            window_provider=self.window_provider,
            process_provider=self.process_provider,
            launcher=self.launcher,
            app_detector=self.app_detector,
            event_callback=event_callback
        )
        return plan.execute(is_sync_mode=True)
