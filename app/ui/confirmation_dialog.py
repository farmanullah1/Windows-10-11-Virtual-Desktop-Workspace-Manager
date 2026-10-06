"""
Safety confirmation dialog displayed before executing workspace operations.
Reminds the user that no processes will be killed and no user data will be deleted.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class ConfirmationDialog(tk.Toplevel):
    """Explicit confirmation dialog matching Section 77 specifications."""

    def __init__(
        self,
        parent: tk.Widget,
        operation_name: str = "Workspace Execution",
        on_confirm: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.title("Confirm Workspace Execution")
        self.geometry("460x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.confirmed = False
        self.on_confirm = on_confirm

        self._build_ui(operation_name)

    def _build_ui(self, operation_name: str) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text=operation_name, style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(container, text="The following actions will occur:", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 6))

        box = ttk.LabelFrame(container, text="Actions Preview", padding=10)
        box.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(box, text="✓ Create missing Virtual Desktops (if required)", style="Success.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(box, text="✓ Launch configured applications (if missing)", style="Success.TLabel").pack(anchor=tk.W, pady=2)
        ttk.Label(box, text="✓ Move application windows to assigned desktops", style="Success.TLabel").pack(anchor=tk.W, pady=2)

        guard_box = ttk.Frame(container)
        guard_box.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(guard_box, text="• No applications will be uninstalled.", style="Muted.TLabel").pack(anchor=tk.W)
        ttk.Label(guard_box, text="• No processes will be terminated.", style="Muted.TLabel").pack(anchor=tk.W)
        ttk.Label(guard_box, text="• No files or developer data will be modified.", style="Muted.TLabel").pack(anchor=tk.W)

        btn_bar = ttk.Frame(container)
        btn_bar.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_bar, text="Run Workspace", style="Primary.TButton", command=self._confirm).pack(side=tk.RIGHT, padx=4)

    def _confirm(self) -> None:
        self.confirmed = True
        self.destroy()
        if self.on_confirm:
            self.on_confirm()
