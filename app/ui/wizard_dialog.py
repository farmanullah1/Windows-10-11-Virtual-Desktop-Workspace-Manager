"""
First-Run Setup Wizard matching Section 78 specifications.
8-step wizard:
Step 1: Welcome
Step 2: Detect Virtual Desktops
Step 3: Configure Desktops
Step 4: Detect Applications
Step 5: Assign Applications
Step 6: Review
Step 7: Save Configuration
Step 8: Completion (Strictly does NOT launch automatically)
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from app.models.workspace import WorkspaceConfig, WorkspaceProfile, DesktopConfig, AppConfig
from app.providers.base import IVirtualDesktopProvider, IProcessProvider, IWindowProvider
from app.discovery.app_detector import AppDetector
from app.discovery.running_apps import RunningAppDiscoverer
from app.configuration.config_store import ConfigStore


class SetupWizardDialog(tk.Toplevel):
    """8-step setup wizard for first-time configuration."""

    def __init__(
        self,
        parent: tk.Widget,
        config: WorkspaceConfig,
        desktop_provider: IVirtualDesktopProvider,
        process_provider: IProcessProvider,
        window_provider: IWindowProvider,
        app_detector: AppDetector,
        config_store: ConfigStore,
        on_completed: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.title("Workspace Manager — Setup Wizard")
        self.geometry("620x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.config = config
        self.profile = config.get_active_profile()
        self.desktop_provider = desktop_provider
        self.process_provider = process_provider
        self.window_provider = window_provider
        self.app_detector = app_detector
        self.config_store = config_store
        self.on_completed = on_completed

        self.current_step = 1
        self.total_steps = 8

        self._build_shell()
        self._show_step(1)

    def _build_shell(self) -> None:
        # Top banner
        banner = ttk.Frame(self, padding=16)
        banner.pack(fill=tk.X)
        self.step_label = ttk.Label(banner, text="Step 1 of 8", style="Muted.TLabel")
        self.step_label.pack(anchor=tk.W)
        self.title_label = ttk.Label(banner, text="Welcome", style="Header.TLabel")
        self.title_label.pack(anchor=tk.W, pady=(2, 0))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Content area
        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Navigation Bar
        nav_bar = ttk.Frame(self, padding=12)
        nav_bar.pack(fill=tk.X)

        self.btn_cancel = ttk.Button(nav_bar, text="Cancel", command=self.destroy)
        self.btn_cancel.pack(side=tk.LEFT)

        self.btn_next = ttk.Button(nav_bar, text="Next >", style="Primary.TButton", command=self._next_step)
        self.btn_next.pack(side=tk.RIGHT, padx=4)

        self.btn_prev = ttk.Button(nav_bar, text="< Back", command=self._prev_step)
        self.btn_prev.pack(side=tk.RIGHT, padx=4)

    def _clear_content(self) -> None:
        for child in self.content_frame.winfo_children():
            child.destroy()

    def _show_step(self, step: int) -> None:
        self.current_step = step
        self.step_label.configure(text=f"Step {step} of {self.total_steps}")
        self._clear_content()

        self.btn_prev.configure(state=tk.NORMAL if step > 1 else tk.DISABLED)
        self.btn_next.configure(text="Finish" if step == 8 else "Next >")

        if step == 1:
            self._render_step_1_welcome()
        elif step == 2:
            self._render_step_2_detect_desktops()
        elif step == 3:
            self._render_step_3_configure_desktops()
        elif step == 4:
            self._render_step_4_detect_apps()
        elif step == 5:
            self._render_step_5_assign_apps()
        elif step == 6:
            self._render_step_6_review()
        elif step == 7:
            self._render_step_7_save()
        elif step == 8:
            self._render_step_8_completion()

    # Step 1: Welcome
    def _render_step_1_welcome(self) -> None:
        self.title_label.configure(text="Welcome to Virtual Desktop Workspace Manager")
        ttk.Label(self.content_frame, text=(
            "This wizard will help you configure your Windows Virtual Desktop workspace.\n\n"
            "Key Benefits:\n"
            "• Organize your development, browser, database, and API tools into dedicated desktops.\n"
            "• Automatically move application windows to their designated virtual spaces.\n"
            "• Fully safe: Never terminates processes, never deletes user desktops or files.\n"
            "• Persistent configuration that restores on your demand.\n\n"
            "Click 'Next' to begin detecting your current Windows desktops."
        ), wraplength=540, font=("Segoe UI", 10)).pack(anchor=tk.W, pady=8)

    # Step 2: Detect Desktops
    def _render_step_2_detect_desktops(self) -> None:
        self.title_label.configure(text="Step 2 — Detect Virtual Desktops")
        count = self.desktop_provider.get_desktop_count()
        curr = self.desktop_provider.get_current_desktop_number()

        ttk.Label(self.content_frame, text=f"Windows Virtual Desktop System Detected:", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(self.content_frame, text=f"• Available Virtual Desktops: {count}", style="Success.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(self.content_frame, text=f"• Current Active Desktop: Desktop {curr}").pack(anchor=tk.W, pady=2)

        ttk.Label(self.content_frame, text=(
            "\nThe default workspace uses 4 desktops (Browser, Development, Database, API Development).\n"
            "If your system currently has fewer than 4 desktops, the manager will safely create them "
            "only when you run the workspace."
        ), wraplength=540).pack(anchor=tk.W, pady=12)

    # Step 3: Configure Desktops
    def _render_step_3_configure_desktops(self) -> None:
        self.title_label.configure(text="Step 3 — Configure Desktops")
        ttk.Label(self.content_frame, text="Customize the names for your virtual desktops:").pack(anchor=tk.W, pady=(0, 10))

        grid = ttk.Frame(self.content_frame)
        grid.pack(fill=tk.X)

        self.desktop_name_vars: List[tk.StringVar] = []
        for i, dt in enumerate(self.profile.desktops):
            ttk.Label(grid, text=f"Desktop {dt.number}:", font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky=tk.W, pady=4, padx=(0, 8))
            v = tk.StringVar(value=dt.name)
            self.desktop_name_vars.append(v)
            ttk.Entry(grid, textvariable=v, width=32).grid(row=i, column=1, sticky=tk.W, pady=4)

    # Step 4: Detect Applications
    def _render_step_4_detect_apps(self) -> None:
        self.title_label.configure(text="Step 4 — Detect Installed Applications")
        ttk.Label(self.content_frame, text="Scanning configured tools on your computer:").pack(anchor=tk.W, pady=(0, 10))

        list_box = ttk.Frame(self.content_frame)
        list_box.pack(fill=tk.BOTH, expand=True)

        for i, app in enumerate(self.profile.apps):
            resolved, src = self.app_detector.detect_executable(app)
            status_icon = "✓ Found" if resolved else "⚠ Not Located"
            status_style = "Success.TLabel" if resolved else "Warning.TLabel"
            row = ttk.Frame(list_box)
            row.pack(fill=tk.X, pady=4)
            ttk.Label(row, text=f"{app.name}:", width=30, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(row, text=status_icon, style=status_style).pack(side=tk.LEFT, padx=6)
            if resolved:
                ttk.Label(row, text=f"({src})", style="Muted.TLabel").pack(side=tk.LEFT)

    # Step 5: Assign Applications
    def _render_step_5_assign_apps(self) -> None:
        self.title_label.configure(text="Step 5 — Application Assignments")
        ttk.Label(self.content_frame, text="Assign which desktop each application belongs to:").pack(anchor=tk.W, pady=(0, 10))

        grid = ttk.Frame(self.content_frame)
        grid.pack(fill=tk.X)

        self.app_desktop_vars: List[tk.IntVar] = []
        for i, app in enumerate(self.profile.apps):
            ttk.Label(grid, text=app.name, width=28, font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky=tk.W, pady=4)
            v = tk.IntVar(value=app.desktop)
            self.app_desktop_vars.append(v)
            choices = [f"Desktop {d.number} — {d.name}" for d in self.profile.desktops]
            cb = ttk.Combobox(grid, values=choices, state="readonly", width=30)
            cb.grid(row=i, column=1, sticky=tk.W, pady=4)
            # Find index
            for idx, d in enumerate(self.profile.desktops):
                if d.number == app.desktop:
                    cb.current(idx)
                    break
            cb.bind("<<ComboboxSelected>>", lambda e, idx=i, combo=cb: self._update_app_desktop_assignment(idx, combo))

    def _update_app_desktop_assignment(self, app_idx: int, combo: ttk.Combobox) -> None:
        sel_idx = combo.current()
        if 0 <= sel_idx < len(self.profile.desktops):
            self.profile.apps[app_idx].desktop = self.profile.desktops[sel_idx].number

    # Step 6: Review
    def _render_step_6_review(self) -> None:
        self.title_label.configure(text="Step 6 — Review Workspace Setup")
        ttk.Label(self.content_frame, text="Summary of configured layout:", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 8))

        summary_box = ttk.Frame(self.content_frame)
        summary_box.pack(fill=tk.BOTH, expand=True)

        for d in self.profile.desktops:
            card = ttk.LabelFrame(summary_box, text=f"Desktop {d.number}: {d.name}", padding=6)
            card.pack(fill=tk.X, pady=4)
            apps = self.profile.get_apps_for_desktop(d.number)
            if apps:
                app_names = ", ".join(a.name for a in apps)
                ttk.Label(card, text=f"Applications: {app_names}").pack(anchor=tk.W)
            else:
                ttk.Label(card, text="(No applications assigned)", style="Muted.TLabel").pack(anchor=tk.W)

    # Step 7: Save Configuration
    def _render_step_7_save(self) -> None:
        self.title_label.configure(text="Step 7 — Save Configuration")
        try:
            self.config.general.first_run_completed = True
            self.config_store.save(self.config)
            ttk.Label(self.content_frame, text="✓ Configuration successfully saved!", style="Success.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=12)
            ttk.Label(self.content_frame, text=(
                f"Saved to: {self.config_store.config_file}\n"
                "Automatic backup created in workspace.backup.json.\n\n"
                "Click 'Next' to complete setup."
            )).pack(anchor=tk.W)
        except Exception as ex:
            ttk.Label(self.content_frame, text=f"Error saving configuration: {ex}", style="Error.TLabel").pack(anchor=tk.W)

    # Step 8: Ready (Section 78 requirement: Strictly DO NOT launch automatically)
    def _render_step_8_completion(self) -> None:
        self.title_label.configure(text="Step 8 — Workspace Configuration Completed")
        ttk.Label(self.content_frame, text=(
            "Setup is complete!\n\n"
            "As requested, no applications or desktops were automatically modified.\n\n"
            "When you are ready, use the 'Launch Workspace' or 'Dry Run' button on the main dashboard.\n\n"
            "Click 'Finish' to open the manager."
        ), font=("Segoe UI", 10), wraplength=540).pack(anchor=tk.W, pady=16)

    def _next_step(self) -> None:
        # Save step 3 entries if on step 3
        if self.current_step == 3:
            for i, v in enumerate(self.desktop_name_vars):
                if i < len(self.profile.desktops):
                    self.profile.desktops[i].name = v.get().strip() or f"Desktop {i+1}"

        if self.current_step < self.total_steps:
            self._show_step(self.current_step + 1)
        else:
            self.destroy()
            if self.on_completed:
                self.on_completed()

    def _prev_step(self) -> None:
        if self.current_step > 1:
            self._show_step(self.current_step - 1)
