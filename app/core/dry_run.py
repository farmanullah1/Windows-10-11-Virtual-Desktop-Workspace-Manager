"""
Dry Run inspection engine. Analyzes the workspace state without making any changes.
Guarantees zero desktop creations, zero process spawns, zero window moves.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from app.models.workspace import WorkspaceProfile, AppConfig
from app.providers.base import IVirtualDesktopProvider, IProcessProvider, IWindowProvider
from app.discovery.app_detector import AppDetector


@dataclass
class DryRunAppStatus:
    app_id: str
    app_name: str
    target_desktop: int
    executable_path: Optional[str]
    is_installed: bool
    is_running: bool
    visible_windows_count: int
    action_preview: str


@dataclass
class DryRunResult:
    existing_desktops: int
    required_desktops: int
    desktops_to_create: List[int]
    apps_by_desktop: Dict[int, List[DryRunAppStatus]]
    warnings: List[str] = field(default_factory=list)

    def format_preview(self) -> str:
        """Produces formatted text matching Section 36 specifications."""
        lines = [
            "=" * 60,
            "WORKSPACE DRY-RUN PREVIEW (NO CHANGES WILL BE MADE)",
            "=" * 60,
            f"Existing Virtual Desktops: {self.existing_desktops}",
            f"Required Virtual Desktops: {self.required_desktops}"
        ]

        if self.desktops_to_create:
            created_str = ", ".join(f"Desktop {n}" for n in self.desktops_to_create)
            lines.append(f"Would create: {created_str}")
        else:
            lines.append("Would create: None (sufficient desktops exist)")

        lines.append("")

        all_desktops = sorted(self.apps_by_desktop.keys())
        for d_num in all_desktops:
            lines.append(f"Desktop {d_num}:")
            apps = self.apps_by_desktop[d_num]
            if not apps:
                lines.append("  (No applications configured for this desktop)")
            for a in apps:
                icon = "[RUNNING]" if a.is_running else ("[MISSING]" if not a.is_installed else "[STOPPED]")
                lines.append(f"  {icon} {a.app_name}: {a.action_preview}")

        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        lines.append("=" * 60)
        return "\n".join(lines)


class DryRunInspector:
    """Calculates dry-run previews safely."""

    def __init__(
        self,
        desktop_provider: IVirtualDesktopProvider,
        process_provider: IProcessProvider,
        window_provider: IWindowProvider,
        app_detector: AppDetector
    ):
        self.desktop_provider = desktop_provider
        self.process_provider = process_provider
        self.window_provider = window_provider
        self.app_detector = app_detector

    def inspect(self, profile: WorkspaceProfile) -> DryRunResult:
        """Inspects current state and determines what actions would occur."""
        existing_count = self.desktop_provider.get_desktop_count()
        required_count = profile.get_max_desktop_number()

        desktops_to_create: List[int] = []
        if existing_count < required_count:
            desktops_to_create = list(range(existing_count + 1, required_count + 1))

        apps_by_desktop: Dict[int, List[DryRunAppStatus]] = {
            d.number: [] for d in profile.desktops
        }
        for i in range(1, required_count + 1):
            if i not in apps_by_desktop:
                apps_by_desktop[i] = []

        warnings: List[str] = []

        for app in profile.apps:
            if not app.enabled:
                continue

            resolved_path, _ = self.app_detector.detect_executable(app)
            is_installed = resolved_path is not None and os.path.exists(resolved_path)

            # Check running
            candidate_names = list(app.process_names)
            if resolved_path:
                candidate_names.append(os.path.basename(resolved_path))
            running_procs = self.process_provider.get_running_processes_matching(candidate_names)
            is_running = len(running_procs) > 0

            # Count visible windows
            win_count = 0
            if is_running:
                for p in running_procs:
                    win_count += len(self.window_provider.find_windows_for_process(p.pid))

            # Action preview
            if is_running:
                action = f"Running ({win_count} window(s)) -> Would move to Desktop {app.desktop}"
            elif is_installed:
                action = f"Not running -> Would launch from '{resolved_path}'"
            else:
                action = "Not found / Not installed -> Would show warning and skip"
                warnings.append(f"Executable for '{app.name}' not found.")

            status = DryRunAppStatus(
                app_id=app.id,
                app_name=app.name,
                target_desktop=app.desktop,
                executable_path=resolved_path,
                is_installed=is_installed,
                is_running=is_running,
                visible_windows_count=win_count,
                action_preview=action
            )

            if app.desktop in apps_by_desktop:
                apps_by_desktop[app.desktop].append(status)
            else:
                apps_by_desktop[app.desktop] = [status]

        return DryRunResult(
            existing_desktops=existing_count,
            required_desktops=required_count,
            desktops_to_create=desktops_to_create,
            apps_by_desktop=apps_by_desktop,
            warnings=warnings
        )
