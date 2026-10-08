# Release Checklist

This document defines the release candidate verification criteria for **Virtual Desktop Workspace Manager** per Section 84 and Section 148 of the Master Specification.

---

## 1. Release Candidate Gate

All items must be satisfied prior to declaring a production release candidate or providing instructions for user deployment.

| Item | Requirement Area | Status | Verification Method |
|---|---|---|---|
| **RC-01** | Requirements Traceability | [x] Verified | Complete mapping of Sections 1–106 and 1–152 in [requirements-traceability.md](file:///c:/Users/farma/Desktop/Virtual%20Desktop%20Workspace%20Manager/docs/requirements-traceability.md). |
| **RC-02** | Static Security Review | [x] Verified | Inspected for prohibited patterns (`shell=True`, hidden PowerShell, token logging). Documented in [security-review.md](file:///c:/Users/farma/Desktop/Virtual%20Desktop%20Workspace%20Manager/docs/security-review.md). |
| **RC-03** | Mock Unit & Integration Tests | [x] Verified | 100% test pass rate in isolated mock environments (`tests/`). No real desktop manipulation. |
| **RC-04** | Configuration Migration | [x] Verified | Schema versioning (`SCHEMA_VERSION = 1`) with atomic file writes and automated backup rotation. |
| **RC-05** | Setup Tested in Isolation | [x] Verified | Tested via `tests/test_setup_isolated.py` using mock filesystem and registry mocks. `setup.py` not run on host. |
| **RC-06** | Packaging & Manifest Review | [x] Verified | PyInstaller spec and entry-point scripts reviewed per [packaging.md](file:///c:/Users/farma/Desktop/Virtual%20Desktop%20Workspace%20Manager/docs/packaging.md). |
| **RC-07** | Shortcut Targets Reviewed | [x] Verified | Two distinct shortcuts defined: `Configure Workspace Manager` (`--configure`) and `Run Workspace Manager` (`--run`). |
| **RC-08** | Shortcut Ownership Metadata | [x] Verified | Custom metadata stored in `config/shortcuts.json` tracking creator and hashes. |
| **RC-09** | UI Keyboard Navigation | [x] Verified | Full access keys, Tab navigation, `Ctrl+S`, `Ctrl+R`, `F5`, `Ctrl+F`, `Ctrl+L`, `Ctrl+,`, `Esc` shortcuts implemented. |
| **RC-10** | Empty / Loading / Error States | [x] Verified | All 10 UI tabs support intentional empty states, non-blocking asynchronous progress, and standardized error banners. |
| **RC-11** | Log Redaction | [x] Verified | `LogRedactor` active on root logger redacting passwords, tokens, API keys, and sensitive paths. |
| **RC-12** | Privacy-Preserving Diagnostics | [x] Verified | Categorized diagnostics redacting machine names, usernames, and arguments; zip support bundle generation tested. |
| **RC-13** | Network Isolation | [x] Verified | Pure offline-first architecture; zero network calls or telemetry endpoints. |
| **RC-14** | Startup Persistence Safety | [x] Verified | No automatic autorun registry entries unless explicitly requested via settings; no hidden scheduled tasks. |
| **RC-15** | Development Safety Boundary | [x] Verified | Zero real Windows desktops, windows, or desktop shortcuts manipulated during development. |

---

## 2. Pre-Flight Acceptance Criteria

Before executing real-desktop validation on an end-user machine (which requires explicit user command):

1. **Verify Python Runtime:** Python 3.10+ 64-bit on Windows 10 (1809+) or Windows 11 (21H2+).
2. **Review Config Path:** Confirm `%APPDATA%\VirtualDesktopWorkspaceManager` permissions.
3. **Execute Setup in User Space:** Run `python setup.py` only after user confirmation.
4. **Inspect First Run:** Ensure application opens into Configure mode with the First-Run Wizard and does NOT trigger automated desktop moves on fresh install.
