# Changelog

All notable changes to the Windows Virtual Desktop Workspace Manager project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-08

### Added
- **Centralized Log Redaction Layer**: `LogRedactor`, `RedactingFormatter`, and `RedactingFilter` automatically sanitize passwords, tokens, API keys, and sensitive environment variables from logs, reports, and UI buffers (Section 51).
- **Standardized Error Catalog**: `ErrorDefinition` and `ErrorCategory` catalog (e.g. `VDM-001`, `WIN-001`, `APP-001`, `CFG-001`, `SETUP-001`, `SEC-001`) with clear user remediation guidance (Section 59).
- **Categorized Diagnostics**: Diagnostic subsystem covering 10 distinct categories: System, Virtual Desktops, Provider, Configuration, Applications, Windows, Permissions, Storage, Dependencies, and Recent Errors (Section 27).
- **Support Bundle Generator**: Automated ZIP archive packaging sanitized diagnostics, recent scrubbed logs, schema metadata, and environment overview (Section 60).
- **Persistent Operation History**: Audit logging for all workspace operations (`Launch`, `Sync`, `Dry Run`), recording duration, targets, outcome, and details in `history.json` (Section 29).
- **State Machine Definition**: Formalized `ApplicationState` and `OperationPhase` lifecycle state models (Sections 37 & 38).
- **Window Match Testing Tool**: Diagnostic-only rule evaluator in UI and backend to test window and process matching rules with confidence scoring without moving windows or launching apps (Section 43).
- **10-Tab Information Architecture**: Full navigation revamp separating Dashboard, Workspaces, Applications, Virtual Desktops, Execution & Plan, History, Logs, Diagnostics, Settings, and About (Section 6).
- **Unsaved Changes Guard**: Prompts user before closing, switching profiles, or discarding unsaved edits (Section 23).
- **Keyboard Shortcuts**: Native-compliant accelerator keys (`Ctrl+S`, `Ctrl+R`, `F5`, `Ctrl+F`, `Ctrl+L`, `Ctrl+,`, `Esc`) with visible focus (Section 19).
- **Full Specification Documentation Suite**: Complete documentation covering user guide, UI/UX specification, state machine, error catalog, recovery guide, support bundle, test strategy, compatibility matrix, and release checklist (Section 61).
- **Expanded Test Suite (94 Automated Tests)**: Provider contract test suite (`test_provider_contracts.py`), failure injection test suite (`test_failure_injection.py`), and fuzz/robustness parsing suite (`test_fuzz_robustness.py`) ensuring 100% test pass rate in isolated environments (Sections 86, 87, 88).

### Changed
- Refactored `MainWindow` in `app/ui/app_window.py` to use modular tabbed views with non-color status badges, responsive scaling, and progressive disclosure (Section 5).
- Upgraded `AppDialog` to provide integrated "Test Match" tool alongside running process detection and template autofill.
- Enhanced `DiagnosticsService` with privacy redaction and categorized reporting.

### Fixed
- Fixed potential log leakage of secrets by applying `RedactingFormatter` across all logging handlers.
- Improved recovery handling for interrupted operations.

## [1.0.0] - 2026-02-01

### Added
- Initial production implementation for Windows 10/11 Virtual Desktop Workspace Manager.
- Core 7-layer application discovery engine and window matching policies.
- COM and `pyvda` virtual desktop providers with fallback mock providers.
- Setup runner `setup.py` and dedicated ICO desktop shortcut generators.
- Unit and scenario acceptance test suites.
