"""
Unit tests for SupportBundleService and categorized diagnostics (Section 27 & 60).
"""

import tempfile
import zipfile
from pathlib import Path
from app.models.workspace import WorkspaceConfig
from app.configuration.config_store import ConfigStore
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockProcessProvider,
    MockWindowProvider,
)
from app.services.diagnostics_service import DiagnosticsService
from app.services.support_bundle import SupportBundleService


def test_categorized_diagnostics_10_categories():
    with tempfile.TemporaryDirectory() as td:
        store = ConfigStore(config_dir=Path(td))
        cfg = store.load()
        dp = MockVirtualDesktopProvider()
        pp = MockProcessProvider()
        wp = MockWindowProvider()

        diag = DiagnosticsService(
            config=cfg,
            desktop_provider=dp,
            process_provider=pp,
            window_provider=wp
        )

        categories = diag.run_categorized_diagnostics()

        expected_cats = [
            "System", "Virtual Desktops", "Provider", "Configuration",
            "Applications", "Windows", "Permissions", "Storage",
            "Dependencies", "Recent Errors"
        ]
        assert len(categories) == 10
        for cat in expected_cats:
            assert cat in categories
            assert categories[cat]["status"] in ["Passed", "Warning", "Failed", "Not Tested"]
            assert len(categories[cat]["items"]) > 0


def test_support_bundle_generation():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        store = ConfigStore(config_dir=tdp)
        cfg = store.load()
        dp = MockVirtualDesktopProvider()
        pp = MockProcessProvider()
        wp = MockWindowProvider()

        # Add a dummy log file
        log_dir = tdp / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "workspace_test.log").write_text("2026-02-01 [INFO] Started with token=secret123\n", encoding="utf-8")

        diag = DiagnosticsService(
            config=cfg,
            desktop_provider=dp,
            process_provider=pp,
            window_provider=wp
        )

        bundle_svc = SupportBundleService(
            diagnostics_service=diag,
            config_store=store,
            log_dir=log_dir
        )

        output_zip = tdp / "support_bundle.zip"
        res = bundle_svc.generate_bundle(output_zip)

        assert res["success"] is True
        assert output_zip.exists()
        assert res["size_bytes"] > 0

        # Inspect ZIP contents
        with zipfile.ZipFile(output_zip, "r") as zf:
            namelist = zf.namelist()
            assert "diagnostic_report.txt" in namelist
            assert "system_summary.json" in namelist
            assert "sanitized_config.json" in namelist
            assert "health_check_categories.json" in namelist

            # Check that log content was redacted inside zip
            log_contents = [zf.read(n).decode("utf-8") for n in namelist if n.startswith("logs/")]
            assert len(log_contents) > 0
            for lc in log_contents:
                assert "secret123" not in lc
                assert "token=[REDACTED]" in lc
