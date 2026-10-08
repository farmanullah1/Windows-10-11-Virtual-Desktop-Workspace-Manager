"""
Application Add/Edit dialog with validation, templates, and running app picker.
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Callable
from app.models.workspace import AppConfig, LaunchMode, WindowPolicy, WindowSnap, DesktopConfig
from app.discovery.app_templates import APPLICATION_TEMPLATES, AppTemplate
from app.discovery.running_apps import RunningAppDiscoverer, RunningAppInfo
from app.configuration.validator import ConfigValidator


class AppDialog(tk.Toplevel):
    """Dialog for creating or editing an application configuration."""

    def __init__(
        self,
        parent: tk.Widget,
        app: Optional[AppConfig] = None,
        desktops: Optional[List[DesktopConfig]] = None,
        running_discoverer: Optional[RunningAppDiscoverer] = None,
        on_save: Optional[Callable[[AppConfig], None]] = None,
        test_match_callback: Optional[Callable[[AppConfig], List[dict]]] = None
    ):
        super().__init__(parent)
        self.title("Configure Application" if app else "Add Application to Workspace")
        self.geometry("540x680")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.app = app or AppConfig()
        self.desktops = desktops or [DesktopConfig(number=1, name="Desktop 1")]
        self.running_discoverer = running_discoverer
        self.on_save = on_save
        self.test_match_callback = test_match_callback

        self._build_ui()
        self._populate_fields()

    def _build_ui(self) -> None:
        pad_opts = {"padx": 16, "pady": 6}

        main_frame = ttk.Frame(self, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Quick Assist bar (Templates / Detect)
        assist_frame = ttk.LabelFrame(main_frame, text="Quick Setup & Discovery", padding=8)
        assist_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(assist_frame, text="Template:").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.template_var = tk.StringVar()
        template_names = ["(Select Template...)"] + [t.name for t in APPLICATION_TEMPLATES]
        self.template_combo = ttk.Combobox(assist_frame, textvariable=self.template_var, values=template_names, state="readonly", width=22)
        self.template_combo.current(0)
        self.template_combo.grid(row=0, column=1, padx=4)
        self.template_combo.bind("<<ComboboxSelected>>", self._on_template_selected)

        if self.running_discoverer:
            btn_detect = ttk.Button(assist_frame, text="Detect Running...", command=self._show_running_apps_picker)
            btn_detect.grid(row=0, column=2, padx=4)

        # Form fields
        form = ttk.Frame(main_frame)
        form.pack(fill=tk.BOTH, expand=True)

        # Name
        ttk.Label(form, text="Application Name:*").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=42).grid(row=0, column=1, sticky=tk.W, pady=4)

        # Executable
        ttk.Label(form, text="Executable Path:").grid(row=1, column=0, sticky=tk.W, pady=4)
        exe_frame = ttk.Frame(form)
        exe_frame.grid(row=1, column=1, sticky=tk.W, pady=4)
        self.exe_var = tk.StringVar()
        self.exe_entry = ttk.Entry(exe_frame, textvariable=self.exe_var, width=32)
        self.exe_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.exe_entry.bind("<KeyRelease>", self._validate_path_live)
        ttk.Button(exe_frame, text="Browse...", width=9, command=self._browse_exe).pack(side=tk.LEFT)

        # Path Status Label
        self.path_status_lbl = ttk.Label(form, text="", font=("Segoe UI", 8))
        self.path_status_lbl.grid(row=2, column=1, sticky=tk.W)

        # Arguments
        ttk.Label(form, text="Arguments:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.args_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.args_var, width=42).grid(row=3, column=1, sticky=tk.W, pady=4)

        # Target Desktop
        ttk.Label(form, text="Target Desktop:*").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.desktop_var = tk.IntVar(value=1)
        desktop_choices = [f"Desktop {d.number} — {d.name}" for d in self.desktops]
        self.desktop_combo = ttk.Combobox(form, values=desktop_choices, state="readonly", width=38)
        self.desktop_combo.grid(row=4, column=1, sticky=tk.W, pady=4)

        # Launch Mode
        ttk.Label(form, text="Launch Mode:").grid(row=5, column=0, sticky=tk.W, pady=4)
        self.launch_mode_var = tk.StringVar(value=LaunchMode.LAUNCH_IF_MISSING.value)
        modes = [
            ("Launch if not running", LaunchMode.LAUNCH_IF_MISSING.value),
            ("Always launch new instance", LaunchMode.ALWAYS_LAUNCH.value),
            ("Reuse existing instance only", LaunchMode.REUSE_ONLY.value),
        ]
        mode_frame = ttk.Frame(form)
        mode_frame.grid(row=5, column=1, sticky=tk.W, pady=4)
        for text, val in modes:
            ttk.Radiobutton(mode_frame, text=text, value=val, variable=self.launch_mode_var).pack(anchor=tk.W)

        # Checkboxes
        check_frame = ttk.Frame(form)
        check_frame.grid(row=6, column=1, sticky=tk.W, pady=6)
        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="Enabled in workspace", variable=self.enabled_var).pack(anchor=tk.W)
        self.move_win_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="Move existing window to target desktop", variable=self.move_win_var).pack(anchor=tk.W)

        # Window Matching Policy
        ttk.Label(form, text="Window Policy:").grid(row=7, column=0, sticky=tk.W, pady=4)
        self.policy_var = tk.StringVar(value=WindowPolicy.MAIN_ONLY.value)
        policies = [
            ("Move main window only", WindowPolicy.MAIN_ONLY.value),
            ("Move all matching windows", WindowPolicy.ALL_MATCHING.value),
            ("Match window title contains...", WindowPolicy.TITLE_CONTAINS.value),
            ("Match window title regex...", WindowPolicy.TITLE_REGEX.value),
        ]
        self.policy_combo = ttk.Combobox(form, values=[p[0] for p in policies], state="readonly", width=38)
        self.policy_combo.grid(row=7, column=1, sticky=tk.W, pady=4)
        self._policy_map = {p[0]: p[1] for p in policies}
        self._reverse_policy_map = {p[1]: p[0] for p in policies}

        # Title Pattern
        ttk.Label(form, text="Title Pattern:").grid(row=8, column=0, sticky=tk.W, pady=4)
        self.title_pattern_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_pattern_var, width=42).grid(row=8, column=1, sticky=tk.W, pady=4)

        # Target Monitor
        ttk.Label(form, text="Target Monitor:").grid(row=9, column=0, sticky=tk.W, pady=4)
        monitor_options = [
            "Monitor 0 (Primary Display)",
            "Monitor 1 (Secondary Display)",
            "Monitor 2",
            "Monitor 3",
        ]
        self.monitor_combo = ttk.Combobox(form, values=monitor_options, state="readonly", width=38)
        self.monitor_combo.current(0)
        self.monitor_combo.grid(row=9, column=1, sticky=tk.W, pady=4)

        # Layout / Tiling Snap
        ttk.Label(form, text="Layout / Tiling:").grid(row=10, column=0, sticky=tk.W, pady=4)
        snap_options = [
            ("Default (Preserve Geometry)", WindowSnap.DEFAULT.value),
            ("Maximize (Fullscreen)", WindowSnap.MAXIMIZE.value),
            ("Minimize", WindowSnap.MINIMIZE.value),
            ("Snap Left Half (50%)", WindowSnap.LEFT_HALF.value),
            ("Snap Right Half (50%)", WindowSnap.RIGHT_HALF.value),
            ("Snap Top Half (50%)", WindowSnap.TOP_HALF.value),
            ("Snap Bottom Half (50%)", WindowSnap.BOTTOM_HALF.value),
            ("Center (75% Size)", WindowSnap.CENTER.value),
        ]
        self._snap_map = {opt[0]: opt[1] for opt in snap_options}
        self._reverse_snap_map = {opt[1]: opt[0] for opt in snap_options}
        self.snap_combo = ttk.Combobox(form, values=[opt[0] for opt in snap_options], state="readonly", width=38)
        self.snap_combo.current(0)
        self.snap_combo.grid(row=10, column=1, sticky=tk.W, pady=4)

        # Timings
        timings_frame = ttk.Frame(form)
        timings_frame.grid(row=11, column=1, sticky=tk.W, pady=6)
        ttk.Label(timings_frame, text="Launch Delay (ms):").pack(side=tk.LEFT, padx=(0, 4))
        self.delay_var = tk.IntVar(value=1000)
        ttk.Entry(timings_frame, textvariable=self.delay_var, width=6).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(timings_frame, text="Timeout (ms):").pack(side=tk.LEFT, padx=(0, 4))
        self.timeout_var = tk.IntVar(value=15000)
        ttk.Entry(timings_frame, textvariable=self.timeout_var, width=6).pack(side=tk.LEFT)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(16, 0))
        if self.test_match_callback:
            ttk.Button(btn_frame, text="🔍 Test Match", command=self._on_test_match_clicked).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_frame, text="Save Application", style="Primary.TButton", command=self._save).pack(side=tk.RIGHT, padx=4)

    def _populate_fields(self) -> None:
        self.name_var.set(self.app.name)
        self.exe_var.set(self.app.executable)
        self.args_var.set(self.app.arguments)
        self.enabled_var.set(self.app.enabled)
        self.move_win_var.set(self.app.move_existing_window)
        self.launch_mode_var.set(self.app.launch_mode)
        self.title_pattern_var.set(self.app.title_pattern)
        self.delay_var.set(self.app.launch_delay_ms)
        self.timeout_var.set(self.app.window_timeout_ms)

        # Match desktop combo
        target_idx = 0
        for i, d in enumerate(self.desktops):
            if d.number == self.app.desktop:
                target_idx = i
                break
        if self.desktops:
            self.desktop_combo.current(target_idx)

        # Match policy
        policy_label = self._reverse_policy_map.get(self.app.window_policy, "Move main window only")
        self.policy_combo.set(policy_label)

        # Match monitor
        mon_idx = min(max(0, getattr(self.app, "monitor_index", 0)), 3)
        self.monitor_combo.current(mon_idx)

        # Match snap
        snap_val = getattr(self.app, "window_snap", WindowSnap.DEFAULT.value)
        snap_lbl = self._reverse_snap_map.get(snap_val, "Default (Preserve Geometry)")
        self.snap_combo.set(snap_lbl)

        self._validate_path_live()

    def _validate_path_live(self, _event=None) -> None:
        path = self.exe_var.get().strip()
        if not path:
            self.path_status_lbl.configure(text="", foreground="")
            return
        expanded = os.path.expandvars(path)
        if os.path.exists(expanded):
            self.path_status_lbl.configure(text="✓ Executable found", foreground="#107c41")
        else:
            self.path_status_lbl.configure(text="⚠ Path not found on disk", foreground="#b25900")

    def _browse_exe(self) -> None:
        chosen = filedialog.askopenfilename(
            parent=self,
            title="Select Application Executable",
            filetypes=[("Executable Files", "*.exe;*.cmd;*.bat"), ("All Files", "*.*")]
        )
        if chosen:
            self.exe_var.set(os.path.normpath(chosen))
            if not self.name_var.get():
                name = os.path.splitext(os.path.basename(chosen))[0]
                self.name_var.set(name.title())
            self._validate_path_live()

    def _on_template_selected(self, _event=None) -> None:
        idx = self.template_combo.current()
        if idx <= 0:
            return
        template: AppTemplate = APPLICATION_TEMPLATES[idx - 1]
        self.name_var.set(template.name)
        if template.candidate_paths:
            self.exe_var.set(template.candidate_paths[0])
        self.args_var.set(template.default_arguments)
        self.app.process_names = list(template.process_names)
        self.policy_var.set(template.window_policy)
        self.policy_combo.set(self._reverse_policy_map.get(template.window_policy, "Move main window only"))

        # Find desktop
        for i, d in enumerate(self.desktops):
            if d.number == template.default_desktop:
                self.desktop_combo.current(i)
                break
        self._validate_path_live()

    def _show_running_apps_picker(self) -> None:
        if not self.running_discoverer:
            return

        running = self.running_discoverer.discover_running_applications()
        if not running:
            messagebox.showinfo("Running Applications", "No visible application windows currently detected.", parent=self)
            return

        picker = tk.Toplevel(self)
        picker.title("Select Running Application")
        picker.geometry("560x400")
        picker.transient(self)
        picker.grab_set()

        tree = ttk.Treeview(picker, columns=("app", "proc", "window"), show="headings", height=12)
        tree.heading("app", text="Application")
        tree.heading("proc", text="Process")
        tree.heading("window", text="Window Title")
        tree.column("app", width=140)
        tree.column("proc", width=120)
        tree.column("window", width=260)
        tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        for i, r in enumerate(running):
            tree.insert("", tk.END, iid=str(i), values=(r.name, r.process_name, r.window_title))

        def select_item():
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            chosen_app = running[idx]
            self.name_var.set(chosen_app.name)
            self.exe_var.set(chosen_app.executable)
            self.app.process_names = [chosen_app.process_name]
            self._validate_path_live()
            picker.destroy()

        btn_bar = ttk.Frame(picker, padding=8)
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="Cancel", command=picker.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_bar, text="Select & Fill", style="Primary.TButton", command=select_item).pack(side=tk.RIGHT, padx=4)

    def _save(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Application name is required.", parent=self)
            return

        # Target desktop
        sel_desktop_idx = self.desktop_combo.current()
        target_desktop = self.desktops[sel_desktop_idx].number if sel_desktop_idx >= 0 else 1

        policy_key = self._policy_map.get(self.policy_combo.get(), WindowPolicy.MAIN_ONLY.value)

        self.app.name = name
        self.app.executable = self.exe_var.get().strip()
        self.app.arguments = self.args_var.get().strip()
        self.app.desktop = target_desktop
        self.app.enabled = self.enabled_var.get()
        self.app.move_existing_window = self.move_win_var.get()
        self.app.launch_mode = self.launch_mode_var.get()
        self.app.window_policy = policy_key
        self.app.title_pattern = self.title_pattern_var.get().strip()
        self.app.monitor_index = max(0, self.monitor_combo.current())
        self.app.window_snap = self._snap_map.get(self.snap_combo.get(), WindowSnap.DEFAULT.value)
        self.app.launch_delay_ms = max(0, self.delay_var.get())
        self.app.window_timeout_ms = max(1000, self.timeout_var.get())

        if not self.app.process_names and self.app.executable:
            self.app.process_names = [os.path.basename(self.app.executable)]

        # Validate
        errors, warnings = ConfigValidator.validate_app(self.app)
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors), parent=self)
            return

        if warnings:
            msg = "The following warnings were noted:\n\n" + "\n".join(warnings) + "\n\nDo you want to save anyway?"
            if not messagebox.askyesno("Save with Warnings", msg, parent=self):
                return

        if self.on_save:
            self.on_save(self.app)

        self.destroy()

    def _on_test_match_clicked(self) -> None:
        """Section 43: Diagnostic-only test matching tool."""
        if not self.test_match_callback:
            return

        # Build temporary AppConfig with current form values
        temp_app = AppConfig(
            id=self.app.id,
            name=self.name_var.get().strip() or "Application",
            executable=self.exe_var.get().strip(),
            arguments=self.args_var.get().strip(),
            desktop=self.desktops[self.desktop_combo.current()].number if self.desktop_combo.current() >= 0 else 1,
            enabled=self.enabled_var.get(),
            launch_mode=self.launch_mode_var.get(),
            window_policy=self._policy_map.get(self.policy_combo.get(), WindowPolicy.MAIN_ONLY.value),
            title_pattern=self.title_pattern_var.get().strip(),
            process_names=list(self.app.process_names)
        )
        if not temp_app.process_names and temp_app.executable:
            temp_app.process_names = [os.path.basename(temp_app.executable)]

        results = self.test_match_callback(temp_app)

        # Show modal dialog with test match results
        top = tk.Toplevel(self)
        top.title(f"Test Match: {temp_app.name}")
        top.geometry("600x420")
        top.transient(self)
        top.grab_set()

        frame = ttk.Frame(top, padding=14)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Window Match Evaluation — {temp_app.name}", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 4))
        rule_desc = f"Rule: Exe='{os.path.basename(temp_app.executable)}' | Policy='{temp_app.window_policy}'"
        if temp_app.title_pattern:
            rule_desc += f" | Title='{temp_app.title_pattern}'"
        ttk.Label(frame, text=rule_desc, style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 10))

        if not results:
            empty_box = ttk.LabelFrame(frame, text="Results", padding=16)
            empty_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            ttk.Label(empty_box, text="○ No active windows or running processes match this rule currently.", font=("Segoe UI", 10)).pack(pady=16)
            ttk.Label(empty_box, text="Start the application or check executable and title regex pattern.", style="Muted.TLabel").pack()
        else:
            res_box = ttk.LabelFrame(frame, text=f"Matches ({len(results)} found)", padding=8)
            res_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            tree = ttk.Treeview(res_box, columns=("conf", "pid", "hwnd", "dt", "title"), show="headings", height=8)
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

        notice = ttk.Label(frame, text="Note: Test Match is strictly read-only and diagnostic; no windows were moved.", style="Muted.TLabel")
        notice.pack(anchor=tk.W, pady=(0, 8))

        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="Close", command=top.destroy).pack(side=tk.RIGHT)
