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
