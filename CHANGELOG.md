# Changelog

All notable changes to the Windows Virtual Desktop Workspace Manager project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-10-08

### Added
- **Multi-Monitor Display Awareness & Window Geometry Snapping / Tiling**:
  - `IWindowProvider` and `WindowService` enhanced with multi-monitor enumeration (`EnumDisplayMonitors`, `GetMonitorInfo` with work area) and geometry tiling (`SetWindowPos`).
  - Added `WindowSnap` enum (`DEFAULT`, `MAXIMIZE`, `MINIMIZE`, `LEFT_HALF`, `RIGHT_HALF`, `TOP_HALF`, `BOTTOM_HALF`, `CENTER`, `CUSTOM`).
  - `AppConfig` expanded with `monitor_index`, `window_snap`, and `custom_rect` fields.
  - `ExecutionPlan` integrates monitor & snap placement immediately after desktop window assignment.
  - Applications table UI and `AppDialog` include Target Monitor and Layout Snap configuration and indicators.
- **Hardware & Session Event Listener / Auto-Triggering Engine**:
  - `TriggerEngine` background daemon thread monitoring hardware display topology changes (`ON_DISPLAY_CHANGE`), scheduled wall-clock times (`ON_TIME_SCHEDULE`), and session startup (`ON_STARTUP`).
  - Robust cooldown guards and `automation_enabled` safety controls to prevent duplicate activations.
  - Profile models updated with `ProfileTrigger` and `TriggerType`.
- **Encrypted Profile Export/Import & Team Sharing**:
  - `ProfileSharingService` providing PBKDF2-HMAC-SHA256 (100,000 iterations) key derivation, stream encryption, and HMAC-SHA256 authenticated integrity verification with zero external dependencies.
  - Automatic path generalization (`%USERPROFILE%` portability across differing developer machines).
  - UI password prompt modals on export and import.
- **Native Windows 11 Build-Resilient Dynamic COM Provider & Fallback Bridge**:
  - `WindowsDynamicComProvider` supporting dynamic vtable offset dispatch across Windows 10 (Builds 17763–19045), Windows 11 21H2 (Build 22000), 22H2/23H2 (Builds 22621/22631), and Windows 11 24H2 (Build 26100+).
  - Graceful cascade fallback to PyVDA, official COM, and Mock provider.
- **Expanded Test Suite (109 Automated Tests)**: Added 15 new automated tests across `test_monitor_snap_feature.py`, `test_trigger_engine.py`, `test_profile_sharing.py`, and `test_dynamic_com_provider.py`.

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
