"""
Settings dialog matching Section 59 specifications.
"""

from __future__ import annotations
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from app.models.workspace import WorkspaceConfig
from app.services.startup_service import StartupService
from app.logging.logger import get_default_log_dir


class SettingsDialog(tk.Toplevel):
    """Configuration dialog for manager options."""

    def __init__(
        self,
        parent: tk.Widget,
        config: WorkspaceConfig,
        on_save: Optional[Callable[[WorkspaceConfig], None]] = None
    ):
        super().__init__(parent)
        self.title("Workspace Manager Settings")
        self.geometry("540x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.config = config
        self.on_save = on_save
        self.startup_service = StartupService()

        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        # --- Tab 1: General ---
        tab_general = ttk.Frame(notebook, padding=12)
        notebook.add(tab_general, text="General")

        ttk.Label(tab_general, text="Windows Startup & Automation", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 8))

        self.start_win_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab_general,
            text="Start Workspace Manager with Windows",
            variable=self.start_win_var
        ).pack(anchor=tk.W, pady=4)

        self.auto_launch_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab_general,
            text="Automatically launch configured workspace on startup (requires above)",
            variable=self.auto_launch_var
        ).pack(anchor=tk.W, pady=4)

        self.confirm_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab_general,
            text="Always show confirmation prompt before executing workspace",
            variable=self.confirm_var
        ).pack(anchor=tk.W, pady=4)

        self.min_tray_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab_general,
            text="Minimize to system tray when closing window",
            variable=self.min_tray_var
        ).pack(anchor=tk.W, pady=4)

        self.start_min_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab_general,
            text="Start application minimized",
            variable=self.start_min_var
        ).pack(anchor=tk.W, pady=4)

        ttk.Separator(tab_general, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12)

        theme_row = ttk.Frame(tab_general)
        theme_row.pack(fill=tk.X, pady=4)
        ttk.Label(theme_row, text="UI Theme:").pack(side=tk.LEFT, padx=(0, 8))
        self.theme_var = tk.StringVar(value="System")
        self.theme_combo = ttk.Combobox(theme_row, textvariable=self.theme_var, values=["System", "Light", "Dark"], state="readonly", width=12)
        self.theme_combo.pack(side=tk.LEFT)

        ttk.Separator(tab_general, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12)

        # Desktop Shortcuts Section
        ttk.Label(tab_general, text="User Desktop Shortcuts", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(
            tab_general,
            text="Manage the 2 official shortcuts: 'Configure' (opens GUI) and 'Run Workspace' (executes active profile).",
            wraplength=480,
            foreground="#666666"
        ).pack(anchor=tk.W, pady=(0, 6))

        sc_row = ttk.Frame(tab_general)
        sc_row.pack(fill=tk.X, pady=4)
        ttk.Button(sc_row, text="Create Desktop Shortcuts", command=self._create_desktop_shortcuts).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(sc_row, text="Remove Owned Shortcuts", command=self._remove_desktop_shortcuts).pack(side=tk.LEFT)

        # --- Tab 2: Execution & Timing ---
        tab_exec = ttk.Frame(notebook, padding=12)
        notebook.add(tab_exec, text="Execution")

        ttk.Label(tab_exec, text="Timing & Polling Thresholds", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 8))

        grid_exec = ttk.Frame(tab_exec)
        grid_exec.pack(fill=tk.X, pady=4)

        ttk.Label(grid_exec, text="Window Ready Timeout (ms):").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.timeout_var = tk.IntVar()
        ttk.Entry(grid_exec, textvariable=self.timeout_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=8)

        ttk.Label(grid_exec, text="Window Polling Interval (ms):").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.poll_var = tk.IntVar()
        ttk.Entry(grid_exec, textvariable=self.poll_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=8)

        ttk.Label(grid_exec, text="Launch Delay between Apps (ms):").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.delay_var = tk.IntVar()
        ttk.Entry(grid_exec, textvariable=self.delay_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=8)

        ttk.Label(grid_exec, text="Retry Count for Move Failures:").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.retry_var = tk.IntVar()
        ttk.Entry(grid_exec, textvariable=self.retry_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=8)

        # --- Tab 3: Logging & Diagnostics ---
        tab_log = ttk.Frame(notebook, padding=12)
        notebook.add(tab_log, text="Logging")

        log_grid = ttk.Frame(tab_log)
        log_grid.pack(fill=tk.X, pady=4)

        ttk.Label(log_grid, text="Log Level:").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.log_level_var = tk.StringVar(value="INFO")
        self.log_level_combo = ttk.Combobox(log_grid, textvariable=self.log_level_var, values=["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR"], state="readonly", width=12)
        self.log_level_combo.grid(row=0, column=1, sticky=tk.W, padx=8)

        ttk.Label(log_grid, text="Log File Retention (days):").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.retention_var = tk.IntVar(value=14)
        ttk.Entry(log_grid, textvariable=self.retention_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=8)

        ttk.Button(tab_log, text="Open Logs Directory", command=self._open_logs_dir).pack(anchor=tk.W, pady=12)

        # --- Tab 4: Safety Guards ---
        tab_safety = ttk.Frame(notebook, padding=12)
        notebook.add(tab_safety, text="Safety")

        ttk.Label(tab_safety, text="Safety & Guardrails", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 8))

        self.auto_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab_safety,
            text="Automation Globally Enabled (Uncheck to pause all launches and moves)",
            variable=self.auto_enabled_var
        ).pack(anchor=tk.W, pady=4)

        self.dry_run_def_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab_safety,
            text="Default to Dry-Run Mode on launch buttons",
            variable=self.dry_run_def_var
        ).pack(anchor=tk.W, pady=4)

        guards_frame = ttk.LabelFrame(tab_safety, text="Strict Production Guarantees", padding=8)
        guards_frame.pack(fill=tk.X, pady=12)
        ttk.Label(guards_frame, text="✓ Never kill processes automatically (ENFORCED)", style="Success.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(guards_frame, text="✓ Never delete user virtual desktops (ENFORCED)", style="Success.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(guards_frame, text="✓ Never delete user files or repositories (ENFORCED)", style="Success.TLabel").pack(anchor=tk.W, pady=2)

        # Bottom buttons
        btn_bar = ttk.Frame(main_frame)
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_bar, text="Save Settings", style="Primary.TButton", command=self._save).pack(side=tk.RIGHT, padx=4)

    def _load_values(self) -> None:
        g = self.config.general
        self.start_win_var.set(g.start_with_windows)
        self.auto_launch_var.set(g.auto_launch_workspace)
        self.confirm_var.set(g.confirm_before_execution)
        self.min_tray_var.set(g.minimize_to_tray)
        self.start_min_var.set(g.start_minimized)
        self.theme_var.set(g.theme)

        e = self.config.execution
        self.timeout_var.set(e.window_timeout_ms)
        self.poll_var.set(e.polling_interval_ms)
        self.delay_var.set(e.launch_delay_ms)
        self.retry_var.set(e.retry_count)

        l = self.config.logging
        self.log_level_var.set(l.log_level)
        self.retention_var.set(l.log_retention_days)

        s = self.config.safety
        self.auto_enabled_var.set(s.automation_enabled)
        self.dry_run_def_var.set(s.dry_run_default)

    def _open_logs_dir(self) -> None:
        log_dir = get_default_log_dir()
        if os.name == "nt":
            os.startfile(str(log_dir))
        else:
            subprocess.Popen(["explorer", str(log_dir)])

    def _create_desktop_shortcuts(self) -> None:
        from app.services.shortcut_service import ShortcutService
        from tkinter import messagebox
        svc = ShortcutService()
        res = svc.create_desktop_shortcuts()
        if res.get("config") and res.get("run"):
            messagebox.showinfo(
                "Shortcuts Created",
                "Created 2 Desktop shortcuts successfully:\n\n"
                "• Virtual Desktop Workspace Manager — Configure\n"
                "• Virtual Desktop Workspace Manager — Run Workspace",
                parent=self
            )
        else:
            messagebox.showwarning("Warning", "Failed to create some shortcuts.", parent=self)

    def _remove_desktop_shortcuts(self) -> None:
        from app.services.shortcut_service import ShortcutService
        from tkinter import messagebox
        if messagebox.askyesno(
            "Remove Shortcuts",
            "Remove the 2 application Desktop shortcuts?\n\n(Unrelated user shortcuts will remain untouched)",
            parent=self
        ):
            svc = ShortcutService()
            svc.remove_desktop_shortcuts()
            messagebox.showinfo("Shortcuts Removed", "Owned Desktop shortcuts removed cleanly.", parent=self)


    def _save(self) -> None:
        # Update config object
        g = self.config.general
        prev_start_with_win = g.start_with_windows
        g.start_with_windows = self.start_win_var.get()
        g.auto_launch_workspace = self.auto_launch_var.get()
        g.confirm_before_execution = self.confirm_var.get()
        g.minimize_to_tray = self.min_tray_var.get()
        g.start_minimized = self.start_min_var.get()
        g.theme = self.theme_var.get()

        e = self.config.execution
        e.window_timeout_ms = max(1000, self.timeout_var.get())
        e.polling_interval_ms = max(50, self.poll_var.get())
        e.launch_delay_ms = max(0, self.delay_var.get())
        e.retry_count = max(0, self.retry_var.get())

        l = self.config.logging
        l.log_level = self.log_level_var.get()
        l.log_retention_days = max(1, self.retention_var.get())

        s = self.config.safety
        s.automation_enabled = self.auto_enabled_var.get()
        s.dry_run_default = self.dry_run_def_var.get()

        # Update startup registry if changed
        if g.start_with_windows != prev_start_with_win or g.start_with_windows:
            if g.start_with_windows:
                self.startup_service.enable_startup(auto_launch=g.auto_launch_workspace)
            else:
                self.startup_service.disable_startup()

        if self.on_save:
            self.on_save(self.config)

        self.destroy()
