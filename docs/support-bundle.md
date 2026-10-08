# Support Bundle Specification & Generation

## 1. Purpose

The **Support Bundle** is a standardized, privacy-preserving ZIP archive containing all relevant diagnostics, configuration metadata, and recent logs required to diagnose issues without exposing sensitive user information.

Conforms to Section 60 of the product specification.

---

## 2. Archive Structure

When generated, the ZIP archive contains:

```text
vdwm_support_bundle_YYYYMMDD_HHMMSS.zip
├── diagnostic_report.txt        # Full formatted diagnostic report
├── system_summary.json         # OS, runtime, and provider capability details
├── sanitized_config.json       # Current workspace configuration (redacted)
├── health_check_categories.json# Status breakdown across 10 subsystem categories
└── logs/                       # Recent session logs (sanitized)
    ├── workspace_20261008.log
    └── workspace_20261007.log
```

---

## 3. Privacy & Redaction Guarantees (Section 51)

Before writing any artifact into the ZIP archive, the centralized `LogRedactor` scans all contents:
- **Tokens & Passwords:** Strings matching `token=`, `password=`, `apikey=`, `secret=`, `credential=` have values replaced with `[REDACTED]`.
- **Bearer Tokens:** Authorization headers are masked (`Bearer [REDACTED]`).
- **User Paths:** User directory paths (e.g. `C:\Users\username`) have the username token replaced with `<USER>`.
- **Zero Raw Secrets:** Raw environment variables containing secret keywords are completely omitted.

---

## 4. How to Generate a Support Bundle

### Via Graphical User Interface:
1. Open the application.
2. Navigate to the **Diagnostics** tab.
3. Click the **📦 Generate Support Bundle** button.
4. Select a destination path (e.g. your Desktop or Downloads folder).
5. The ZIP archive will be created and a confirmation dialog will display the archive size and included file count.

### Via Python API:
```python
from pathlib import Path
from app.core.manager import WorkspaceManager
from app.services.support_bundle import SupportBundleService
from app.services.diagnostics_service import DiagnosticsService

manager = WorkspaceManager()
diag_svc = DiagnosticsService(
    config=manager.config,
    desktop_provider=manager.desktop_provider,
    process_provider=manager.process_provider,
    window_provider=manager.window_provider
)
bundle_svc = SupportBundleService(
    diagnostics_service=diag_svc,
    config_store=manager.config_store
)
bundle_svc.generate_bundle(Path("support_bundle.zip"))
```
