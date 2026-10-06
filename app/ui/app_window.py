"""
Main Desktop Application Window for Windows Virtual Desktop Workspace Manager.
Integrates Dashboard, Desktop Cards Panel, Live Logs, Status Bar, and Menus.
"""

from __future__ import annotations
import os
import sys
import platform
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional, List, Dict
from app import __version__
from app.models.workspace import WorkspaceConfig, WorkspaceProfile, DesktopConfig, AppConfig
from app.core.manager import WorkspaceManager
from app.ui.theme import ThemeManager
from app.ui.app_dialog import AppDialog
from app.ui.settings_dialog import SettingsDialog
from app.ui.log_view import LogViewPanel
from app.ui.confirmation_dialog import ConfirmationDialog
from app.ui.wizard_dialog import SetupWizardDialog
from app.ui.tray import TrayIconManager
from app.services.diagnostics_service import DiagnosticsService
from app.discovery.running_apps import RunningAppDiscoverer
from app.logging.logger import get_logger


class MainWindow(tk.Tk):
    """Primary application window for Virtual Desktop Workspace Manager."""

    def __init__(self, manager: WorkspaceManager, start_minimized: bool = False):
        super().__init__()
        self.manager = manager
        self.logger = get_logger()
        self.diagnostics_service = DiagnosticsService(
            config=self.manager.config,
            desktop_provider=self.manager.desktop_provider,
            process_provider=self.manager.process_provider,
            window_provider=self.manager.window_provider
        )
        self.running_discoverer = RunningAppDiscoverer(
            process_provider=self.manager.process_provider,
            window_provider=self.manager.window_provider
        )

        self.title("Virtual Desktop Workspace Manager")
        self.geometry("980x780")
        self.minsize(860, 640)

        # Apply Theme
        self.palette = ThemeManager.apply_theme(self, self.manager.config.general.theme)

        # Setup System Tray
        self.tray_manager = TrayIconManager(
            on_open=self._tray_open_action,
            on_launch_workspace=self._tray_launch_action,
            on_sync_workspace=self._tray_sync_action,
            on_toggle_pause=self._tray_pause_action,
            on_view_logs=self._tray_open_action,
            on_exit=self._on_exit,
            is_paused=not self.manager.config.safety.automation_enabled
        )
        if self.manager.config.general.minimize_to_tray:
            self.tray_manager.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close_requested)

        self._build_ui()
        self._refresh_all_views()

        # Handle start minimized
        if start_minimized or self.manager.config.general.start_minimized:
            self.withdraw()

        # Check for incomplete operation crash marker (Section 65)
        self.after(300, self._check_crash_recovery)

        # Check first-run wizard (Section 78)
        if not self.manager.config.general.first_run_completed:
            self.after(500, self._open_setup_wizard)

    # -------------------------------------------------------------
    # UI Building
    # -------------------------------------------------------------

    def _build_ui(self) -> None:
        # 1. Header Toolbar
        self._build_header_toolbar()

        # 2. Main content container (PanedWindow: Top for Dashboard/Desktops, Bottom for Logs)
        self.paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Top section: Dashboard + Desktop Panel
        top_container = ttk.Frame(self.paned)
        self.paned.add(top_container, weight=3)

        # Dashboard View
        self._build_dashboard_view(top_container)

        # Desktop Cards Scrollable Area
        self._build_desktop_cards_area(top_container)

        # Bottom section: Live Log Panel
        bottom_container = ttk.LabelFrame(self.paned, text="Live Operation Logs & Diagnostics", padding=6)
        self.paned.add(bottom_container, weight=2)
        self.log_panel = LogViewPanel(
            bottom_container,
            diagnostics_service=self.diagnostics_service,
            palette=self.palette
        )
        self.log_panel.pack(fill=tk.BOTH, expand=True)

        # 3. Status bar
        self._build_status_bar()

    def _build_header_toolbar(self) -> None:
        toolbar = ttk.Frame(self, padding=(12, 8))
        toolbar.pack(fill=tk.X)

        # Title & Version
        title_box = ttk.Frame(toolbar)
        title_box.pack(side=tk.LEFT)
        ttk.Label(title_box, text="Virtual Desktop Manager", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_box, text=f"v{__version__}", style="Muted.TLabel").pack(side=tk.LEFT, padx=6, pady=(4, 0))

        # Profile Switcher
        prof_frame = ttk.Frame(toolbar)
        prof_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(prof_frame, text="Profile:").pack(side=tk.LEFT, padx=(0, 4))
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(prof_frame, textvariable=self.profile_var, state="readonly", width=18)
        self.profile_combo.pack(side=tk.LEFT)
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_switched)

        ttk.Button(prof_frame, text="+", width=3, command=self._add_new_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text="Export", width=7, command=self._export_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text="Import", width=7, command=self._import_profile).pack(side=tk.LEFT, padx=2)

        # Right side controls
        right_frame = ttk.Frame(toolbar)
        right_frame.pack(side=tk.RIGHT)

        # Emergency STOP button
        self.btn_stop = ttk.Button(right_frame, text="STOP", style="Danger.TButton", width=7, command=self._on_stop_clicked)
        self.btn_stop.pack(side=tk.RIGHT, padx=4)
        self.btn_stop.configure(state=tk.DISABLED)

        # Automation toggle
        self.auto_toggle_var = tk.BooleanVar(value=self.manager.config.safety.automation_enabled)
        self.chk_auto = ttk.Checkbutton(
            right_frame,
            text="Automation Active",
            variable=self.auto_toggle_var,
            command=self._on_auto_toggle
        )
        self.chk_auto.pack(side=tk.RIGHT, padx=8)

        ttk.Button(right_frame, text="About", width=7, command=self._show_about_dialog).pack(side=tk.RIGHT, padx=4)
        ttk.Button(right_frame, text="Health Check", width=12, command=self._show_health_check_dialog).pack(side=tk.RIGHT, padx=4)
        ttk.Button(right_frame, text="Wizard", width=8, command=self._open_setup_wizard).pack(side=tk.RIGHT, padx=4)
        ttk.Button(right_frame, text="Settings", width=8, command=self._open_settings_dialog).pack(side=tk.RIGHT, padx=4)

    def _build_dashboard_view(self, parent: ttk.Frame) -> None:
        self.dash_frame = ttk.LabelFrame(parent, text="Workspace Dashboard", padding=10)
        self.dash_frame.pack(fill=tk.X, pady=(0, 8))

        # Row 1: Current Desktop & Status indicators
        stat_row = ttk.Frame(self.dash_frame)
        stat_row.pack(fill=tk.X, pady=(0, 8))

        self.lbl_current_desktop = ttk.Label(stat_row, text="Current Desktop: Detecting...", font=("Segoe UI", 10, "bold"))
        self.lbl_current_desktop.pack(side=tk.LEFT)

        self.lbl_summary_stats = ttk.Label(stat_row, text="Desktops: 0 | Configured Apps: 0 | Running: 0", style="Muted.TLabel")
        self.lbl_summary_stats.pack(side=tk.RIGHT)

        # Row 2: Status check badges
        self.badge_frame = ttk.Frame(self.dash_frame)
        self.badge_frame.pack(fill=tk.X, pady=(0, 10))

        # Row 3: Action Buttons (Launch, Sync, Dry Run, Refresh)
        act_row = ttk.Frame(self.dash_frame)
        act_row.pack(fill=tk.X)

        self.btn_launch = ttk.Button(act_row, text="▶ Launch Workspace", style="Primary.TButton", command=self._on_launch_clicked)
        self.btn_launch.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_sync = ttk.Button(act_row, text="⟳ Sync Workspace", command=self._on_sync_clicked)
        self.btn_sync.pack(side=tk.LEFT, padx=4)

        self.btn_dry_run = ttk.Button(act_row, text="🔍 Dry Run", command=self._on_dry_run_clicked)
        self.btn_dry_run.pack(side=tk.LEFT, padx=4)

        self.btn_refresh = ttk.Button(act_row, text="↻ Refresh", command=self._refresh_all_views)
        self.btn_refresh.pack(side=tk.LEFT, padx=4)

        ttk.Button(act_row, text="+ Add Application", command=lambda: self._open_add_app_dialog()).pack(side=tk.RIGHT, padx=4)
        ttk.Button(act_row, text="+ Add Desktop", command=self._on_add_desktop_clicked).pack(side=tk.RIGHT, padx=4)

    def _build_desktop_cards_area(self, parent: ttk.Frame) -> None:
        cards_container = ttk.LabelFrame(parent, text="Virtual Desktops & Application Layout", padding=8)
        cards_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(cards_container, bg=self.palette["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(cards_container, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_cards = ttk.Frame(canvas)

        self.scrollable_cards.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_cards, anchor=tk.NW, width=920)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_status_bar(self) -> None:
        self.status_bar = ttk.Frame(self, relief="sunken", padding=(8, 2))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = ttk.Label(self.status_bar, text="Ready", style="Muted.TLabel")
        self.lbl_status.pack(side=tk.LEFT)

        self.lbl_progress = ttk.Label(self.status_bar, text="", style="Muted.TLabel")
        self.lbl_progress.pack(side=tk.RIGHT)

    # -------------------------------------------------------------
    # Refresh & Rendering
    # -------------------------------------------------------------

    def _refresh_all_views(self) -> None:
        """Refreshes profile list, dashboard badges, current desktop, and desktop cards."""
        # 1. Update Profile combo
        profiles = self.manager.config.profiles
        names = [p.name for p in profiles]
        self.profile_combo.configure(values=names)
        active_prof = self.manager.config.get_active_profile()
        if active_prof.name in names:
            self.profile_combo.current(names.index(active_prof.name))

        # 2. Update Current Desktop
        curr_dt = self.manager.get_current_desktop_number()
        total_dt = self.manager.get_desktop_count()
        dt_name = ""
        for d in active_prof.desktops:
            if d.number == curr_dt:
                dt_name = f" — {d.name}"
                break
        self.lbl_current_desktop.configure(text=f"Current Desktop: Desktop {curr_dt}{dt_name}")

        # 3. Calculate app stats
        configured_count = len(active_prof.apps)
        running_count = 0
        missing_count = 0

        for a in active_prof.apps:
            exe, _ = self.manager.app_detector.detect_executable(a)
            if not exe:
                missing_count += 1
            cand = list(a.process_names)
            if exe:
                cand.append(os.path.basename(exe))
            if self.manager.process_provider.get_running_processes_matching(cand):
                running_count += 1

        self.lbl_summary_stats.configure(
            text=f"Desktops: {total_dt} | Apps: {configured_count} configured, {running_count} running, {missing_count} missing"
        )

        # 4. Render Desktop Badges on Dashboard
        for child in self.badge_frame.winfo_children():
            child.destroy()

        badge_row = ttk.Frame(self.badge_frame)
        badge_row.pack(anchor=tk.W)
        ttk.Label(badge_row, text="Status: ", style="SubHeader.TLabel").pack(side=tk.LEFT, padx=(0, 4))

        for dt in sorted(active_prof.desktops, key=lambda d: d.number):
            apps = active_prof.get_apps_for_desktop(dt.number)
            has_missing = any(not self.manager.app_detector.detect_executable(a)[0] for a in apps)
            if has_missing:
                txt = f"⚠ Desktop {dt.number} ({dt.name}) Missing App"
                style = "Warning.TLabel"
            else:
                txt = f"✓ Desktop {dt.number} ({dt.name}) Ready"
                style = "Success.TLabel"
            ttk.Label(badge_row, text=txt, style=style).pack(side=tk.LEFT, padx=6)

        # 5. Render Desktop Cards
        self._render_desktop_cards(active_prof, curr_dt)

    def _render_desktop_cards(self, profile: WorkspaceProfile, current_desktop_num: int) -> None:
        for child in self.scrollable_cards.winfo_children():
            child.destroy()

        desktops = sorted(profile.desktops, key=lambda d: d.number)
        if not desktops:
            ttk.Label(self.scrollable_cards, text="No virtual desktops configured. Click '+ Add Desktop' to start.", style="Muted.TLabel").pack(pady=20)
            return

        for dt in desktops:
            is_active = (dt.number == current_desktop_num)
            card_title = f"Desktop {dt.number} — {dt.name}" + ("  [ACTIVE]" if is_active else "")
            card = ttk.LabelFrame(self.scrollable_cards, text=card_title, padding=10)
            card.pack(fill=tk.X, pady=6, padx=4)

            # Card Header Toolbar
            header_bar = ttk.Frame(card)
            header_bar.pack(fill=tk.X, pady=(0, 6))

            ttk.Button(header_bar, text="Open Desktop", width=13, command=lambda n=dt.number: self._open_desktop(n)).pack(side=tk.LEFT, padx=2)
            ttk.Button(header_bar, text="Rename", width=8, command=lambda d=dt: self._rename_desktop(d)).pack(side=tk.LEFT, padx=2)
            ttk.Button(header_bar, text="+ Add App", width=10, command=lambda n=dt.number: self._open_add_app_dialog(target_desktop=n)).pack(side=tk.LEFT, padx=2)

            # Apps in this desktop
            apps = profile.get_apps_for_desktop(dt.number)
            if not apps:
                ttk.Label(card, text="  No applications assigned to this desktop.", style="Muted.TLabel").pack(anchor=tk.W, pady=4)
            else:
                apps_box = ttk.Frame(card)
                apps_box.pack(fill=tk.X, pady=4)

                for app in apps:
                    self._render_app_row(apps_box, app, profile)

    def _render_app_row(self, parent: ttk.Frame, app: AppConfig, profile: WorkspaceProfile) -> None:
        row = ttk.Frame(parent, padding=(4, 2))
        row.pack(fill=tk.X, pady=2)

        # Detection & Running status
        exe, _ = self.manager.app_detector.detect_executable(app)
        cand = list(app.process_names)
        if exe:
            cand.append(os.path.basename(exe))
        is_running = len(self.manager.process_provider.get_running_processes_matching(cand)) > 0

        if not exe:
            status_icon = "⚠"
            status_style = "Warning.TLabel"
            status_tip = "Executable not found"
        elif is_running:
            status_icon = "✓"
            status_style = "Success.TLabel"
            status_tip = "Running"
        else:
            status_icon = "○"
            status_style = "Muted.TLabel"
            status_tip = "Stopped"

        ttk.Label(row, text=status_icon, style=status_style, width=3).pack(side=tk.LEFT)
        ttk.Label(row, text=app.name, font=("Segoe UI", 9, "bold"), width=24).pack(side=tk.LEFT)
        ttk.Label(row, text=f"({status_tip} | {app.window_policy})", style="Muted.TLabel", width=22).pack(side=tk.LEFT)

        # Quick Actions
        actions_bar = ttk.Frame(row)
        actions_bar.pack(side=tk.RIGHT)

        ttk.Button(actions_bar, text="Move to...", width=9, command=lambda a=app: self._show_reassign_dialog(a)).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_bar, text="Edit", width=6, command=lambda a=app: self._open_edit_app_dialog(a)).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_bar, text="Remove", width=8, command=lambda a=app: self._confirm_remove_app(a)).pack(side=tk.LEFT, padx=2)

    # -------------------------------------------------------------
    # Action Handlers
    # -------------------------------------------------------------

    def _open_desktop(self, desktop_number: int) -> None:
        """Switches Windows view to that desktop."""
        success = self.manager.switch_to_desktop(desktop_number)
        if success:
            self.lbl_status.configure(text=f"Switched view to Desktop {desktop_number}")
            self._refresh_all_views()
        else:
            messagebox.showwarning("Desktop Switch", f"Could not switch to Desktop {desktop_number}.", parent=self)

    def _rename_desktop(self, dt: DesktopConfig) -> None:
        new_name = simpledialog.askstring("Rename Desktop", f"Enter new name for Desktop {dt.number}:", initialvalue=dt.name, parent=self)
        if new_name is not None and new_name.strip():
            self.logger.info("Desktop Mapping Changed: Desktop %d renamed to '%s'", dt.number, new_name.strip())
            self.manager.rename_desktop(dt.number, new_name.strip())
            self._refresh_all_views()

    def _on_add_desktop_clicked(self) -> None:
        name = simpledialog.askstring("Add Desktop", "Enter custom name for new desktop:", parent=self)
        if name is not None:
            self.logger.info("Desktop Mapping Changed: Added new Desktop '%s'", name.strip())
            self.manager.add_desktop(name.strip())
            self._refresh_all_views()

    def _open_add_app_dialog(self, target_desktop: int = 1) -> None:
        app = AppConfig(desktop=target_desktop)
        dialog = AppDialog(
            parent=self,
            app=app,
            desktops=self.manager.config.get_active_profile().desktops,
            running_discoverer=self.running_discoverer,
            on_save=lambda new_app: self._on_app_added(new_app)
        )

    def _on_app_added(self, app: AppConfig) -> None:
        self.logger.info("Application Added: '%s' -> Desktop %d", app.name, app.desktop)
        self.manager.add_app_to_profile(app)
        self._refresh_all_views()

    def _open_edit_app_dialog(self, app: AppConfig) -> None:
        dialog = AppDialog(
            parent=self,
            app=app,
            desktops=self.manager.config.get_active_profile().desktops,
            running_discoverer=self.running_discoverer,
            on_save=lambda updated_app: self._on_app_updated(updated_app)
        )

    def _on_app_updated(self, app: AppConfig) -> None:
        self.logger.info("Application Updated: '%s' on Desktop %d", app.name, app.desktop)
        self.manager.update_app_in_profile(app)
        self._refresh_all_views()

    def _show_reassign_dialog(self, app: AppConfig) -> None:
        """Section 14: Reassign application between desktops with optional immediate move."""
        profile = self.manager.config.get_active_profile()

        top = tk.Toplevel(self)
        top.title(f"Reassign '{app.name}'")
        top.geometry("420x240")
        top.resizable(False, False)
        top.transient(self)
        top.grab_set()

        frame = ttk.Frame(top, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Reassign '{app.name}'", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(frame, text=f"Current assignment: Desktop {app.desktop}").pack(anchor=tk.W, pady=2)

        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=8)
        ttk.Label(row, text="Move to Desktop:").pack(side=tk.LEFT, padx=(0, 6))

        choices = [f"Desktop {d.number} — {d.name}" for d in profile.desktops]
        combo = ttk.Combobox(row, values=choices, state="readonly", width=26)
        combo.pack(side=tk.LEFT)
        for i, d in enumerate(profile.desktops):
            if d.number == app.desktop:
                combo.current(i)
                break

        move_now_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Move currently running window immediately", variable=move_now_var).pack(anchor=tk.W, pady=6)

        def save_reassign():
            idx = combo.current()
            if idx < 0:
                return
            new_target = profile.desktops[idx].number
            self.logger.info("Application Reassigned: '%s' -> Desktop %d", app.name, new_target)
            self.manager.reassign_app(app.id, new_target)

            if move_now_var.get():
                moved = self.manager.move_running_window_now(app.id, new_target)
                if moved:
                    messagebox.showinfo("Window Moved", f"Moved running window for '{app.name}' to Desktop {new_target}.", parent=top)
                else:
                    messagebox.showinfo("Assignment Saved", f"Reassigned '{app.name}' to Desktop {new_target}.\n(No running window found to move immediately).", parent=top)

            top.destroy()
            self._refresh_all_views()

        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(btn_bar, text="Cancel", command=top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_bar, text="Save", style="Primary.TButton", command=save_reassign).pack(side=tk.RIGHT, padx=4)

    def _confirm_remove_app(self, app: AppConfig) -> None:
        """Section 15: Safe removal with explicit confirmation stating it does not uninstall."""
        msg = (
            f"Remove '{app.name}' from Desktop {app.desktop}?\n\n"
            "This will NOT uninstall the application.\n"
            "It only removes its workspace configuration."
        )
        if messagebox.askokcancel("Confirm Remove", msg, parent=self):
            self.logger.info("Application Removed: '%s' from Desktop %d", app.name, app.desktop)
            self.manager.remove_app_from_profile(app.id)
            self._refresh_all_views()

    # -------------------------------------------------------------
    # Execution Triggers
    # -------------------------------------------------------------

    def _on_launch_clicked(self) -> None:
        if self.manager.config.safety.dry_run_default:
            self._on_dry_run_clicked()
            return
        active_prof = self.manager.config.get_active_profile()
        self.logger.info("Workspace Launch Started: Profile '%s'", active_prof.name)
        if self.manager.config.safety.require_confirmation and self.manager.config.general.confirm_before_execution:
            ConfirmationDialog(
                self,
                "Launch Workspace",
                on_confirm=lambda: self._execute_operation(is_sync=False),
                on_cancel=lambda: self.logger.info("Workspace Launch Cancelled by user")
            )
        else:
            self._execute_operation(is_sync=False)

    def _on_sync_clicked(self) -> None:
        active_prof = self.manager.config.get_active_profile()
        self.logger.info("Workspace Sync Started: Profile '%s'", active_prof.name)
        if self.manager.config.safety.require_confirmation and self.manager.config.general.confirm_before_execution:
            ConfirmationDialog(
                self,
                "Sync Workspace",
                on_confirm=lambda: self._execute_operation(is_sync=True),
                on_cancel=lambda: self.logger.info("Workspace Sync Cancelled by user")
            )
        else:
            self._execute_operation(is_sync=True)

    def _on_dry_run_clicked(self) -> None:
        result = self.manager.dry_run()
        preview_text = result.format_preview()

        # Display in dialog
        top = tk.Toplevel(self)
        top.title("Dry Run Preview")
        top.geometry("640x500")
        top.transient(self)
        top.grab_set()

        txt = tk.Text(top, wrap=tk.WORD, font=("Consolas", 9), padx=10, pady=10)
        txt.insert(tk.END, preview_text)
        txt.configure(state=tk.DISABLED)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        btn_bar = ttk.Frame(top, padding=8)
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="Close", command=top.destroy).pack(side=tk.RIGHT)

    def _execute_operation(self, is_sync: bool) -> None:
        self.btn_launch.configure(state=tk.DISABLED)
        self.btn_sync.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)
        op_title = "Syncing" if is_sync else "Launching"
        self.lbl_status.configure(text=f"Operation in progress: {op_title} workspace...")

        def run_thread():
            try:
                if is_sync:
                    report = self.manager.sync_workspace()
                else:
                    report = self.manager.launch_workspace()

                self.after(0, self._on_operation_completed, report)
            except Exception as ex:
                self.logger.error(f"Execution error: {ex}")
                self.after(0, lambda: messagebox.showerror("Execution Failure", str(ex), parent=self))
                self.after(0, self._reset_op_buttons)

        thread = threading.Thread(target=run_thread, daemon=True)
        thread.start()

    def _on_operation_completed(self, report) -> None:
        self._reset_op_buttons()
        self.lbl_status.configure(text=f"Workspace {report.operation_type} completed ({report.duration_seconds}s)")
        self._refresh_all_views()

        # Show summary popup matching Section 102
        messagebox.showinfo("Operation Summary", report.summary_text(), parent=self)

    def _on_stop_clicked(self) -> None:
        self.logger.info("Workspace Operation Cancelled (Emergency STOP)")
        self.manager.stop_current_operation()
        self.btn_stop.configure(state=tk.DISABLED)
        self.lbl_status.configure(text="Cancellation requested...")

    def _reset_op_buttons(self) -> None:
        self.btn_launch.configure(state=tk.NORMAL)
        self.btn_sync.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)

    # -------------------------------------------------------------
    # Crash Recovery & First-Run Wizard
    # -------------------------------------------------------------

    def _check_crash_recovery(self) -> None:
        marker = self.manager.config_store.check_incomplete_operation()
        if marker:
            msg = (
                f"Notice: A previous workspace operation ('{marker.get('operation')}') "
                f"started at {marker.get('time_str')} may not have completed cleanly.\n\n"
                "Would you like to run 'Sync Workspace' now to reconcile your state?"
            )
            if messagebox.askyesno("Crash Recovery", msg, parent=self):
                self._execute_operation(is_sync=True)
            self.manager.config_store.clear_operation_marker()

    def _open_setup_wizard(self) -> None:
        wizard = SetupWizardDialog(
            parent=self,
            config=self.manager.config,
            desktop_provider=self.manager.desktop_provider,
            process_provider=self.manager.process_provider,
            window_provider=self.manager.window_provider,
            app_detector=self.manager.app_detector,
            config_store=self.manager.config_store,
            on_completed=self._refresh_all_views
        )

    def _open_settings_dialog(self) -> None:
        SettingsDialog(
            parent=self,
            config=self.manager.config,
            on_save=lambda _: self._refresh_all_views()
        )

    def _show_health_check_dialog(self) -> None:
        """Section 113: Diagnostic-only health check dialog verifying 8 critical subsystems."""
        checks = self.diagnostics_service.run_health_check()
        summary_text = self.diagnostics_service.format_health_check_summary()

        top = tk.Toplevel(self)
        top.title("System Health Check")
        top.geometry("640x500")
        top.transient(self)
        top.grab_set()

        content = ttk.Frame(top, padding=16)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="System Health Check", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(content, text="Diagnostic verification of platform, providers, configuration, and storage.", style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 10))

        list_frame = ttk.LabelFrame(content, text="Subsystem Status", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        all_ok = True
        for key, info in checks.items():
            row = ttk.Frame(list_frame)
            row.pack(fill=tk.X, pady=2)
            mark = "✓" if info["ok"] else "✗"
            color_fg = "#2e7d32" if info["ok"] else "#c62828"
            if not info["ok"]:
                all_ok = False

            lbl_mark = tk.Label(row, text=mark, fg=color_fg, font=("Segoe UI", 10, "bold"), width=3)
            lbl_mark.pack(side=tk.LEFT)
            ttk.Label(row, text=f"{info['title']}:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
            ttk.Label(row, text=info['detail'], style="Muted.TLabel").pack(side=tk.LEFT)

        banner_txt = "OVERALL STATUS: HEALTHY (Ready for safe operation)" if all_ok else "OVERALL STATUS: ATTENTION NEEDED"
        banner_fg = "#2e7d32" if all_ok else "#c62828"
        lbl_banner = tk.Label(content, text=banner_txt, fg=banner_fg, font=("Segoe UI", 10, "bold"))
        lbl_banner.pack(anchor=tk.W, pady=(0, 10))

        btn_bar = ttk.Frame(content)
        btn_bar.pack(fill=tk.X)

        def copy_summary():
            self.clipboard_clear()
            self.clipboard_append(summary_text)
            messagebox.showinfo("Copied", "Health check summary copied to clipboard.", parent=top)

        ttk.Button(btn_bar, text="Copy Report", command=copy_summary).pack(side=tk.LEFT)
        ttk.Button(btn_bar, text="Close", command=top.destroy).pack(side=tk.RIGHT)

    def _show_about_dialog(self) -> None:
        """Section 140: About dialog showing version, runtime, dependencies, API provider, and diagnostics shortcut."""
        top = tk.Toplevel(self)
        top.title("About Virtual Desktop Workspace Manager")
        top.geometry("540x440")
        top.resizable(False, False)
        top.transient(self)
        top.grab_set()

        content = ttk.Frame(top, padding=20)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="Virtual Desktop Workspace Manager", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(content, text=f"Version {__version__} — Production Release", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 10))

        info_frame = ttk.LabelFrame(content, text="System & Runtime Details", padding=12)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        items = [
            ("Operating System:", f"{platform.system()} {platform.release()} (Build {platform.version()})"),
            ("Python Runtime:", f"{sys.version.split()[0]} ({platform.architecture()[0]})"),
            ("Virtual Desktop Provider:", self.manager.desktop_provider.name),
            ("Process Provider:", self.manager.process_provider.name),
            ("Window Provider:", self.manager.window_provider.name),
            ("License:", "MIT License"),
            ("Offline Mode:", "Enabled (Zero External Network Requests)"),
            ("Integrity Level:", "Standard User (Medium Integrity)"),
        ]

        for label, val in items:
            row = ttk.Frame(info_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=label, width=24, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(row, text=val, style="Muted.TLabel").pack(side=tk.LEFT)

        btn_bar = ttk.Frame(content)
        btn_bar.pack(fill=tk.X)

        ttk.Button(btn_bar, text="🩺 Run Health Check", command=lambda: [top.destroy(), self._show_health_check_dialog()]).pack(side=tk.LEFT)
        ttk.Button(btn_bar, text="Close", command=top.destroy).pack(side=tk.RIGHT)

    def _on_auto_toggle(self) -> None:
        active = self.auto_toggle_var.get()
        self.manager.config.safety.automation_enabled = active
        self.manager.save_config()
        status_txt = "Active" if active else "Paused"
        self.logger.info("Automation %s", "Enabled" if active else "Disabled")
        self.lbl_status.configure(text=f"Automation {status_txt}")

    # -------------------------------------------------------------
    # Profile Management
    # -------------------------------------------------------------

    def _on_profile_switched(self, _event=None) -> None:
        sel_idx = self.profile_combo.current()
        if sel_idx >= 0 and sel_idx < len(self.manager.config.profiles):
            chosen_profile = self.manager.config.profiles[sel_idx]
            self.logger.info("Profile Switched: to '%s'", chosen_profile.name)
            self.manager.config.general.active_profile_id = chosen_profile.id
            self.manager.save_config()
            self._refresh_all_views()

    def _add_new_profile(self) -> None:
        name = simpledialog.askstring("New Profile", "Enter name for new workspace profile:", parent=self)
        if name and name.strip():
            import uuid
            new_prof = WorkspaceProfile(
                id=str(uuid.uuid4())[:8],
                name=name.strip(),
                desktops=[DesktopConfig(number=i, name=f"Desktop {i}") for i in range(1, 5)],
                apps=[]
            )
            self.manager.config.profiles.append(new_prof)
            self.manager.config.general.active_profile_id = new_prof.id
            self.manager.save_config()
            self._refresh_all_views()

    def _export_profile(self) -> None:
        prof = self.manager.config.get_active_profile()
        target = filedialog.asksaveasfilename(
            parent=self,
            title=f"Export Profile '{prof.name}'",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"{prof.name.lower().replace(' ', '_')}_profile.json"
        )
        if target:
            from pathlib import Path
            self.manager.config_store.export_profile(prof, Path(target))
            messagebox.showinfo("Exported", f"Profile exported to {target}", parent=self)

    def _import_profile(self) -> None:
        source = filedialog.askopenfilename(
            parent=self,
            title="Import Workspace Profile",
            filetypes=[("JSON Files", "*.json")]
        )
        if source:
            from pathlib import Path
            try:
                prof = self.manager.config_store.import_profile(Path(source))
                # Add or replace
                existing = [p for p in self.manager.config.profiles if p.id == prof.id]
                if existing:
                    import uuid
                    prof.id = str(uuid.uuid4())[:8]
                self.manager.config.profiles.append(prof)
                self.manager.config.general.active_profile_id = prof.id
                self.manager.save_config()
                self._refresh_all_views()
                self.logger.info("Configuration Imported: Profile '%s'", prof.name)
                messagebox.showinfo("Imported", f"Profile '{prof.name}' successfully imported!", parent=self)
            except Exception as ex:
                self.logger.error("Configuration Import Failed: %s", ex)
                messagebox.showerror("Import Error", f"Failed to import profile: {ex}", parent=self)

    # -------------------------------------------------------------
    # Close & Tray Handlers
    # -------------------------------------------------------------

    def _on_close_requested(self) -> None:
        if self.manager.config.general.minimize_to_tray:
            self.withdraw()
        else:
            self._on_exit()

    def _tray_open_action(self) -> None:
        self.after(0, self.deiconify)
        self.after(0, self.lift)

    def _tray_launch_action(self) -> None:
        self.after(0, self._on_launch_clicked)

    def _tray_sync_action(self) -> None:
        self.after(0, self._on_sync_clicked)

    def _tray_pause_action(self) -> None:
        self.after(0, lambda: self.auto_toggle_var.set(not self.auto_toggle_var.get()))
        self.after(0, self._on_auto_toggle)

    def _on_exit(self) -> None:
        self.tray_manager.stop()
        self.destroy()
