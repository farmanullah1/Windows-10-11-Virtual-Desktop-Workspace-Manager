"""
Tests for DiagnosticsService and privacy redaction.
"""

from app.models.workspace import WorkspaceConfig
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockProcessProvider,
    MockWindowProvider,
)
from app.services.diagnostics_service import DiagnosticsService


def test_diagnostics_report_redaction():
    config = WorkspaceConfig()
    dp = MockVirtualDesktopProvider()
    pp = MockProcessProvider()
    wp = MockWindowProvider()

    diag = DiagnosticsService(config, dp, pp, wp)
    sample_text = "Connecting with token=secret12345&password=mypassword to service"
    sanitized = diag._sanitize(sample_text)

    assert "secret12345" not in sanitized
    assert "mypassword" not in sanitized
    assert "***REDACTED***" in sanitized


def test_diagnostics_report_generation():
    config = WorkspaceConfig()
    dp = MockVirtualDesktopProvider()
    pp = MockProcessProvider()
    wp = MockWindowProvider()

    diag = DiagnosticsService(config, dp, pp, wp)
    report = diag.generate_report()

    assert "VIRTUAL DESKTOP WORKSPACE MANAGER — DIAGNOSTIC REPORT" in report
    assert "VIRTUAL DESKTOP SUBSYSTEM" in report
    assert "ACTIVE WORKSPACE PROFILE" in report


def test_health_check_execution_and_summary():
    """Section 113: Verify all 8 health check items and summary format."""
    config = WorkspaceConfig()
    dp = MockVirtualDesktopProvider()
    pp = MockProcessProvider()
    wp = MockWindowProvider()

    diag = DiagnosticsService(config, dp, pp, wp)
    checks = diag.run_health_check()

    assert len(checks) == 8
    expected_keys = [
        "windows_supported",
        "virtual_desktop_provider_available",
        "configuration_valid",
        "desktop_mappings_valid",
        "applications_detected",
        "permissions_sufficient",
        "configuration_writable",
        "logging_writable",
    ]
    for key in expected_keys:
        assert key in checks
        assert "title" in checks[key]
        assert "ok" in checks[key]
        assert "detail" in checks[key]

    summary = diag.format_health_check_summary()
    assert "VIRTUAL DESKTOP WORKSPACE MANAGER — HEALTH CHECK" in summary
    assert "OVERALL STATUS:" in summary

