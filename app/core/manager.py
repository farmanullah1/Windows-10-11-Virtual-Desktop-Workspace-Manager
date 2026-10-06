"""
WorkspaceManager facade orchestrating configuration, providers, execution,
synchronization, dry-run previews, and real-time operations.
"""

from __future__ import annotations
import threading
from typing import Optional, Callable, List, Tuple
from app.models.workspace import WorkspaceConfig, WorkspaceProfile, AppConfig, DesktopConfig
from app.models.event import WorkspaceEvent
from app.models.report import ExecutionReport
from app.configuration.config_store import ConfigStore
from app.providers.base import (
    IVirtualDesktopProvider,
    IWindowProvider,
    IProcessProvider,
    IApplicationLauncher,
    DesktopInfo,
)
from app.providers.windows_vda_provider import WindowsVdaProvider
from app.services.process_service import ProcessService
from app.services.window_service import WindowService
from app.discovery.app_detector import AppDetector
from app.core.execution_plan import WorkspaceExecutionPlan
from app.core.synchronizer import WorkspaceSynchronizer
from app.core.dry_run import DryRunInspector, DryRunResult
from app.logging.logger import get_logger


class WorkspaceManager:
    """Central controller for Virtual Desktop Workspace operations."""

    def __init__(
        self,
        config_store: Optional[ConfigStore] = None,
        desktop_provider: Optional[IVirtualDesktopProvider] = None,
        window_provider: Optional[IWindowProvider] = None,
        process_provider: Optional[IProcessProvider] = None,
        launcher: Optional[IApplicationLauncher] = None
    ):
        self.logger = get_logger()
        self.config_store = config_store or ConfigStore()
        self.config: WorkspaceConfig = self.config_store.load()

        # Providers (auto-select Windows providers if none injected)
        self.desktop_provider = desktop_provider or WindowsVdaProvider()
        self.window_provider = window_provider or WindowService()
        proc_service = ProcessService()
        self.process_provider = process_provider or proc_service
        self.launcher = launcher or proc_service

        self.app_detector = AppDetector(self.process_provider)
        self.synchronizer = WorkspaceSynchronizer(
            desktop_provider=self.desktop_provider,
            window_provider=self.window_provider,
            process_provider=self.process_provider,
            launcher=self.launcher,
            app_detector=self.app_detector
        )
        self.dry_runner = DryRunInspector(
            desktop_provider=self.desktop_provider,
            window_provider=self.window_provider,
            process_provider=self.process_provider,
            app_detector=self.app_detector
        )

        self._active_plan: Optional[WorkspaceExecutionPlan] = None
        self._op_lock = threading.Lock()

    # -------------------------------------------------------------
    # State Queries
    # -------------------------------------------------------------

    def get_current_desktop_number(self) -> int:
        return self.desktop_provider.get_current_desktop_number()

    def get_desktop_count(self) -> int:
        return self.desktop_provider.get_desktop_count()

    def get_desktops(self) -> List[DesktopInfo]:
        return self.desktop_provider.get_desktops()

    def switch_to_desktop(self, desktop_number: int) -> bool:
        return self.desktop_provider.switch_to_desktop(desktop_number)

    def is_operation_running(self) -> bool:
        return self._active_plan is not None

    # -------------------------------------------------------------
    # Execution & Sync
    # -------------------------------------------------------------

    def launch_workspace(
        self,
        profile_id: Optional[str] = None,
        event_callback: Optional[Callable[[WorkspaceEvent], None]] = None
    ) -> ExecutionReport:
        """Launches the workspace according to active profile configuration."""
        if not self.config.safety.automation_enabled:
            raise RuntimeError("Automation is currently paused/disabled in safety settings.")

        with self._op_lock:
            profile = self._resolve_profile(profile_id)
            self.config_store.set_operation_marker("Launch")

            plan = WorkspaceExecutionPlan(
                profile=profile,
                desktop_provider=self.desktop_provider,
                window_provider=self.window_provider,
                process_provider=self.process_provider,
                launcher=self.launcher,
                app_detector=self.app_detector,
                event_callback=event_callback
            )
            self._active_plan = plan

        try:
            report = plan.execute(is_sync_mode=False)
            return report
        finally:
            with self._op_lock:
                self._active_plan = None
                self.config_store.clear_operation_marker()

    def sync_workspace(
        self,
        profile_id: Optional[str] = None,
        event_callback: Optional[Callable[[WorkspaceEvent], None]] = None
    ) -> ExecutionReport:
        """Reconciles running window desktop locations without launching missing apps."""
        if not self.config.safety.automation_enabled:
            raise RuntimeError("Automation is currently paused/disabled in safety settings.")

        with self._op_lock:
            profile = self._resolve_profile(profile_id)
            self.config_store.set_operation_marker("Sync")

            plan = WorkspaceExecutionPlan(
                profile=profile,
                desktop_provider=self.desktop_provider,
                window_provider=self.window_provider,
                process_provider=self.process_provider,
                launcher=self.launcher,
                app_detector=self.app_detector,
                event_callback=event_callback
            )
            self._active_plan = plan

        try:
            report = plan.execute(is_sync_mode=True)
            return report
        finally:
            with self._op_lock:
                self._active_plan = None
                self.config_store.clear_operation_marker()

    def stop_current_operation(self) -> None:
        """Emergency Stop: cancels in-flight workspace operation without killing processes."""
        with self._op_lock:
            if self._active_plan:
                self._active_plan.cancel()

    def dry_run(self, profile_id: Optional[str] = None) -> DryRunResult:
        """Generates dry-run preview without executing any modifications."""
        profile = self._resolve_profile(profile_id)
        return self.dry_runner.inspect(profile)

    # -------------------------------------------------------------
    # Immediate Actions (Section 14 & 52)
    # -------------------------------------------------------------

    def move_running_window_now(self, app_id: str, target_desktop: int) -> bool:
        """Immediately moves an already running application window to the target desktop."""
        profile = self.config.get_active_profile()
        app = next((a for a in profile.apps if a.id == app_id), None)
        if not app:
            return False

        # Find running process
        resolved_exe, _ = self.app_detector.detect_executable(app)
        candidate_names = list(app.process_names)
        if resolved_exe:
            candidate_names.append(os.path.basename(resolved_exe))
        running_procs = self.process_provider.get_running_processes_matching(candidate_names)
        if not running_procs:
            return False

        # Find windows
        windows = []
        for p in running_procs:
            windows.extend(self.window_provider.find_windows_for_process(p.pid))

        if not windows:
            return False

        # Move windows
        success = True
        for w in windows:
            moved = self.desktop_provider.move_window_to_desktop(w.hwnd, target_desktop)
            if not moved:
                success = False
        return success

    # -------------------------------------------------------------
    # Configuration Management
    # -------------------------------------------------------------

    def add_app_to_profile(self, app_config: AppConfig, profile_id: Optional[str] = None) -> None:
        """Adds an application to the workspace profile and saves persistently."""
        profile = self._resolve_profile(profile_id)
        # Ensure unique ID
        existing_ids = {a.id for a in profile.apps}
        if app_config.id in existing_ids:
            import uuid
            app_config.id = f"{app_config.id}_{str(uuid.uuid4())[:4]}"

        profile.apps.append(app_config)
        self.save_config()
        self.logger.info(f"Added application '{app_config.name}' to Desktop {app_config.desktop}")

    def update_app_in_profile(self, app_config: AppConfig, profile_id: Optional[str] = None) -> None:
        """Updates an existing application configuration."""
        profile = self._resolve_profile(profile_id)
        for i, a in enumerate(profile.apps):
            if a.id == app_config.id:
                profile.apps[i] = app_config
                self.save_config()
                self.logger.info(f"Updated application '{app_config.name}'")
                return
        # If not found, append
        profile.apps.append(app_config)
        self.save_config()

    def remove_app_from_profile(self, app_id: str, profile_id: Optional[str] = None) -> bool:
        """Removes application configuration from workspace (does not uninstall)."""
        profile = self._resolve_profile(profile_id)
        initial_len = len(profile.apps)
        profile.apps = [a for a in profile.apps if a.id != app_id]
        if len(profile.apps) < initial_len:
            self.save_config()
            self.logger.info(f"Removed application ID '{app_id}' from workspace.")
            return True
        return False

    def reassign_app(self, app_id: str, new_desktop_number: int, profile_id: Optional[str] = None) -> bool:
        """Reassigns an application from one desktop to another."""
        profile = self._resolve_profile(profile_id)
        for a in profile.apps:
            if a.id == app_id:
                old_dt = a.desktop
                a.desktop = new_desktop_number
                self.save_config()
                self.logger.info(f"Reassigned '{a.name}' from Desktop {old_dt} to Desktop {new_desktop_number}")
                return True
        return False

    def add_desktop(self, name: str, profile_id: Optional[str] = None) -> DesktopConfig:
        """Adds a new configured desktop card to the active profile."""
        profile = self._resolve_profile(profile_id)
        next_num = max([d.number for d in profile.desktops], default=0) + 1
        new_dt = DesktopConfig(number=next_num, name=name or f"Desktop {next_num}")
        profile.desktops.append(new_dt)
        self.save_config()
        self.logger.info(f"Configured new Desktop {next_num}: '{new_dt.name}'")
        return new_dt

    def rename_desktop(self, desktop_number: int, new_name: str, profile_id: Optional[str] = None) -> bool:
        """Renames a configured desktop card."""
        profile = self._resolve_profile(profile_id)
        for d in profile.desktops:
            if d.number == desktop_number:
                d.name = new_name
                self.save_config()
                return True
        return False

    def save_config(self) -> None:
        """Persists workspace configuration to disk atomically with backup."""
        self.config_store.save(self.config)

    def _resolve_profile(self, profile_id: Optional[str] = None) -> WorkspaceProfile:
        if profile_id:
            for p in self.config.profiles:
                if p.id == profile_id:
                    return p
        return self.config.get_active_profile()
