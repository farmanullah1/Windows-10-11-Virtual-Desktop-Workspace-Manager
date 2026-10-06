"""
Live Log Viewer matching Section 40 specifications.
Features filtering by level, search, copy, clear, open log folder, and export diagnostics.
"""

from __future__ import annotations
import os
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable
from app.logging.logger import get_buffer_handler, get_default_log_dir, SUCCESS_LEVEL_NUM
from app.services.diagnostics_service import DiagnosticsService


class LogViewPanel(ttk.Frame):
    """Embeddable or standalone live logging panel."""

    def __init__(
        self,
        parent: tk.Widget,
        diagnostics_service: Optional[DiagnosticsService] = None,
        palette: Optional[dict] = None
    ):
        super().__init__(parent)
        self.diagnostics_service = diagnostics_service
        self.palette = palette or {}
        self.buffer_handler = get_buffer_handler()
        self.active_level_filter = "ALL"
        self.search_query = ""

        self._build_ui()
        self._load_buffered_records()
        self.buffer_handler.add_listener(self._on_new_record)

    def _build_ui(self) -> None:
        # Toolbar
        toolbar = ttk.Frame(self, padding=(0, 4))
        toolbar.pack(fill=tk.X)

        ttk.Label(toolbar, text="Filter:").pack(side=tk.LEFT, padx=(0, 4))
        self.filter_var = tk.StringVar(value="ALL")
        levels = ["ALL", "INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG"]
        self.level_combo = ttk.Combobox(toolbar, textvariable=self.filter_var, values=levels, state="readonly", width=9)
        self.level_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.level_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=18)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        # Action buttons
        ttk.Button(toolbar, text="Clear", width=7, command=self._clear_logs).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="Copy", width=7, command=self._copy_logs).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="Open Folder", width=11, command=self._open_log_folder).pack(side=tk.RIGHT, padx=2)
        if self.diagnostics_service:
            ttk.Button(toolbar, text="Export Diagnostics", width=16, command=self._export_diagnostics).pack(side=tk.RIGHT, padx=2)

        # Scrolled Text Box
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        log_bg = self.palette.get("log_bg", "#1e1e1e")
        log_fg = self.palette.get("log_fg", "#d4d4d4")

        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            bg=log_bg,
            fg=log_fg,
            font=("Consolas", 9),
            relief="flat",
            padx=8,
            pady=8
        )
        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Color tags
        self.text.tag_config("INFO", foreground="#4cc2ff")
        self.text.tag_config("SUCCESS", foreground="#6ccb5f")
        self.text.tag_config("WARNING", foreground="#fce100")
        self.text.tag_config("ERROR", foreground="#ff6a6a")
        self.text.tag_config("DEBUG", foreground="#8a8a8a")

    def _matches_filters(self, record: logging.LogRecord) -> bool:
        lvl = record.levelname.upper()
        if self.active_level_filter != "ALL" and lvl != self.active_level_filter:
            return False
        if self.search_query:
            msg = record.getMessage().lower()
            if self.search_query not in msg:
                return False
        return True

    def _format_record(self, record: logging.LogRecord) -> str:
        asctime = getattr(record, "asctime", "")
        if not asctime:
            import time
            asctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        return f"{asctime} [{record.levelname}] {record.getMessage()}\n"

    def _load_buffered_records(self) -> None:
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        for r in self.buffer_handler.get_records():
            if self._matches_filters(r):
                line = self._format_record(r)
                self.text.insert(tk.END, line, r.levelname)
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def _on_new_record(self, record: logging.LogRecord) -> None:
        if not self.winfo_exists():
            return
        # Dispatch to UI thread
        self.after(0, self._append_record, record)

    def _append_record(self, record: logging.LogRecord) -> None:
        if not self._matches_filters(record):
            return
        self.text.configure(state=tk.NORMAL)
        line = self._format_record(record)
        self.text.insert(tk.END, line, record.levelname)
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def _on_filter_changed(self, _event=None) -> None:
        self.active_level_filter = self.filter_var.get()
        self._load_buffered_records()

    def _on_search_changed(self, _event=None) -> None:
        self.search_query = self.search_var.get().strip().lower()
        self._load_buffered_records()

    def _clear_logs(self) -> None:
        self.buffer_handler.clear()
        self._load_buffered_records()

    def _copy_logs(self) -> None:
        content = self.text.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Copied", "Logs copied to clipboard.", parent=self)

    def _open_log_folder(self) -> None:
        log_dir = get_default_log_dir()
        if os.name == "nt":
            os.startfile(str(log_dir))
        else:
            import subprocess
            subprocess.Popen(["explorer", str(log_dir)])

    def _export_diagnostics(self) -> None:
        if not self.diagnostics_service:
            return
        report_text = self.diagnostics_service.generate_report()
        save_path = filedialog.asksaveasfilename(
            parent=self,
            title="Export Diagnostic Report",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile="workspace_diagnostics.txt"
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            messagebox.showinfo("Export Successful", f"Diagnostic report exported to:\n{save_path}", parent=self)
