"""
Support Bundle service that packages redacted diagnostics, sanitized logs,
configuration metadata, and system summary into a ZIP archive for troubleshooting.
Conforms to Section 60 (Support Bundle).
"""

from __future__ import annotations
import os
import json
import time
import zipfile
import platform
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from app import __version__
from app.logging.redactor import get_global_redactor
from app.services.diagnostics_service import DiagnosticsService
from app.configuration.config_store import ConfigStore


class SupportBundleService:
    """Creates a privacy-preserving diagnostic archive for support/troubleshooting."""

    def __init__(
        self,
        diagnostics_service: DiagnosticsService,
        config_store: ConfigStore,
        log_dir: Optional[Path] = None
    ):
        self.diagnostics_service = diagnostics_service
        self.config_store = config_store
        self.log_dir = log_dir or config_store.config_dir / "logs"
        self.redactor = get_global_redactor()

    def generate_bundle(self, destination_zip: Path) -> Dict[str, Any]:
        """
        Gathers diagnostic artifacts, sanitizes all contents,
        and saves them into destination_zip.
        """
        destination_zip = Path(destination_zip)
        destination_zip.parent.mkdir(parents=True, exist_ok=True)

        files_written: List[str] = []

        with zipfile.ZipFile(destination_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. Diagnostic report (text)
            diag_report = self.diagnostics_service.generate_report()
            sanitized_report = self.redactor.redact(diag_report)
            zf.writestr("diagnostic_report.txt", sanitized_report)
            files_written.append("diagnostic_report.txt")

            # 2. System and Provider Summary (JSON)
            summary = {
                "bundle_created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "application_version": __version__,
                "os": f"{platform.system()} {platform.release()}",
                "os_build": platform.version(),
                "architecture": platform.architecture()[0],
                "python_version": sys.version.split()[0],
                "desktop_provider": getattr(self.diagnostics_service.desktop_provider, "name", "unknown"),
                "process_provider": getattr(self.diagnostics_service.process_provider, "name", "unknown"),
                "window_provider": getattr(self.diagnostics_service.window_provider, "name", "unknown"),
                "offline_mode": True,
            }
            zf.writestr("system_summary.json", json.dumps(summary, indent=2))
            files_written.append("system_summary.json")

            # 3. Sanitized Active Configuration (JSON)
            try:
                config_dict = self.config_store.load().to_dict()
                sanitized_config = self.redactor.redact_dict(config_dict)
                zf.writestr("sanitized_config.json", json.dumps(sanitized_config, indent=2))
                files_written.append("sanitized_config.json")
            except Exception as ex:
                zf.writestr("config_error.txt", f"Error exporting configuration: {ex}")

            # 4. Recent Logs (sanitized)
            log_entries: List[str] = []
            if self.log_dir.exists():
                for log_file in sorted(self.log_dir.glob("*.log"), reverse=True)[:3]:
                    try:
                        content = log_file.read_text(encoding="utf-8", errors="replace")
                        sanitized_content = self.redactor.redact(content)
                        zf.writestr(f"logs/{log_file.name}", sanitized_content)
                        files_written.append(f"logs/{log_file.name}")
                    except Exception:
                        pass

            # 5. Health Check Breakdown
            try:
                health_checks = self.diagnostics_service.run_categorized_diagnostics()
                zf.writestr("health_check_categories.json", json.dumps(health_checks, indent=2))
                files_written.append("health_check_categories.json")
            except Exception:
                pass

        file_size = destination_zip.stat().st_size if destination_zip.exists() else 0

        return {
            "success": True,
            "archive_path": str(destination_zip),
            "files_included": files_written,
            "size_bytes": file_size,
        }
