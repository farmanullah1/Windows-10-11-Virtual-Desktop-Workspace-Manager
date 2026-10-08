"""
Main Desktop Application Window for Windows Virtual Desktop Workspace Manager.
Completely overhauled according to Revision 2.0 UX, information architecture,
keyboard accessibility, unsaved changes protection, and diagnostics requirements.
"""

from __future__ import annotations
import os
import sys
import time
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from app import __version__
from app.models.workspace import WorkspaceConfig, WorkspaceProfile, DesktopConfig, AppConfig
from app.models.history import OperationHistoryRecord
from app.models.state import ApplicationState
from app.core.manager import WorkspaceManager
from app.ui.theme import ThemeManager
from app.ui.app_dialog import AppDialog
from app.ui.settings_dialog import SettingsDialog
from app.ui.log_view import LogViewPanel
from app.ui.confirmation_dialog import ConfirmationDialog
from app.ui.wizard_dialog import SetupWizardDialog
from app.ui.tray import TrayIconManager
from app.services.diagnostics_service import DiagnosticsService
from app.services.support_bundle import SupportBundleService
from app.discovery.running_apps import RunningAppDiscoverer
from app.logging.logger import get_logger


class MainWindow(tk.Tk):
    """Primary application window for Virtual Desktop Workspace Manager."""

    def __init__(self, manager: WorkspaceManager, start_minimized: bool = False):
        super().__init__()
        self.manager = manager
        self.logger = get_logger()
        self.is_dirty: bool = False  # Unsaved-change tracking (Section 23)

        self.diagnostics_service = DiagnosticsService(
            config=self.manager.config,
            desktop_provider=self.manager.desktop_provider,
            process_provider=self.manager.process_provider,
            window_provider=self.manager.window_provider
        )
        self.support_bundle_service = SupportBundleService(
            diagnostics_service=self.diagnostics_service,
            config_store=self.manager.config_store
        )
        self.running_discoverer = RunningAppDiscoverer(
            process_provider=self.manager.process_provider,
            window_provider=self.manager.window_provider
        )

        self.title("Virtual Desktop Workspace Manager")
        self.geometry("1060x820")
        self.minsize(920, 680)

        # Apply theme
        self.palette = ThemeManager.apply_theme(self, self.manager.config.general.theme)

        # Setup System Tray
        self.tray_manager = TrayIconManager(
            on_open=self._tray_open_action,
            on_launch_workspace=self._tray_launch_action,
            on_sync_workspace=self._tray_sync_action,
            on_toggle_pause=self._tray_pause_action,
            on_view_logs=lambda: self._select_tab(6),
            on_exit=self._on_exit,
            is_paused=not self.manager.config.safety.automation_enabled
        )
        if self.manager.config.general.minimize_to_tray:
            self.tray_manager.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close_requested)

        self._bind_shortcuts()
        self._build_ui()
        self._refresh_all_views()

        # Handle start minimized
        if start_minimized or self.manager.config.general.start_minimized:
            self.withdraw()

        # Check crash recovery (Section 46)
        self.after(300, self._check_crash_recovery)

        # Check first-run wizard (Section 32)
        if not self.manager.config.general.first_run_completed:
            self.after(500, self._open_setup_wizard)

    # -------------------------------------------------------------
    # Keyboard Navigation & Shortcuts (Section 19)
    # -------------------------------------------------------------

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-s>", lambda e: self._save_changes())
        self.bind("<Control-r>", lambda e: self._refresh_all_views())
        self.bind("<F5>", lambda e: self._refresh_all_views())
        self.bind("<Control-f>", lambda e: self._focus_search())
        self.bind("<Control-l>", lambda e: self._select_tab(6))  # Logs tab
        self.bind("<Control-comma>", lambda e: self._select_tab(8))  # Settings tab
        self.bind("<Escape>", lambda e: self._on_escape())

    def _focus_search(self) -> None:
        self._select_tab(2)  # Applications tab
        if hasattr(self, "app_search_entry"):
            self.app_search_entry.focus_set()

    def _select_tab(self, index: int) -> None:
        try:
            self.notebook.select(index)
        except Exception:
            pass

    def _on_escape(self) -> None:
        if hasattr(self, "app_search_var") and self.app_search_var.get():
            self.app_search_var.set("")
            self._refresh_applications_view()

    # -------------------------------------------------------------
    # Main UI Shell
    # -------------------------------------------------------------

    def _build_ui(self) -> None:
        # 1. Global Header Toolbar (Section 6.1)
        self._build_header()

        # 2. Main Tabbed Navigation (Section 6)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 6))

        # Build each dedicated screen
        self._build_dashboard_tab()
        self._build_workspaces_tab()
        self._build_applications_tab()
        self._build_virtual_desktops_tab()
        self._build_execution_tab()
        self._build_history_tab()
        self._build_logs_tab()
        self._build_diagnostics_tab()
        self._build_settings_tab()
        self._build_about_tab()

        # 3. Status Bar
        self._build_status_bar()

    # -------------------------------------------------------------
    # 1. Global Header
    # -------------------------------------------------------------

    def _build_header(self) -> None:
        header = ttk.Frame(self, padding=(12, 8))
        header.pack(fill=tk.X)

        # Title & Version
        title_box = ttk.Frame(header)
        title_box.pack(side=tk.LEFT)
        ttk.Label(title_box, text="Virtual Desktop Workspace Manager", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_box, text=f"v{__version__}", style="Muted.TLabel").pack(side=tk.LEFT, padx=6, pady=(4, 0))

        # Profile Switcher Box
        prof_frame = ttk.Frame(header)
        prof_frame.pack(side=tk.LEFT, padx=16)
        ttk.Label(prof_frame, text="Profile:").pack(side=tk.LEFT, padx=(0, 4))
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(prof_frame, textvariable=self.profile_var, state="readonly", width=16)
        self.profile_combo.pack(side=tk.LEFT)
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_switched)

        ttk.Button(prof_frame, text="+", width=3, command=self._add_new_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text="Duplicate", width=9, command=self._duplicate_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text="Export", width=7, command=self._export_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(prof_frame, text="Import", width=7, command=self._import_profile).pack(side=tk.LEFT, padx=2)

        # Right-side indicators and controls
        right_box = ttk.Frame(header)
        right_box.pack(side=tk.RIGHT)

        # Emergency STOP button (Section 6.2)
        self.btn_stop = ttk.Button(right_box, text="■ STOP", style="Danger.TButton", width=9, command=self._on_stop_clicked)
        self.btn_stop.pack(side=tk.RIGHT, padx=4)
        self.btn_stop.configure(state=tk.DISABLED)

        # Save Changes button (highlighted when dirty)
        self.btn_save_changes = ttk.Button(right_box, text="Save Changes", style="Primary.TButton", width=13, command=self._save_changes)
        self.btn_save_changes.pack(side=tk.RIGHT, padx=4)
        self.btn_save_changes.configure(state=tk.DISABLED)

        # Automation active toggle
        self.auto_toggle_var = tk.BooleanVar(value=self.manager.config.safety.automation_enabled)
        self.chk_auto = ttk.Checkbutton(
            right_box,
            text="Automation Active",
            variable=self.auto_toggle_var,
            command=self._on_auto_toggle
        )
        self.chk_auto.pack(side=tk.RIGHT, padx=6)

        # Health badge indicator (Section 26)
        self.lbl_health_badge = ttk.Label(right_box, text="✓ Healthy", style="Success.TLabel", cursor="hand2")
        self.lbl_health_badge.pack(side=tk.RIGHT, padx=8)
        self.lbl_health_badge.bind("<Button-1>", lambda e: self._select_tab(7))  # Open Diagnostics

    # -------------------------------------------------------------
    # 2. Tab 1: Dashboard (Section 7)
    # -------------------------------------------------------------

    def _build_dashboard_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Dashboard ")

        # Status & Stat Cards Frame
        status_box = ttk.LabelFrame(tab, text="Workspace Status", padding=12)
        status_box.pack(fill=tk.X, pady=(0, 10))

        # Top line in status box: Overall condition
        top_stat = ttk.Frame(status_box)
        top_stat.pack(fill=tk.X, pady=(0, 8))
        self.dash_status_lbl = ttk.Label(top_stat, text="✓ Ready for Operation", font=("Segoe UI", 11, "bold"))
        self.dash_status_lbl.pack(side=tk.LEFT)
        self.dash_current_desktop_lbl = ttk.Label(top_stat, text="Current: Desktop 1", style="SubHeader.TLabel")
        self.dash_current_desktop_lbl.pack(side=tk.RIGHT)

        # 4 Stat Cards Grid
        grid_frame = ttk.Frame(status_box)
        grid_frame.pack(fill=tk.X, pady=6)
        for i in range(4):
            grid_frame.columnconfigure(i, weight=1)

        self.card_dt = self._create_stat_card(grid_frame, 0, "Desktops", "0")
        self.card_apps = self._create_stat_card(grid_frame, 1, "Configured Apps", "0")
        self.card_running = self._create_stat_card(grid_frame, 2, "Running Apps", "0")
        self.card_warnings = self._create_stat_card(grid_frame, 3, "Missing / Warnings", "0")

        # Quick Actions Bar (Section 34)
        act_box = ttk.LabelFrame(tab, text="Quick Actions", padding=10)
        act_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(act_box, text="▶ Launch Workspace", style="Primary.TButton", width=18, command=self._on_launch_clicked).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(act_box, text="⟳ Sync Workspace", width=16, command=self._on_sync_clicked).pack(side=tk.LEFT, padx=4)
        ttk.Button(act_box, text="🔍 Dry Run", width=12, command=self._on_dry_run_clicked).pack(side=tk.LEFT, padx=4)
        ttk.Button(act_box, text="↻ Refresh", width=10, command=self._refresh_all_views).pack(side=tk.LEFT, padx=4)

        ttk.Button(act_box, text="+ Add Application", width=16, command=lambda: self._open_add_app_dialog()).pack(side=tk.RIGHT, padx=4)
        ttk.Button(act_box, text="+ Add Desktop", width=14, command=self._on_add_desktop_clicked).pack(side=tk.RIGHT, padx=4)

        # Workspace Overview Container
        overview_box = ttk.LabelFrame(tab, text="Active Workspace Overview", padding=10)
        overview_box.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        canvas = tk.Canvas(overview_box, bg=self.palette["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(overview_box, orient=tk.VERTICAL, command=canvas.yview)
        self.overview_content = ttk.Frame(canvas)

        self.overview_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.overview_content, anchor=tk.NW, width=980)
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Recent Activity Footer Card
        self.dash_activity_frame = ttk.Frame(tab, padding=6)
        self.dash_activity_frame.pack(fill=tk.X)
        self.dash_activity_lbl = ttk.Label(self.dash_activity_frame, text="Recent Activity: None recorded yet.", style="Muted.TLabel")
        self.dash_activity_lbl.pack(side=tk.LEFT)
        ttk.Button(self.dash_activity_frame, text="View History", command=lambda: self._select_tab(5)).pack(side=tk.RIGHT)

    def _create_stat_card(self, parent: ttk.Frame, col: int, title: str, initial_val: str) -> ttk.Label:
        box = ttk.Frame(parent, padding=8, relief="ridge")
        box.grid(row=0, column=col, sticky="nsew", padx=4)
        ttk.Label(box, text=title, style="Muted.TLabel").pack(anchor=tk.W)
        val_lbl = ttk.Label(box, text=initial_val, font=("Segoe UI", 14, "bold"))
        val_lbl.pack(anchor=tk.W, pady=(2, 0))
        return val_lbl

    # -------------------------------------------------------------
    # 3. Tab 2: Workspaces Editor (Section 15)
    # -------------------------------------------------------------

    def _build_workspaces_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Workspaces ")

        # Header toolbar
        tb = ttk.Frame(tab)
        tb.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(tb, text="Configure Workspace Desktops and Application Assignments", style="SubHeader.TLabel").pack(side=tk.LEFT)
        ttk.Button(tb, text="+ Add Desktop", command=self._on_add_desktop_clicked).pack(side=tk.RIGHT, padx=4)
        ttk.Button(tb, text="+ Add Application", style="Primary.TButton", command=lambda: self._open_add_app_dialog()).pack(side=tk.RIGHT, padx=4)

        # Scrollable desktop cards container
        cards_box = ttk.Frame(tab)
        cards_box.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(cards_box, bg=self.palette["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(cards_box, orient=tk.VERTICAL, command=canvas.yview)
        self.workspace_cards_frame = ttk.Frame(canvas)

        self.workspace_cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.workspace_cards_frame, anchor=tk.NW, width=980)
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # -------------------------------------------------------------
    # 4. Tab 3: Applications View (Section 21)
    # -------------------------------------------------------------

    def _build_applications_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Applications ")

        # Search & Filter Toolbar (Section 21)
        filter_bar = ttk.Frame(tab)
        filter_bar.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_bar, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.app_search_var = tk.StringVar()
        self.app_search_entry = ttk.Entry(filter_bar, textvariable=self.app_search_var, width=22)
        self.app_search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.app_search_entry.bind("<KeyRelease>", lambda e: self._refresh_applications_view())

        ttk.Label(filter_bar, text="Desktop:").pack(side=tk.LEFT, padx=(0, 4))
        self.app_desktop_filter_var = tk.StringVar(value="All")
        self.app_desktop_combo = ttk.Combobox(filter_bar, textvariable=self.app_desktop_filter_var, state="readonly", width=14)
        self.app_desktop_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.app_desktop_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_applications_view())

        ttk.Label(filter_bar, text="Status:").pack(side=tk.LEFT, padx=(0, 4))
        self.app_status_filter_var = tk.StringVar(value="All")
        status_choices = ["All", "Running", "Stopped", "Missing Executable"]
        self.app_status_combo = ttk.Combobox(filter_bar, textvariable=self.app_status_filter_var, values=status_choices, state="readonly", width=16)
        self.app_status_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.app_status_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_applications_view())

        ttk.Button(filter_bar, text="Clear Filters", command=self._clear_app_filters).pack(side=tk.LEFT, padx=4)

        self.lbl_app_count = ttk.Label(filter_bar, text="", style="Muted.TLabel")
        self.lbl_app_count.pack(side=tk.RIGHT, padx=4)
        ttk.Button(filter_bar, text="+ Add Application", command=lambda: self._open_add_app_dialog()).pack(side=tk.RIGHT, padx=4)

        cols = ("status", "name", "desktop", "monitor", "snap", "mode", "policy", "executable")
        self.app_tree = ttk.Treeview(tab, columns=cols, show="headings", height=16)
        self.app_tree.heading("status", text="Status")
        self.app_tree.heading("name", text="Application Name")
        self.app_tree.heading("desktop", text="Assigned Desktop")
        self.app_tree.heading("monitor", text="Monitor")
        self.app_tree.heading("snap", text="Layout Snap")
        self.app_tree.heading("mode", text="Launch Mode")
        self.app_tree.heading("policy", text="Window Policy")
        self.app_tree.heading("executable", text="Executable Path")

        self.app_tree.column("status", width=80, anchor=tk.CENTER)
        self.app_tree.column("name", width=170)
        self.app_tree.column("desktop", width=130)
        self.app_tree.column("monitor", width=80, anchor=tk.CENTER)
        self.app_tree.column("snap", width=100, anchor=tk.CENTER)
        self.app_tree.column("mode", width=120)
        self.app_tree.column("policy", width=120)
        self.app_tree.column("executable", width=260)

        tree_scroll = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.app_tree.yview)
        self.app_tree.configure(yscrollcommand=tree_scroll.set)

        self.app_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, before=self.app_tree)

        # Action button bar below table
        action_bar = ttk.Frame(tab, padding=(0, 8))
        action_bar.pack(fill=tk.X)

        ttk.Button(action_bar, text="Edit Application", command=self._on_table_edit_app).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Move to Desktop...", command=self._on_table_reassign_app).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="🔍 Test Match (Diagnostic)", command=self._on_table_test_match).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Remove from Workspace", command=self._on_table_remove_app).pack(side=tk.LEFT, padx=4)

    def _clear_app_filters(self) -> None:
        self.app_search_var.set("")
        self.app_desktop_filter_var.set("All")
        self.app_status_filter_var.set("All")
        self._refresh_applications_view()

    # -------------------------------------------------------------
    # 5. Tab 4: Virtual Desktops Mapping (Section 18)
    # -------------------------------------------------------------

    def _build_virtual_desktops_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Virtual Desktops ")

        desc_box = ttk.Frame(tab)
        desc_box.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(desc_box, text="Windows Virtual Desktop Mapping & State Verification", style="SubHeader.TLabel").pack(anchor=tk.W)
        ttk.Label(desc_box, text="Inspects identity, existence, and current active desktop index. Mappings require review if state changes.", style="Muted.TLabel").pack(anchor=tk.W)

        # Table
        cols = ("ws_desktop", "win_desktop", "status", "active", "apps_assigned")
        self.dt_tree = ttk.Treeview(tab, columns=cols, show="headings", height=12)
        self.dt_tree.heading("ws_desktop", text="Workspace Desktop")
        self.dt_tree.heading("win_desktop", text="Windows Desktop Target")
        self.dt_tree.heading("status", text="Existence / Identity")
        self.dt_tree.heading("active", text="Current Indicator")
        self.dt_tree.heading("apps_assigned", text="Assigned Applications")

        self.dt_tree.column("ws_desktop", width=200)
        self.dt_tree.column("win_desktop", width=180)
        self.dt_tree.column("status", width=160)
        self.dt_tree.column("active", width=140, anchor=tk.CENTER)
        self.dt_tree.column("apps_assigned", width=240)

        self.dt_tree.pack(fill=tk.BOTH, expand=True)

        btn_bar = ttk.Frame(tab, padding=(0, 8))
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="↻ Refresh Desktops", command=self._refresh_virtual_desktops_view).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Switch to Selected Desktop", command=self._on_table_switch_desktop).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="+ Create Missing Desktop", command=self._on_add_desktop_clicked).pack(side=tk.LEFT, padx=4)

    # -------------------------------------------------------------
    # 6. Tab 5: Execution & Plan (Sections 13 & 14)
    # -------------------------------------------------------------

    def _build_execution_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Execution & Plan ")

        # Plan Review & Mode
        plan_box = ttk.LabelFrame(tab, text="Review Execution Plan (Section 13)", padding=10)
        plan_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.plan_text = tk.Text(plan_box, wrap=tk.WORD, font=("Consolas", 9), height=14, padx=8, pady=8)
        self.plan_text.pack(fill=tk.BOTH, expand=True)

        plan_actions = ttk.Frame(plan_box)
        plan_actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(plan_actions, text="🔍 Update / Review Dry Run Plan", command=self._load_execution_plan_preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(plan_actions, text="▶ Run Workspace", style="Primary.TButton", command=self._on_launch_clicked).pack(side=tk.RIGHT, padx=4)
        ttk.Button(plan_actions, text="⟳ Sync Workspace", command=self._on_sync_clicked).pack(side=tk.RIGHT, padx=4)

        # Live Execution Task Progress (Section 14)
        live_box = ttk.LabelFrame(tab, text="Live Task Progress (Section 14)", padding=10)
        live_box.pack(fill=tk.X)

        self.live_task_lbl = ttk.Label(live_box, text="No operation in flight.", font=("Segoe UI", 9, "bold"))
        self.live_task_lbl.pack(anchor=tk.W, pady=(0, 4))
        self.progress_bar = ttk.Progressbar(live_box, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 6))

    def _load_execution_plan_preview(self) -> None:
        dry_result = self.manager.dry_run()
        self.plan_text.configure(state=tk.NORMAL)
        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, dry_result.format_preview())
        self.plan_text.configure(state=tk.DISABLED)

    # -------------------------------------------------------------
    # 7. Tab 6: Operation History (Section 29)
    # -------------------------------------------------------------

    def _build_history_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" History ")

        top_bar = ttk.Frame(tab)
        top_bar.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(top_bar, text="Audit Log & Operation History (Section 29)", style="SubHeader.TLabel").pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Clear History", command=self._on_clear_history_clicked).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top_bar, text="↻ Refresh", command=self._refresh_history_view).pack(side=tk.RIGHT, padx=4)

        # History Table
        cols = ("time", "profile", "op", "result", "duration", "op_id")
        self.hist_tree = ttk.Treeview(tab, columns=cols, show="headings", height=10)
        self.hist_tree.heading("time", text="Timestamp")
        self.hist_tree.heading("profile", text="Profile")
        self.hist_tree.heading("op", text="Operation")
        self.hist_tree.heading("result", text="Result")
        self.hist_tree.heading("duration", text="Duration")
        self.hist_tree.heading("op_id", text="Operation ID")

        self.hist_tree.column("time", width=160)
        self.hist_tree.column("profile", width=140)
        self.hist_tree.column("op", width=120)
        self.hist_tree.column("result", width=120)
        self.hist_tree.column("duration", width=100)
        self.hist_tree.column("op_id", width=220)

        self.hist_tree.pack(fill=tk.BOTH, expand=True)
        self.hist_tree.bind("<<TreeviewSelect>>", self._on_history_selected)

        # Selected History Details Card
        self.hist_details_box = ttk.LabelFrame(tab, text="Operation Details", padding=10)
        self.hist_details_box.pack(fill=tk.X, pady=(10, 0))

        self.hist_details_text = tk.Text(self.hist_details_box, wrap=tk.WORD, height=6, font=("Consolas", 9))
        self.hist_details_text.pack(fill=tk.X, expand=True, pady=(0, 6))

        h_btn_bar = ttk.Frame(self.hist_details_box)
        h_btn_bar.pack(fill=tk.X)
        ttk.Button(h_btn_bar, text="Copy Operation ID", command=self._copy_selected_op_id).pack(side=tk.LEFT, padx=4)
        ttk.Button(h_btn_bar, text="Rerun as Dry Run", command=self._on_dry_run_clicked).pack(side=tk.LEFT, padx=4)

    def _on_history_selected(self, _event=None) -> None:
        sel = self.hist_tree.selection()
        if not sel:
            return
        records = self.manager.get_operation_history()
        idx = int(sel[0])
        if 0 <= idx < len(records):
            rec = records[idx]
            self.hist_details_text.configure(state=tk.NORMAL)
            self.hist_details_text.delete("1.0", tk.END)
            self.hist_details_text.insert(tk.END, f"Operation: {rec.operation_type} | Profile: {rec.profile_name} | ID: {rec.operation_id}\n")
            self.hist_details_text.insert(tk.END, f"Result: {rec.result} | Duration: {rec.duration_seconds}s | Desktops: {rec.desktops_found}/{rec.desktops_target} | Apps: {rec.apps_count}\n\n")
            self.hist_details_text.insert(tk.END, rec.summary)
            self.hist_details_text.configure(state=tk.DISABLED)

    def _copy_selected_op_id(self) -> None:
        sel = self.hist_tree.selection()
        if not sel:
            return
        records = self.manager.get_operation_history()
        idx = int(sel[0])
        if 0 <= idx < len(records):
            op_id = records[idx].operation_id
            self.clipboard_clear()
            self.clipboard_append(op_id)
            messagebox.showinfo("Copied", f"Operation ID '{op_id}' copied to clipboard.", parent=self)

    def _on_clear_history_clicked(self) -> None:
        if messagebox.askyesno("Clear History", "Clear all recorded operation history?", parent=self):
            self.manager.clear_operation_history()
            self._refresh_history_view()

    # -------------------------------------------------------------
    # 8. Tab 7: Logs (Sections 28 & 51)
    # -------------------------------------------------------------

    def _build_logs_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Logs ")

        self.log_panel = LogViewPanel(
            tab,
            diagnostics_service=self.diagnostics_service,
            palette=self.palette
        )
        self.log_panel.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------
    # 9. Tab 8: Diagnostics & Recovery (Sections 27, 46, 60)
    # -------------------------------------------------------------

    def _build_diagnostics_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Diagnostics ")

        # Top Bar
        tb = ttk.Frame(tab)
        tb.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(tb, text="System Diagnostics, Health Categories, & Recovery", style="SubHeader.TLabel").pack(side=tk.LEFT)

        ttk.Button(tb, text="📦 Generate Support Bundle", style="Primary.TButton", command=self._on_generate_support_bundle).pack(side=tk.RIGHT, padx=4)
        ttk.Button(tb, text="📋 Copy Report", command=self._on_copy_diag_report).pack(side=tk.RIGHT, padx=4)
        ttk.Button(tb, text="🩺 Run Health Check", command=self._on_run_health_check).pack(side=tk.RIGHT, padx=4)

        # 10 Categories Container
        cat_box = ttk.LabelFrame(tab, text="Subsystem Categories (Section 27)", padding=10)
        cat_box.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        canvas = tk.Canvas(cat_box, bg=self.palette["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(cat_box, orient=tk.VERTICAL, command=canvas.yview)
        self.diag_cards_frame = ttk.Frame(canvas)

        self.diag_cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.diag_cards_frame, anchor=tk.NW, width=980)
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # -------------------------------------------------------------
    # 10. Tab 9: Settings (Sections 30 & 31)
    # -------------------------------------------------------------

    def _build_settings_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text=" Settings ")

        head = ttk.Frame(tab)
        head.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(head, text="Preferences & Guardrails", style="SubHeader.TLabel").pack(side=tk.LEFT)
        ttk.Button(head, text="Open Full Settings Dialog", command=self._open_settings_dialog).pack(side=tk.RIGHT)

        card = ttk.LabelFrame(tab, text="Quick Settings Overview", padding=16)
        card.pack(fill=tk.BOTH, expand=True)

        items = [
            ("Theme Preference:", self.manager.config.general.theme),
            ("Minimize to System Tray:", str(self.manager.config.general.minimize_to_tray)),
            ("Confirm Before Execution:", str(self.manager.config.general.confirm_before_execution)),
            ("Automation Enabled:", str(self.manager.config.safety.automation_enabled)),
            ("Dry Run by Default:", str(self.manager.config.safety.dry_run_default)),
            ("Logging Level:", self.manager.config.logging.log_level),
            ("Log Retention Days:", f"{self.manager.config.logging.log_retention_days} days"),
            ("Default Window Timeout:", f"{self.manager.config.execution.window_timeout_ms} ms"),
        ]

        for k, v in items:
            r = ttk.Frame(card)
            r.pack(fill=tk.X, pady=4)
            ttk.Label(r, text=k, width=28, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(r, text=v, style="Muted.TLabel").pack(side=tk.LEFT)

    # -------------------------------------------------------------
    # 11. Tab 10: About
    # -------------------------------------------------------------

    def _build_about_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(tab, text=" About ")

        ttk.Label(tab, text="Virtual Desktop Workspace Manager", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(tab, text=f"Version {__version__} — Production Release 2.0", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 12))

        info_box = ttk.LabelFrame(tab, text="Architecture & Runtime Details", padding=12)
        info_box.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        items = [
            ("Operating System:", f"{platform.system()} {platform.release()} (Build {platform.version()})"),
            ("Python Runtime:", f"{sys.version.split()[0]} ({platform.architecture()[0]})"),
            ("Virtual Desktop Provider:", getattr(self.manager.desktop_provider, "name", self.manager.desktop_provider.__class__.__name__)),
            ("Process Provider:", getattr(self.manager.process_provider, "name", self.manager.process_provider.__class__.__name__)),
            ("Window Provider:", getattr(self.manager.window_provider, "name", self.manager.window_provider.__class__.__name__)),
            ("License:", "MIT License"),
            ("Offline Mode:", "100% Offline (Zero External Network Requests)"),
            ("Integrity Level:", "Standard User (Medium Integrity)"),
        ]

        for k, v in items:
            r = ttk.Frame(info_box)
            r.pack(fill=tk.X, pady=3)
            ttk.Label(r, text=k, width=26, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(r, text=v, style="Muted.TLabel").pack(side=tk.LEFT)

        sc_box = ttk.LabelFrame(tab, text="Keyboard Shortcuts Reference", padding=10)
        sc_box.pack(fill=tk.X)

        scs = [
            ("Ctrl+S", "Save configuration changes"),
            ("Ctrl+R / F5", "Refresh all detections & views"),
            ("Ctrl+F", "Switch to Applications tab and focus search"),
            ("Ctrl+L", "Switch to Logs tab"),
            ("Ctrl+,", "Switch to Settings tab"),
            ("Esc", "Close modal / cancel search filter"),
        ]
        for key, desc in scs:
            r = ttk.Frame(sc_box)
            r.pack(fill=tk.X, pady=1)
            ttk.Label(r, text=key, width=16, font=("Consolas", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(r, text=desc, style="Muted.TLabel").pack(side=tk.LEFT)

    # -------------------------------------------------------------
    # Status Bar
    # -------------------------------------------------------------

    def _build_status_bar(self) -> None:
        self.status_bar = ttk.Frame(self, relief="sunken", padding=(10, 3))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = ttk.Label(self.status_bar, text="Ready", style="Muted.TLabel")
        self.lbl_status.pack(side=tk.LEFT)

        self.lbl_dirty_status = ttk.Label(self.status_bar, text="", foreground="#b25900", font=("Segoe UI", 8, "bold"))
        self.lbl_dirty_status.pack(side=tk.LEFT, padx=16)

        prov_name = getattr(self.manager.desktop_provider, "name", self.manager.desktop_provider.__class__.__name__)
        self.lbl_provider_info = ttk.Label(self.status_bar, text=f"Provider: {prov_name}", style="Muted.TLabel")
        self.lbl_provider_info.pack(side=tk.RIGHT)

    # -------------------------------------------------------------
    # Refresh & Rendering Handlers
    # -------------------------------------------------------------

    def _refresh_all_views(self) -> None:
        # Update Profiles combo
        profiles = self.manager.config.profiles
        names = [p.name for p in profiles]
        self.profile_combo.configure(values=names)
        active_prof = self.manager.config.get_active_profile()
        if active_prof.name in names:
            self.profile_combo.current(names.index(active_prof.name))

        # Update Health badge
        self._update_health_badge()

        # Update Current Desktop
        curr_dt = self.manager.get_current_desktop_number()
        total_dt = self.manager.get_desktop_count()
        dt_name = ""
        for d in active_prof.desktops:
            if d.number == curr_dt:
                dt_name = f" — {d.name}"
                break
        self.dash_current_desktop_lbl.configure(text=f"Current: Desktop {curr_dt}{dt_name}")

        # Refresh each tab
        self._refresh_dashboard(active_prof, curr_dt, total_dt)
        self._refresh_workspaces_view(active_prof, curr_dt)
        self._refresh_applications_view()
        self._refresh_virtual_desktops_view()
        self._refresh_history_view()
        self._refresh_diagnostics_view()

    def _update_health_badge(self) -> None:
        checks = self.diagnostics_service.run_health_check()
        all_ok = all(c["ok"] for c in checks.values())
        if all_ok:
            self.lbl_health_badge.configure(text="✓ Healthy", style="Success.TLabel")
        else:
            self.lbl_health_badge.configure(text="⚠ Attention Needed", style="Warning.TLabel")

    def _refresh_dashboard(self, profile: WorkspaceProfile, current_dt: int, total_dt: int) -> None:
        configured_count = len(profile.apps)
        running_count = 0
        missing_count = 0

        for a in profile.apps:
            exe, _ = self.manager.app_detector.detect_executable(a)
            if not exe:
                missing_count += 1
            cand = list(a.process_names)
            if exe:
                cand.append(os.path.basename(exe))
            if self.manager.process_provider.get_running_processes_matching(cand):
                running_count += 1

        self.card_dt.configure(text=str(total_dt))
        self.card_apps.configure(text=str(configured_count))
        self.card_running.configure(text=str(running_count))
        self.card_warnings.configure(text=str(missing_count))

        if missing_count > 0:
            self.dash_status_lbl.configure(text=f"⚠ {missing_count} Application(s) Missing or Need Attention")
        else:
            self.dash_status_lbl.configure(text="✓ Workspace Ready & Configured")

        # Render Overview cards
        for child in self.overview_content.winfo_children():
            child.destroy()

        desktops = sorted(profile.desktops, key=lambda d: d.number)
        if not desktops:
            ttk.Label(self.overview_content, text="No desktops configured.", style="Muted.TLabel").pack(pady=10)
            return

        for dt in desktops:
            is_active = (dt.number == current_dt)
            card = ttk.LabelFrame(self.overview_content, text=f"Desktop {dt.number} — {dt.name}" + (" [ACTIVE]" if is_active else ""), padding=8)
            card.pack(fill=tk.X, pady=4, padx=2)

            apps = profile.get_apps_for_desktop(dt.number)
            if not apps:
                ttk.Label(card, text="  No applications assigned.", style="Muted.TLabel").pack(anchor=tk.W)
            else:
                row = ttk.Frame(card)
                row.pack(fill=tk.X)
                for app in apps:
                    exe, _ = self.manager.app_detector.detect_executable(app)
                    icon = "✓" if exe else "⚠"
                    fg_style = "Success.TLabel" if exe else "Warning.TLabel"
                    badge = ttk.Frame(row, padding=(4, 2))
                    badge.pack(side=tk.LEFT, padx=4)
                    ttk.Label(badge, text=f"{icon} {app.name}", style=fg_style).pack()

        # Update Recent Activity
        records = self.manager.get_operation_history(limit=1)
        if records:
            r = records[0]
            self.dash_activity_lbl.configure(text=f"Recent Activity: Last {r.operation_type} at {r.time_str} • {r.result} ({r.duration_seconds}s)")
        else:
            self.dash_activity_lbl.configure(text="Recent Activity: No workspace operations recorded yet.")

    def _refresh_workspaces_view(self, profile: WorkspaceProfile, current_dt: int) -> None:
        for child in self.workspace_cards_frame.winfo_children():
            child.destroy()

        desktops = sorted(profile.desktops, key=lambda d: d.number)
        if not desktops:
            ttk.Label(self.workspace_cards_frame, text="No virtual desktops configured. Click '+ Add Desktop' to start.", style="Muted.TLabel").pack(pady=20)
            return

        for dt in desktops:
            is_active = (dt.number == current_dt)
            card_title = f"Desktop {dt.number} — {dt.name}" + ("  [ACTIVE]" if is_active else "")
            card = ttk.LabelFrame(self.workspace_cards_frame, text=card_title, padding=10)
            card.pack(fill=tk.X, pady=6, padx=4)

            # Toolbar
            header_bar = ttk.Frame(card)
            header_bar.pack(fill=tk.X, pady=(0, 6))

            ttk.Button(header_bar, text="Open Desktop", width=13, command=lambda n=dt.number: self._open_desktop(n)).pack(side=tk.LEFT, padx=2)
            ttk.Button(header_bar, text="Rename", width=8, command=lambda d=dt: self._rename_desktop(d)).pack(side=tk.LEFT, padx=2)
            ttk.Button(header_bar, text="+ Add App", width=10, command=lambda n=dt.number: self._open_add_app_dialog(target_desktop=n)).pack(side=tk.LEFT, padx=2)

            apps = profile.get_apps_for_desktop(dt.number)
            if not apps:
                ttk.Label(card, text="  No applications assigned to this desktop.", style="Muted.TLabel").pack(anchor=tk.W, pady=4)
            else:
                apps_box = ttk.Frame(card)
                apps_box.pack(fill=tk.X, pady=4)
                for app in apps:
                    self._render_workspace_app_row(apps_box, app)

    def _render_workspace_app_row(self, parent: ttk.Frame, app: AppConfig) -> None:
        row = ttk.Frame(parent, padding=(4, 2))
        row.pack(fill=tk.X, pady=2)

        exe, _ = self.manager.app_detector.detect_executable(app)
        cand = list(app.process_names)
        if exe:
            cand.append(os.path.basename(exe))
        is_running = len(self.manager.process_provider.get_running_processes_matching(cand)) > 0

        if not exe:
            icon = "⚠"
            style = "Warning.TLabel"
            tip = "Executable not found"
        elif is_running:
            icon = "✓"
            style = "Success.TLabel"
            tip = "Running"
        else:
            icon = "○"
            style = "Muted.TLabel"
            tip = "Stopped"

        ttk.Label(row, text=icon, style=style, width=3).pack(side=tk.LEFT)
        ttk.Label(row, text=app.name, font=("Segoe UI", 9, "bold"), width=22).pack(side=tk.LEFT)
        ttk.Label(row, text=f"({tip} | {app.window_policy})", style="Muted.TLabel", width=22).pack(side=tk.LEFT)

        actions_bar = ttk.Frame(row)
        actions_bar.pack(side=tk.RIGHT)

        ttk.Button(actions_bar, text="Move to...", width=9, command=lambda a=app: self._show_reassign_dialog(a)).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_bar, text="Edit", width=6, command=lambda a=app: self._open_edit_app_dialog(a)).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_bar, text="Test Match", width=10, command=lambda a=app: self._test_match_app_dialog(a)).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_bar, text="Remove", width=8, command=lambda a=app: self._confirm_remove_app(a)).pack(side=tk.LEFT, padx=2)

    def _refresh_applications_view(self) -> None:
        for item in self.app_tree.get_children():
            self.app_tree.delete(item)

        profile = self.manager.config.get_active_profile()

        # Update desktop filter choices
        dt_names = ["All"] + [f"Desktop {d.number} — {d.name}" for d in profile.desktops]
        self.app_desktop_combo.configure(values=dt_names)

        query = self.app_search_var.get().strip().lower()
        dt_filter = self.app_desktop_filter_var.get()
        status_filter = self.app_status_filter_var.get()

        displayed = 0
        for app in profile.apps:
            # Name / exe filter
            if query and (query not in app.name.lower() and query not in app.executable.lower()):
                continue

            # Desktop filter
            if dt_filter != "All" and f"Desktop {app.desktop}" not in dt_filter:
                continue

            exe, _ = self.manager.app_detector.detect_executable(app)
            cand = list(app.process_names)
            if exe:
                cand.append(os.path.basename(exe))
            is_running = len(self.manager.process_provider.get_running_processes_matching(cand)) > 0

            # Status filter
            if status_filter == "Running" and not is_running:
                continue
            elif status_filter == "Stopped" and is_running:
                continue
            elif status_filter == "Missing Executable" and exe:
                continue

            if not exe:
                stat_str = "⚠ Missing"
            elif is_running:
                stat_str = "✓ Running"
            else:
                stat_str = "○ Stopped"

            dt_name = next((d.name for d in profile.desktops if d.number == app.desktop), f"Desktop {app.desktop}")

            snap_label = getattr(app, "window_snap", "default").replace("_", " ").title()
            mon_label = f"Mon {getattr(app, 'monitor_index', 0)}"

            self.app_tree.insert(
                "",
                tk.END,
                iid=app.id,
                values=(
                    stat_str,
                    app.name,
                    f"Desktop {app.desktop} ({dt_name})",
                    mon_label,
                    snap_label,
                    app.launch_mode,
                    app.window_policy,
                    app.executable
                )
            )
            displayed += 1

        self.lbl_app_count.configure(text=f"Showing {displayed} of {len(profile.apps)} apps")

    def _refresh_virtual_desktops_view(self) -> None:
        for item in self.dt_tree.get_children():
            self.dt_tree.delete(item)

        profile = self.manager.config.get_active_profile()
        current_dt = self.manager.get_current_desktop_number()
        total_dt = self.manager.get_desktop_count()

        for d in sorted(profile.desktops, key=lambda x: x.number):
            exists = d.number <= total_dt
            status_txt = "✓ Exists on Windows" if exists else "⚠ Not Created Yet"
            active_txt = "[CURRENT ACTIVE]" if d.number == current_dt else ""
            apps = [a.name for a in profile.get_apps_for_desktop(d.number)]
            apps_txt = ", ".join(apps) if apps else "(None)"

            self.dt_tree.insert(
                "",
                tk.END,
                iid=str(d.number),
                values=(f"Workspace Desktop: {d.name}", f"Desktop {d.number}", status_txt, active_txt, apps_txt)
            )

    def _refresh_history_view(self) -> None:
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)

        records = self.manager.get_operation_history(limit=50)
        for i, r in enumerate(records):
            self.hist_tree.insert(
                "",
                tk.END,
                iid=str(i),
                values=(r.time_str, r.profile_name, r.operation_type, r.result, f"{r.duration_seconds}s", r.operation_id)
            )

    def _refresh_diagnostics_view(self) -> None:
        for child in self.diag_cards_frame.winfo_children():
            child.destroy()

        categories = self.diagnostics_service.run_categorized_diagnostics()
        for cat_name, cat_data in categories.items():
            status = cat_data.get("status", "Passed")
            icon = "✓" if status == "Passed" else ("⚠" if status == "Warning" else "✕")
            box = ttk.LabelFrame(self.diag_cards_frame, text=f"{icon} {cat_name} — {status}", padding=8)
            box.pack(fill=tk.X, pady=4, padx=4)

            for item in cat_data.get("items", []):
                r = ttk.Frame(box)
                r.pack(fill=tk.X, pady=1)
                ttk.Label(r, text=f"• {item['name']}:", width=24, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
                ttk.Label(r, text=item["value"], style="Muted.TLabel").pack(side=tk.LEFT)

    # -------------------------------------------------------------
    # Unsaved Changes Tracking (Section 23)
    # -------------------------------------------------------------

    def _mark_dirty(self) -> None:
        self.is_dirty = True
        self.lbl_dirty_status.configure(text="● Unsaved Changes (Ctrl+S)")
        self.btn_save_changes.configure(state=tk.NORMAL)

    def _save_changes(self) -> None:
        try:
            self.manager.save_config()
            self.is_dirty = False
            self.lbl_dirty_status.configure(text="")
            self.btn_save_changes.configure(state=tk.DISABLED)
            self.lbl_status.configure(text="Configuration saved successfully.")
            self._refresh_all_views()
        except Exception as ex:
            messagebox.showerror("Save Error", f"Failed to save configuration: {ex}", parent=self)

    def _check_unsaved_changes(self) -> bool:
        """Returns True if user chose to proceed, False if action was cancelled."""
        if not self.is_dirty:
            return True
        msg = "You have unsaved configuration changes.\n\nWould you like to save them now?"
        resp = messagebox.askyesnocancel("Unsaved Changes", msg, parent=self)
        if resp is True:
            self._save_changes()
            return True
        elif resp is False:
            self.is_dirty = False
            self.lbl_dirty_status.configure(text="")
            self.btn_save_changes.configure(state=tk.DISABLED)
            return True
        return False  # Cancelled

    # -------------------------------------------------------------
    # Execution & Sync Operations (Sections 12, 13, 14)
    # -------------------------------------------------------------

    def _on_launch_clicked(self) -> None:
        if self.manager.config.safety.dry_run_default:
            self._on_dry_run_clicked()
            return

        active_prof = self.manager.config.get_active_profile()
        if self.manager.config.safety.require_confirmation and self.manager.config.general.confirm_before_execution:
            ConfirmationDialog(
                self,
                f"Run '{active_prof.name}' Workspace?\n\nThis may launch missing applications and assign windows to Virtual Desktops.\nNo processes will be killed.",
                on_confirm=lambda: self._execute_operation(is_sync=False),
                on_cancel=lambda: self.logger.info("Workspace Launch Cancelled by user")
            )
        else:
            self._execute_operation(is_sync=False)

    def _on_sync_clicked(self) -> None:
        active_prof = self.manager.config.get_active_profile()
        if self.manager.config.safety.require_confirmation and self.manager.config.general.confirm_before_execution:
            ConfirmationDialog(
                self,
                f"Sync '{active_prof.name}' Workspace?\n\nThis will reconcile window positions without launching new applications.",
                on_confirm=lambda: self._execute_operation(is_sync=True),
                on_cancel=lambda: self.logger.info("Workspace Sync Cancelled by user")
            )
        else:
            self._execute_operation(is_sync=True)

    def _on_dry_run_clicked(self) -> None:
        self._select_tab(4)  # Switch to Execution tab
        self._load_execution_plan_preview()

    def _execute_operation(self, is_sync: bool) -> None:
        self.btn_stop.configure(state=tk.NORMAL)
        op_title = "Syncing" if is_sync else "Launching"
        self.lbl_status.configure(text=f"Operation in progress: {op_title} workspace...")
        self.live_task_lbl.configure(text=f"Running {op_title} workspace...")
        self.progress_bar.start(10)

        def event_listener(evt):
            self.after(0, lambda: self.live_task_lbl.configure(text=f"→ {evt.message}"))

        def run_thread():
            try:
                if is_sync:
                    report = self.manager.sync_workspace(event_callback=event_listener)
                else:
                    report = self.manager.launch_workspace(event_callback=event_listener)

                self.after(0, self._on_operation_completed, report)
            except Exception as ex:
                self.logger.error(f"Execution error: {ex}")
                self.after(0, lambda: messagebox.showerror("Execution Failure", str(ex), parent=self))
                self.after(0, self._reset_op_buttons)

        thread = threading.Thread(target=run_thread, daemon=True)
        thread.start()

    def _on_operation_completed(self, report) -> None:
        self._reset_op_buttons()
        self.progress_bar.stop()
        self.lbl_status.configure(text=f"Workspace {report.operation_type} completed in {report.duration_seconds}s")
        self.live_task_lbl.configure(text=f"✓ Workspace {report.operation_type} finished ({report.duration_seconds}s)")
        self._refresh_all_views()
        messagebox.showinfo("Operation Summary", report.summary_text(), parent=self)

    def _on_stop_clicked(self) -> None:
        self.logger.info("Workspace Operation Cancelled (Emergency STOP)")
        self.manager.stop_current_operation()
        self.btn_stop.configure(state=tk.DISABLED)
        self.lbl_status.configure(text="Cancellation requested...")

    def _reset_op_buttons(self) -> None:
        self.btn_stop.configure(state=tk.DISABLED)
        self.progress_bar.stop()

    # -------------------------------------------------------------
    # Application & Desktop Actions
    # -------------------------------------------------------------

    def _open_desktop(self, desktop_number: int) -> None:
        success = self.manager.switch_to_desktop(desktop_number)
        if success:
            self.lbl_status.configure(text=f"Switched view to Desktop {desktop_number}")
            self._refresh_all_views()
        else:
            messagebox.showwarning("Desktop Switch", f"Could not switch to Desktop {desktop_number}.", parent=self)

    def _rename_desktop(self, dt: DesktopConfig) -> None:
        new_name = simpledialog.askstring("Rename Desktop", f"Enter new name for Desktop {dt.number}:", initialvalue=dt.name, parent=self)
        if new_name is not None and new_name.strip():
            self.manager.rename_desktop(dt.number, new_name.strip())
            self._mark_dirty()
            self._refresh_all_views()

    def _on_add_desktop_clicked(self) -> None:
        name = simpledialog.askstring("Add Desktop", "Enter custom name for new desktop:", parent=self)
        if name is not None:
            self.manager.add_desktop(name.strip())
            self._mark_dirty()
            self._refresh_all_views()

    def _open_add_app_dialog(self, target_desktop: int = 1) -> None:
        app = AppConfig(desktop=target_desktop)
        AppDialog(
            parent=self,
            app=app,
            desktops=self.manager.config.get_active_profile().desktops,
            running_discoverer=self.running_discoverer,
            on_save=lambda new_app: self._on_app_added(new_app),
            test_match_callback=self.manager.test_match_app
        )

    def _on_app_added(self, app: AppConfig) -> None:
        self.manager.add_app_to_profile(app)
        self._mark_dirty()
        self._refresh_all_views()

    def _open_edit_app_dialog(self, app: AppConfig) -> None:
        AppDialog(
            parent=self,
            app=app,
            desktops=self.manager.config.get_active_profile().desktops,
            running_discoverer=self.running_discoverer,
            on_save=lambda updated_app: self._on_app_updated(updated_app),
            test_match_callback=self.manager.test_match_app
        )

    def _on_app_updated(self, app: AppConfig) -> None:
        self.manager.update_app_in_profile(app)
        self._mark_dirty()
        self._refresh_all_views()

    def _show_reassign_dialog(self, app: AppConfig) -> None:
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
            self.manager.reassign_app(app.id, new_target)
            self._mark_dirty()

            if move_now_var.get():
                moved = self.manager.move_running_window_now(app.id, new_target)
                if moved:
                    messagebox.showinfo("Window Moved", f"Moved running window for '{app.name}' to Desktop {new_target}.", parent=top)

            top.destroy()
            self._refresh_all_views()

        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(btn_bar, text="Cancel", command=top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_bar, text="Save", style="Primary.TButton", command=save_reassign).pack(side=tk.RIGHT, padx=4)

    def _confirm_remove_app(self, app: AppConfig) -> None:
        msg = (
            f"Remove '{app.name}' from Desktop {app.desktop}?\n\n"
            "This will NOT uninstall the application.\n"
            "It only removes its workspace configuration."
        )
        if messagebox.askokcancel("Confirm Remove", msg, parent=self):
            self.manager.remove_app_from_profile(app.id)
            self._mark_dirty()
            self._refresh_all_views()

    def _test_match_app_dialog(self, app: AppConfig) -> None:
        """Section 43: Diagnostic-only test matching tool."""
        results = self.manager.test_match_app(app)
        top = tk.Toplevel(self)
        top.title(f"Test Match: {app.name}")
        top.geometry("600x400")
        top.transient(self)
        top.grab_set()

        frame = ttk.Frame(top, padding=14)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Window Match Evaluation — {app.name}", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 4))
        rule_desc = f"Rule: Exe='{os.path.basename(app.executable)}' | Policy='{app.window_policy}'"
        if app.title_pattern:
            rule_desc += f" | Title='{app.title_pattern}'"
        ttk.Label(frame, text=rule_desc, style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 8))

        if not results:
            box = ttk.LabelFrame(frame, text="Results", padding=16)
            box.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
            ttk.Label(box, text="○ No active windows or running processes match this rule currently.", font=("Segoe UI", 10)).pack(pady=16)
        else:
            box = ttk.LabelFrame(frame, text=f"Matches ({len(results)} found)", padding=8)
            box.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

            tree = ttk.Treeview(box, columns=("conf", "pid", "hwnd", "dt", "title"), show="headings", height=8)
            tree.heading("conf", text="Confidence")
            tree.heading("pid", text="PID")
            tree.heading("hwnd", text="HWND")
            tree.heading("dt", text="Current Desktop")
            tree.heading("title", text="Window Title")
            tree.column("conf", width=80)
            tree.column("pid", width=60)
            tree.column("hwnd", width=80)
            tree.column("dt", width=100)
            tree.column("title", width=240)
            tree.pack(fill=tk.BOTH, expand=True)

            for r in results:
                tree.insert("", tk.END, values=(r["confidence"], r["pid"], r["hwnd"], r["desktop"], r["title"]))

        ttk.Label(frame, text="Note: Read-only diagnostic test; no windows were moved.", style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 6))
        ttk.Button(frame, text="Close", command=top.destroy).pack(side=tk.RIGHT)

    # -------------------------------------------------------------
    # Table Context Action Handlers
    # -------------------------------------------------------------

    def _get_selected_app(self) -> Optional[AppConfig]:
        sel = self.app_tree.selection()
        if not sel:
            messagebox.showinfo("Select Application", "Please select an application row first.", parent=self)
            return None
        app_id = sel[0]
        profile = self.manager.config.get_active_profile()
        return next((a for a in profile.apps if a.id == app_id), None)

    def _on_table_edit_app(self) -> None:
        app = self._get_selected_app()
        if app:
            self._open_edit_app_dialog(app)

    def _on_table_reassign_app(self) -> None:
        app = self._get_selected_app()
        if app:
            self._show_reassign_dialog(app)

    def _on_table_test_match(self) -> None:
        app = self._get_selected_app()
        if app:
            self._test_match_app_dialog(app)

    def _on_table_remove_app(self) -> None:
        app = self._get_selected_app()
        if app:
            self._confirm_remove_app(app)

    def _on_table_switch_desktop(self) -> None:
        sel = self.dt_tree.selection()
        if not sel:
            messagebox.showinfo("Select Desktop", "Please select a desktop row first.", parent=self)
            return
        dt_num = int(sel[0])
        self._open_desktop(dt_num)

    # -------------------------------------------------------------
    # Profile Switching & Operations (Section 25)
    # -------------------------------------------------------------

    def _on_profile_switched(self, _event=None) -> None:
        if not self._check_unsaved_changes():
            return
        sel_idx = self.profile_combo.current()
        if 0 <= sel_idx < len(self.manager.config.profiles):
            chosen = self.manager.config.profiles[sel_idx]
            self.manager.config.general.active_profile_id = chosen.id
            self.manager.save_config()
            self._refresh_all_views()

    def _add_new_profile(self) -> None:
        if not self._check_unsaved_changes():
            return
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

    def _duplicate_profile(self) -> None:
        if not self._check_unsaved_changes():
            return
        active_prof = self.manager.config.get_active_profile()
        name = simpledialog.askstring("Duplicate Profile", f"Enter name for copy of '{active_prof.name}':", initialvalue=f"{active_prof.name} Copy", parent=self)
        if name and name.strip():
            import uuid
            new_data = active_prof.to_dict()
            new_data["id"] = str(uuid.uuid4())[:8]
            new_data["name"] = name.strip()
            new_prof = WorkspaceProfile.from_dict(new_data)
            self.manager.config.profiles.append(new_prof)
            self.manager.config.general.active_profile_id = new_prof.id
            self.manager.save_config()
            self._refresh_all_views()

    def _export_profile(self) -> None:
        prof = self.manager.config.get_active_profile()
        target = filedialog.asksaveasfilename(
            parent=self,
            title=f"Export Profile '{prof.name}'",
            defaultextension=".vdwm",
            filetypes=[("Workspace Bundles", "*.vdwm"), ("JSON Files", "*.json")],
            initialfile=f"{prof.name.lower().replace(' ', '_')}.vdwm"
        )
        if target:
            from tkinter import simpledialog
            from app.services.profile_sharing import ProfileSharingService
            passcode = simpledialog.askstring(
                "Encrypt Profile (Optional)",
                "Enter a passcode to encrypt this profile for secure team sharing\n(leave blank for plain export):",
                parent=self,
                show="*"
            )
            sharing = ProfileSharingService()
            sharing.export_profile(prof, Path(target), passcode=passcode or None)
            enc_msg = " (Encrypted with passcode)" if passcode else ""
            messagebox.showinfo("Exported", f"Profile exported successfully to:\n{target}{enc_msg}", parent=self)

    def _import_profile(self) -> None:
        if not self._check_unsaved_changes():
            return
        source = filedialog.askopenfilename(
            parent=self,
            title="Import Workspace Profile",
            filetypes=[("Workspace Bundles & JSON", "*.vdwm;*.json"), ("All Files", "*.*")]
        )
        if source:
            try:
                from tkinter import simpledialog
                from app.services.profile_sharing import ProfileSharingService
                sharing = ProfileSharingService()

                # Check if file is encrypted
                with open(source, "r", encoding="utf-8") as f:
                    content_preview = f.read(200)

                passcode = None
                if "vdwm_encrypted" in content_preview:
                    passcode = simpledialog.askstring(
                        "Encrypted Profile Bundle",
                        "This profile bundle is passcode-protected.\nPlease enter the passcode to decrypt:",
                        parent=self,
                        show="*"
                    )
                    if not passcode:
                        return

                prof = sharing.import_profile(Path(source), passcode=passcode)
                existing = [p for p in self.manager.config.profiles if p.id == prof.id]
                if existing:
                    import uuid
                    prof.id = str(uuid.uuid4())[:8]
                self.manager.config.profiles.append(prof)
                self.manager.config.general.active_profile_id = prof.id
                self.manager.save_config()
                self._refresh_all_views()
                messagebox.showinfo("Imported", f"Profile '{prof.name}' successfully imported and activated!", parent=self)
            except Exception as ex:
                messagebox.showerror("Import Error", f"Failed to import profile: {ex}", parent=self)

    # -------------------------------------------------------------
    # Diagnostics & Support Bundle Actions (Sections 27, 60)
    # -------------------------------------------------------------

    def _on_run_health_check(self) -> None:
        summary_text = self.diagnostics_service.format_health_check_summary()
        self._refresh_diagnostics_view()
        messagebox.showinfo("Health Check Results", summary_text, parent=self)

    def _on_copy_diag_report(self) -> None:
        report = self.diagnostics_service.generate_report()
        self.clipboard_clear()
        self.clipboard_append(report)
        messagebox.showinfo("Copied", "Sanitized diagnostic report copied to clipboard.", parent=self)

    def _on_generate_support_bundle(self) -> None:
        target = filedialog.asksaveasfilename(
            parent=self,
            title="Export Diagnostic Support Bundle (ZIP)",
            defaultextension=".zip",
            filetypes=[("ZIP Archive", "*.zip")],
            initialfile=f"vdwm_support_bundle_{time.strftime('%Y%m%d_%H%M%S')}.zip"
        )
        if target:
            try:
                res = self.support_bundle_service.generate_bundle(Path(target))
                msg = f"Support bundle generated successfully!\n\nLocation: {target}\nSize: {res['size_bytes']} bytes\nFiles: {len(res['files_included'])} files"
                messagebox.showinfo("Support Bundle Ready", msg, parent=self)
            except Exception as ex:
                messagebox.showerror("Export Failed", f"Failed to generate support bundle: {ex}", parent=self)

    def _check_crash_recovery(self) -> None:
        marker = self.manager.config_store.check_incomplete_operation()
        if marker:
            msg = (
                f"Notice: A previous workspace operation ('{marker.get('operation')}') "
                f"started at {marker.get('time_str')} may not have completed cleanly.\n\n"
                "Would you like to run 'Sync Workspace' now to reconcile your state?"
            )
            if messagebox.askyesno("Crash Recovery (Section 46)", msg, parent=self):
                self._execute_operation(is_sync=True)
            self.manager.config_store.clear_operation_marker()

    def _open_setup_wizard(self) -> None:
        SetupWizardDialog(
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
            on_save=lambda _: [self._mark_dirty(), self._refresh_all_views()]
        )

    def _on_auto_toggle(self) -> None:
        active = self.auto_toggle_var.get()
        self.manager.config.safety.automation_enabled = active
        self._mark_dirty()
        status_txt = "Active" if active else "Paused"
        self.lbl_status.configure(text=f"Automation {status_txt}")

    # -------------------------------------------------------------
    # Close & Exit
    # -------------------------------------------------------------

    def _on_close_requested(self) -> None:
        if not self._check_unsaved_changes():
            return
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
        if not self._check_unsaved_changes():
            return
        self.tray_manager.stop()
        self.destroy()
