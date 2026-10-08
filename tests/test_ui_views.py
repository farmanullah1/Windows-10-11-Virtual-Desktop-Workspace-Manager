"""
Unit tests for MainWindow and UI components using mock providers.
"""

import os
import tempfile
import pytest
from pathlib import Path
from app.configuration.config_store import ConfigStore
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockProcessProvider,
    MockWindowProvider,
    MockApplicationLauncher,
)
from app.core.manager import WorkspaceManager
from app.models.workspace import AppConfig


def test_main_window_headless_initialization():
    """Tests initializing MainWindow and verifying all 10 tabs and components."""
    import tkinter as tk

    try:
        root_test = tk.Tk()
        root_test.withdraw()
    except tk.TclError:
        pytest.skip("Tkinter display unavailable in current headless test environment.")

    root_test.destroy()

    with tempfile.TemporaryDirectory() as td:
        store = ConfigStore(config_dir=Path(td))
        dp = MockVirtualDesktopProvider()
        pp = MockProcessProvider()
        wp = MockWindowProvider()
        launcher = MockApplicationLauncher()

        mgr = WorkspaceManager(
            config_store=store,
            desktop_provider=dp,
            window_provider=wp,
            process_provider=pp,
            launcher=launcher
        )

        from app.ui.app_window import MainWindow

        win = MainWindow(mgr, start_minimized=True)
        try:
            # Verify 10 tabs exist
            tab_count = win.notebook.index("end")
            assert tab_count == 10

            # Verify components
            assert hasattr(win, "app_tree")
            assert hasattr(win, "dt_tree")
            assert hasattr(win, "hist_tree")
            assert hasattr(win, "log_panel")

            # Verify unsaved changes state starts clean
            assert win.is_dirty is False

            # Test marking dirty
            win._mark_dirty()
            assert win.is_dirty is True

            # Test saving changes
            win._save_changes()
            assert win.is_dirty is False

            # Test Application filtering
            win.app_search_var.set("ghost_app_that_does_not_exist")
            win._refresh_applications_view()
            assert len(win.app_tree.get_children()) == 0

            win.app_search_var.set("")
            win._refresh_applications_view()
            assert len(win.app_tree.get_children()) > 0

            # Test Virtual Desktops view
            win._refresh_virtual_desktops_view()
            assert len(win.dt_tree.get_children()) >= 4

            # Test Tab selection
            win._select_tab(3)
            assert win.notebook.index(win.notebook.select()) == 3

            # Test escape shortcut clears search
            win.app_search_var.set("query")
            win._on_escape()
            assert win.app_search_var.get() == ""

        finally:
            win.tray_manager.stop()
            win.destroy()
