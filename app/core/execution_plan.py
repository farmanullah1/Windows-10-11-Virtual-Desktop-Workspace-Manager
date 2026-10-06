"""
Phased execution engine implementing transaction-like workspace launch
with cancellation support, failure isolation, and comprehensive reporting.
"""

from __future__ import annotations
import os
import time
from threading import Event
from typing import Optional, List, Dict, Callable
from app.models.workspace import WorkspaceProfile, AppConfig, LaunchMode, WindowPolicy
from app.models.event import EventType, WorkspaceEvent
from app.models.report import ExecutionReport, AppExecutionStatus
from app.providers.base import (
    IVirtualDesktopProvider,
    IWindowProvider,
    IProcessProvider,
    IApplicationLauncher,
    WindowInfo,
    ProcessInfo,
)
from app.discovery.app_detector import AppDetector
from app.logging.logger import get_logger


class WorkspaceExecutionPlan:
    """
    Executes a workspace sequence through 7 defined phases:
    Phase 1: Detect desktops
    Phase 2: Prepare desktops (create required, never delete existing)
    Phase 3: Launch / find processes
    Phase 4: Wait for application top-level windows
    Phase 5: Move windows to assigned desktops
    Phase 6: Verify desktop assignment
    Phase 7: Generate ExecutionReport
    """

    def __init__(
        self,
        profile: WorkspaceProfile,
        desktop_provider: IVirtualDesktopProvider,
        window_provider: IWindowProvider,
        process_provider: IProcessProvider,
        launcher: IApplicationLauncher,
        app_detector: AppDetector,
        event_callback: Optional[Callable[[WorkspaceEvent], None]] = None
    ):
        self.profile = profile
        self.desktop_provider = desktop_provider
        self.window_provider = window_provider
        self.process_provider = process_provider
        self.launcher = launcher
        self.app_detector = app_detector
        self.event_callback = event_callback
        self.logger = get_logger()
        self.cancel_event = Event()

    def cancel(self) -> None:
        """Signals emergency stop / cancellation."""
        self.cancel_event.set()
        self._emit(EventType.WORKSPACE_OPERATION_CANCELLED, "Workspace operation cancelled by user.")
        self.logger.warning("Emergency stop requested. Cancelling pending workspace actions.")

    def _emit(self, event_type: EventType, message: str, details: Optional[Dict] = None, app_id: Optional[str] = None, desktop: Optional[int] = None) -> None:
        event = WorkspaceEvent(
            event_type=event_type,
            message=message,
            details=details or {},
            app_id=app_id,
            desktop_number=desktop
        )
        if self.event_callback:
            try:
                self.event_callback(event)
            except Exception:
                pass

    def execute(self, is_sync_mode: bool = False) -> ExecutionReport:
        """Executes the complete phased plan."""
        op_name = "Sync" if is_sync_mode else "Launch"
        report = ExecutionReport(operation_type=op_name)
        self.logger.info(f"--- Starting Workspace {op_name}: '{self.profile.name}' ---")
        self._emit(
            EventType.WORKSPACE_SYNC_STARTED if is_sync_mode else EventType.WORKSPACE_LAUNCH_STARTED,
            f"Starting Workspace {op_name}"
        )

        try:
            # -------------------------------------------------------------
            # Phase 1 & 2: Desktop Discovery & Preparation
            # -------------------------------------------------------------
            required_desktop_count = self.profile.get_max_desktop_number()
            report.total_desktops_target = required_desktop_count

            current_count = self.desktop_provider.get_desktop_count()
            report.total_desktops_found = current_count
            self.logger.info(f"Phase 1: Detected {current_count} available Virtual Desktops (Required: {required_desktop_count}).")
            self._emit(EventType.DESKTOP_DISCOVERY_COMPLETED, f"Detected {current_count} desktops")

            if current_count < required_desktop_count:
                needed = required_desktop_count - current_count
                self.logger.info(f"Phase 2: Need to create {needed} additional desktop(s).")
                for _ in range(needed):
                    if self.cancel_event.is_set():
                        report.cancelled = True
                        break
                    new_dt = self.desktop_provider.create_desktop()
                    report.desktops_created += 1
                    report.total_desktops_found = self.desktop_provider.get_desktop_count()
                    self._emit(EventType.DESKTOP_CREATED, f"Created Desktop {new_dt.number}", desktop=new_dt.number)
            else:
                self.logger.info(f"Phase 2: Sufficient desktops available ({current_count} >= {required_desktop_count}). Preserving existing desktops.")

            if self.cancel_event.is_set():
                report.cancelled = True
                report.finish()
                return report

            # -------------------------------------------------------------
            # Phase 3 to 6: Process and Window Execution for each App
            # -------------------------------------------------------------
            enabled_apps = [a for a in self.profile.apps if a.enabled]
            report.apps_configured = len(enabled_apps)

            for app in enabled_apps:
                if self.cancel_event.is_set():
                    report.cancelled = True
                    break

                status = AppExecutionStatus(
                    app_id=app.id,
                    app_name=app.name,
                    target_desktop=app.desktop
                )
                start_app_time = time.time()

                try:
                    self._process_single_app(app, status, is_sync_mode, report)
                except Exception as ex:
                    err_msg = f"Error processing application '{app.name}': {ex}"
                    self.logger.error(err_msg)
                    status.error = str(ex)
                    report.errors.append(err_msg)
                    report.apps_failed += 1
                finally:
                    status.duration_ms = int((time.time() - start_app_time) * 1000)
                    report.app_statuses[app.id] = status

            # Check final report counts
            for st in report.app_statuses.values():
                if st.verified or st.window_moved:
                    report.apps_assigned += 1
                elif st.error:
                    pass  # already counted in apps_failed
                else:
                    report.apps_skipped += 1

        except Exception as global_ex:
            err = f"Fatal workspace execution failure: {global_ex}"
            self.logger.error(err)
            report.errors.append(err)

        finally:
            report.finish()
            finish_event = EventType.WORKSPACE_SYNC_COMPLETED if is_sync_mode else EventType.WORKSPACE_LAUNCH_COMPLETED
            self._emit(finish_event, f"Workspace {op_name} finished")
            self.logger.info(f"--- Workspace {op_name} Report ---\n{report.summary_text()}")

        return report

    def _process_single_app(
        self,
        app: AppConfig,
        status: AppExecutionStatus,
        is_sync_mode: bool,
        report: ExecutionReport
    ) -> None:
        """Executes the lifecycle for one application with full error isolation."""
        self.logger.info(f"Processing '{app.name}' (Target Desktop: {app.desktop})")
        self._emit(EventType.APPLICATION_DISCOVERY_STARTED, f"Discovering {app.name}", app_id=app.id)

        # 1. Resolve executable
        resolved_exe, source = self.app_detector.detect_executable(app)
        if resolved_exe:
            report.apps_detected += 1
            self.logger.info(f"'{app.name}' resolved at: {resolved_exe} (source: {source})")
        else:
            warn_msg = f"'{app.name}' executable could not be resolved from configured paths or discovery."
            self.logger.warning(warn_msg)
            report.warnings.append(warn_msg)
            status.warning = warn_msg

        # 2. Check if already running
        candidate_names = list(app.process_names)
        if resolved_exe:
            candidate_names.append(os.path.basename(resolved_exe))
        if app.executable:
            candidate_names.append(os.path.basename(app.executable))

        running_procs = self.process_provider.get_running_processes_matching(candidate_names)
        if running_procs:
            status.was_running = True
            report.apps_launched_or_reused += 1
            self.logger.info(f"'{app.name}' is already running (PID: {running_procs[0].pid}). Reusing existing instance.")
            self._emit(EventType.APPLICATION_ALREADY_RUNNING, f"{app.name} already running", app_id=app.id)
        else:
            # Not running
            if is_sync_mode and app.launch_mode != LaunchMode.ALWAYS_LAUNCH.value:
                # In Sync mode, don't launch missing apps unless requested
                self.logger.info(f"Sync Mode: '{app.name}' is not running. Skipping launch.")
                return

            if app.launch_mode == LaunchMode.REUSE_ONLY.value:
                self.logger.info(f"'{app.name}' configured for REUSE_ONLY and is not currently running. Skipping.")
                return

            if not resolved_exe:
                warn_msg = f"Cannot launch '{app.name}': executable not found."
                self.logger.warning(warn_msg)
                status.warning = warn_msg
                report.warnings.append(warn_msg)
                return

            # Phase 3: Launch
            self.logger.info(f"Phase 3: Launching '{app.name}'...")
            self._emit(EventType.APPLICATION_LAUNCH_STARTED, f"Launching {app.name}", app_id=app.id)
            pid = self.launcher.launch(resolved_exe, app.arguments)
            status.was_launched = True
            report.apps_launched_or_reused += 1

            # Controlled launch delay
            if app.launch_delay_ms > 0:
                time.sleep(app.launch_delay_ms / 1000.0)

            # Refresh running procs list to include newly spawned PID
            new_proc = self.process_provider.get_process_info(pid)
            if new_proc:
                running_procs = [new_proc]
            else:
                running_procs = [ProcessInfo(pid=pid, name=os.path.basename(resolved_exe), executable_path=resolved_exe, cmdline=[])]

        if not app.move_existing_window:
            self.logger.info(f"Window move disabled for '{app.name}'. Skipping desktop movement.")
            return

        # -------------------------------------------------------------
        # Phase 4: Wait for application top-level window
        # -------------------------------------------------------------
        pids = [p.pid for p in running_procs]
        if not pids and status.was_launched:
            pids = [pid]
        windows = self._wait_for_windows(app, pids)
        if not windows:
            warn_msg = f"Timed out waiting for visible window for '{app.name}' (PID: {pids})."
            self.logger.warning(warn_msg)
            status.warning = warn_msg
            report.warnings.append(warn_msg)
            return

        status.window_found = True
        self.logger.info(f"Phase 4: Found {len(windows)} candidate window(s) for '{app.name}'.")

        # Apply Window Policy (MAIN_ONLY, ALL_MATCHING, TITLE_CONTAINS, etc.)
        matched_windows = self._filter_windows_by_policy(app, windows)
        if not matched_windows:
            warn_msg = f"No windows matched policy '{app.window_policy}' for '{app.name}'."
            self.logger.warning(warn_msg)
            status.warning = warn_msg
            report.warnings.append(warn_msg)
            return

        # -------------------------------------------------------------
        # Phase 5 & 6: Move and Verify
        # -------------------------------------------------------------
        all_moved = True
        all_verified = True

        for win in matched_windows:
            self._emit(EventType.WINDOW_MOVE_STARTED, f"Moving window '{win.title}' to Desktop {app.desktop}", app_id=app.id)
            moved = self.desktop_provider.move_window_to_desktop(win.hwnd, app.desktop)
            if moved:
                status.window_moved = True
                self.logger.success(f"Moved '{win.title}' (HWND {win.hwnd}) to Desktop {app.desktop}")
                self._emit(EventType.WINDOW_MOVE_COMPLETED, f"Moved window to Desktop {app.desktop}", app_id=app.id)

                # Verification
                verified = self.desktop_provider.is_window_on_desktop(win.hwnd, app.desktop)
                if verified is True:
                    self.logger.success(f"Verified '{win.title}' on Desktop {app.desktop}")
                    status.verified = True
                elif verified is False:
                    warn_v = f"Verification check failed: '{win.title}' not detected on Desktop {app.desktop}."
                    self.logger.warning(warn_v)
                    report.warnings.append(warn_v)
                    all_verified = False
                else:
                    self.logger.info(f"Verification unsupported by active provider for HWND {win.hwnd}.")
                    status.verified = True  # treat as unverified success
            else:
                all_moved = False
                err_move = f"Failed to move HWND {win.hwnd} for '{app.name}' to Desktop {app.desktop}."
                self.logger.error(err_move)
                report.errors.append(err_move)

        if not all_moved:
            status.error = "Failed to move one or more windows."

    def _wait_for_windows(self, app: AppConfig, pids: List[int]) -> List[WindowInfo]:
        """Polls for top-level windows matching PIDs or title with configurable timeout."""
        timeout_sec = app.window_timeout_ms / 1000.0
        start = time.time()
        interval = 0.25

        while time.time() - start < timeout_sec:
            if self.cancel_event.is_set():
                return []

            # 1. Search by PID
            windows: List[WindowInfo] = []
            for pid in pids:
                windows.extend(self.window_provider.find_windows_for_process(pid))

            # 2. Search by Title if PID search yielded nothing and title pattern exists
            if not windows and app.title_pattern:
                windows.extend(self.window_provider.find_windows_by_title(app.title_pattern))

            if windows:
                return windows

            time.sleep(interval)

        return []

    def _filter_windows_by_policy(self, app: AppConfig, candidate_windows: List[WindowInfo]) -> List[WindowInfo]:
        """Filters candidate windows according to AppConfig policy."""
        import re
        policy = app.window_policy

        if policy == WindowPolicy.ALL_MATCHING.value:
            return candidate_windows

        if policy == WindowPolicy.TITLE_CONTAINS.value and app.title_pattern:
            return [w for w in candidate_windows if app.title_pattern.lower() in w.title.lower()]

        if policy == WindowPolicy.TITLE_REGEX.value and app.title_pattern:
            try:
                rx = re.compile(app.title_pattern, re.IGNORECASE)
                return [w for w in candidate_windows if rx.search(w.title)]
            except re.error:
                return candidate_windows

        # Default: MAIN_ONLY -> pick the best main window
        non_min = [w for w in candidate_windows if not w.is_minimized]
        if non_min:
            return [non_min[0]]
        return [candidate_windows[0]]
