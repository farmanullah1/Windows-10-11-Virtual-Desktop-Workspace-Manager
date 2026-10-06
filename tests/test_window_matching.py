"""
Tests for Window matching policies, title filters, and candidate selection.
"""

from app.models.workspace import WindowPolicy
from app.providers.base import WindowInfo
from app.services.window_service import WindowService


def test_window_service_policy_main_only():
    svc = WindowService()
    windows = [
        WindowInfo(hwnd=101, title="Main App Window", pid=10, executable="", is_visible=True, is_minimized=True, is_maximized=False),
        WindowInfo(hwnd=102, title="App Visible Window", pid=10, executable="", is_visible=True, is_minimized=False, is_maximized=False),
    ]
    # MAIN_ONLY prefers non-minimized
    selected = svc.select_windows_by_policy(windows, policy=WindowPolicy.MAIN_ONLY.value)
    assert len(selected) == 1
    assert selected[0].hwnd == 102


def test_window_service_policy_all_matching():
    svc = WindowService()
    windows = [
        WindowInfo(hwnd=201, title="Editor 1", pid=20, executable="", is_visible=True, is_minimized=False, is_maximized=False),
        WindowInfo(hwnd=202, title="Editor 2", pid=20, executable="", is_visible=True, is_minimized=False, is_maximized=False),
    ]
    selected = svc.select_windows_by_policy(windows, policy=WindowPolicy.ALL_MATCHING.value)
    assert len(selected) == 2


def test_window_service_policy_title_contains():
    svc = WindowService()
    windows = [
        WindowInfo(hwnd=301, title="Google Search - Brave", pid=30, executable="", is_visible=True, is_minimized=False, is_maximized=False),
        WindowInfo(hwnd=302, title="Settings Page", pid=30, executable="", is_visible=True, is_minimized=False, is_maximized=False),
    ]
    selected = svc.select_windows_by_policy(windows, policy=WindowPolicy.TITLE_CONTAINS.value, title_pattern="Brave")
    assert len(selected) == 1
    assert selected[0].hwnd == 301


def test_window_service_policy_title_regex():
    svc = WindowService()
    windows = [
        WindowInfo(hwnd=401, title="Project [DEBUG] - Code", pid=40, executable="", is_visible=True, is_minimized=False, is_maximized=False),
        WindowInfo(hwnd=402, title="Project [RELEASE] - Code", pid=40, executable="", is_visible=True, is_minimized=False, is_maximized=False),
    ]
    selected = svc.select_windows_by_policy(windows, policy=WindowPolicy.TITLE_REGEX.value, title_pattern=r"\[DEBUG\]")
    assert len(selected) == 1
    assert selected[0].hwnd == 401
