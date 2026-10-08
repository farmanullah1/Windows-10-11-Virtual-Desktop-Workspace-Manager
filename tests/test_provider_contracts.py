"""
Contract tests for Provider interfaces and their Mock implementations per Section 86.
Validates that IVirtualDesktopProvider, IWindowProvider, IProcessProvider,
and IApplicationLauncher strictly uphold interface contracts.
"""

import pytest
from app.providers.base import (
    IVirtualDesktopProvider,
    IWindowProvider,
    IProcessProvider,
    IApplicationLauncher,
    DesktopInfo,
    WindowInfo,
    ProcessInfo,
)
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockWindowProvider,
    MockProcessProvider,
    MockApplicationLauncher,
)


class TestVirtualDesktopProviderContract:
    """Verifies IVirtualDesktopProvider contract compliance."""

    def test_mock_implements_interface(self):
        provider = MockVirtualDesktopProvider(initial_desktop_count=3)
        assert isinstance(provider, IVirtualDesktopProvider)

    def test_enumeration_and_counts(self):
        provider = MockVirtualDesktopProvider(initial_desktop_count=3)
        assert provider.is_available() is True
        assert provider.get_desktop_count() == 3

        desktops = provider.get_desktops()
        assert len(desktops) == 3
        for i, d in enumerate(desktops, 1):
            assert isinstance(d, DesktopInfo)
            assert d.number == i
            assert isinstance(d.id, str)
            assert isinstance(d.name, str)

        curr = provider.get_current_desktop_number()
        assert curr == 1
        assert 1 <= curr <= provider.get_desktop_count()

    def test_create_desktop_contract(self):
        provider = MockVirtualDesktopProvider(initial_desktop_count=2)
        initial_count = provider.get_desktop_count()

        new_d = provider.create_desktop()
        assert isinstance(new_d, DesktopInfo)
        assert new_d.number == initial_count + 1
        assert provider.get_desktop_count() == initial_count + 1

    def test_switch_desktop_contract(self):
        provider = MockVirtualDesktopProvider(initial_desktop_count=4)
        assert provider.switch_to_desktop(3) is True
        assert provider.get_current_desktop_number() == 3

        # Invalid desktop numbers
        assert provider.switch_to_desktop(0) is False
        assert provider.switch_to_desktop(999) is False
        assert provider.get_current_desktop_number() == 3  # unchanged

    def test_window_movement_and_query_contract(self):
        provider = MockVirtualDesktopProvider(initial_desktop_count=3)
        hwnd = 12345

        # Move to desktop 2
        assert provider.move_window_to_desktop(hwnd, 2) is True
        assert provider.get_window_desktop(hwnd) == 2
        assert provider.is_window_on_desktop(hwnd, 2) is True
        assert provider.is_window_on_desktop(hwnd, 1) is False

        # Move to invalid desktop
        assert provider.move_window_to_desktop(hwnd, 99) is False
        assert provider.get_window_desktop(hwnd) == 2

        # Verification disabled mode
        provider.allow_verification = False
        assert provider.is_window_on_desktop(hwnd, 2) is None
        assert provider.is_window_on_current_desktop(hwnd) is None


class TestWindowProviderContract:
    """Verifies IWindowProvider contract compliance."""

    def test_mock_implements_interface(self):
        provider = MockWindowProvider()
        assert isinstance(provider, IWindowProvider)

    def test_window_query_contracts(self):
        win1 = WindowInfo(
            hwnd=1001,
            title="Google Chrome - Dashboard",
            pid=501,
            executable="chrome.exe",
            is_visible=True,
            is_minimized=False,
            is_maximized=True,
        )
        win2 = WindowInfo(
            hwnd=1002,
            title="Code - workspace.py",
            pid=502,
            executable="code.exe",
            is_visible=True,
            is_minimized=False,
            is_maximized=False,
        )
        win_hidden = WindowInfo(
            hwnd=1003,
            title="Hidden Background Helper",
            pid=501,
            executable="chrome.exe",
            is_visible=False,
            is_minimized=False,
            is_maximized=False,
        )

        provider = MockWindowProvider([win1, win2, win_hidden])

        # get_all_top_level_windows returns only visible windows
        all_visible = provider.get_all_top_level_windows()
        assert len(all_visible) == 2
        assert win1 in all_visible
        assert win2 in all_visible
        assert win_hidden not in all_visible

        # find_windows_for_process ignores invisible
        pid_windows = provider.find_windows_for_process(501)
        assert len(pid_windows) == 1
        assert pid_windows[0].hwnd == 1001

        # find_windows_by_title (substring)
        code_matches = provider.find_windows_by_title("Code")
        assert len(code_matches) == 1
        assert code_matches[0].hwnd == 1002

        # find_windows_by_title (regex)
        regex_matches = provider.find_windows_by_title(r"chrome.*dashboard", is_regex=True)
        assert len(regex_matches) == 1
        assert regex_matches[0].hwnd == 1001

        # get_window_info
        assert provider.get_window_info(1001) == win1
        assert provider.get_window_info(9999) is None


class TestProcessProviderContract:
    """Verifies IProcessProvider contract compliance."""

    def test_mock_implements_interface(self):
        provider = MockProcessProvider()
        assert isinstance(provider, IProcessProvider)

    def test_process_query_contracts(self):
        p1 = ProcessInfo(pid=100, name="brave.exe", executable_path="C:\\Apps\\brave.exe", cmdline=[])
        p2 = ProcessInfo(pid=200, name="python.exe", executable_path="C:\\Python\\python.exe", cmdline=[])
        provider = MockProcessProvider([p1, p2])

        assert provider.is_process_running("brave.exe") is True
        assert provider.is_process_running("C:\\Apps\\brave.exe") is True
        assert provider.is_process_running("notepad.exe") is False

        matching = provider.get_running_processes_matching(["brave.exe", "notepad.exe"])
        assert len(matching) == 1
        assert matching[0].pid == 100

        assert provider.get_process_info(100) == p1
        assert provider.get_process_info(999) is None
        assert len(provider.get_all_running_processes()) == 2


class TestApplicationLauncherContract:
    """Verifies IApplicationLauncher contract compliance."""

    def test_mock_implements_interface(self):
        launcher = MockApplicationLauncher()
        assert isinstance(launcher, IApplicationLauncher)

    def test_launch_contract(self):
        window_provider = MockWindowProvider()
        process_provider = MockProcessProvider()
        launcher = MockApplicationLauncher(
            auto_create_window=True,
            window_provider=window_provider,
            process_provider=process_provider
        )

        pid1 = launcher.launch("C:\\Tools\\app.exe", "--debug", "C:\\Tools")
        assert isinstance(pid1, int)
        assert pid1 > 0

        pid2 = launcher.launch("C:\\Tools\\app.exe")
        assert pid2 > pid1  # PIDs are distinct

        assert len(launcher.launched_commands) == 2
        assert process_provider.is_process_running("app.exe") is True
        assert len(window_provider.get_all_top_level_windows()) == 2
