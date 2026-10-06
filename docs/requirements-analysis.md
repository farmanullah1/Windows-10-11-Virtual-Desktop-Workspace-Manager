# Requirements Analysis — Windows Virtual Desktop Workspace Manager

This document provides a comprehensive requirements analysis for the production-grade **Windows 10/11 Virtual Desktop Workspace Manager**, establishing functional, non-functional, safety, and security baselines.

---

## 1. Executive Summary

Modern software development workflows require context switching across multiple domains: web browsing, integrated development environments (IDEs), database management tools, API testing suites, and communication channels. Windows 10 and 11 offer native Virtual Desktops to segregate these environments, but lack native capability to automatically orchestrate, persist, and reliably map designated application windows into their designated virtual spaces.

The **Windows Virtual Desktop Workspace Manager** addresses this capability gap without compromising system stability, application data, or user control.

---

## 2. Functional Requirements

### 2.1 Virtual Desktop Orchestration (REQ-F-VD)

* **REQ-F-VD-01 (Detection)**: The application must detect and enumerate all currently open Windows Virtual Desktops using available system COM APIs.
* **REQ-F-VD-02 (Desktop Preservation)**: Existing virtual desktops created by the user must never be deleted or closed automatically.
* **REQ-F-VD-03 (Incremental Creation)**: If the active workspace configuration requires $N$ virtual desktops and only $M < N$ currently exist, the application must create exactly $N - M$ virtual desktops up to a configurable ceiling (`max_desktops_limit`, default 10).
* **REQ-F-VD-04 (Fallback Operation)**: If internal Windows COM interfaces are unavailable due to Windows OS build changes or security policies, the system must detect this and fall back to official COM interfaces or documented keyboard hotkeys.

### 2.2 Application Discovery & Launch Management (REQ-F-APP)

* **REQ-F-APP-01 (7-Layer Resolution)**: Target application executables must be discovered using a prioritized 7-layer strategy:
  1. User-configured absolute path.
  2. Currently running matching processes (`psutil`).
  3. Start Menu and Desktop shell shortcuts (`.lnk` target resolution).
  4. Windows `App Paths` registry keys (HKCU / HKLM).
  5. Built-in application templates (Brave, Chrome, Edge, Firefox, VS Code, Visual Studio, Antigravity, SSMS, Postman, Docker Desktop, Terminal, Explorer).
  6. Environment variable expansion (`%ProgramFiles%`, `%LocalAppData%`, `%SystemRoot%`).
  7. Versioned directory wildcards (e.g. `%LocalAppData%\Postman\app-*\Postman.exe`).
* **REQ-F-APP-02 (Launch Modes)**: Support three explicit launch policies per application:
  * `LAUNCH_IF_MISSING`: Launch only if no matching running instance/window exists.
  * `ALWAYS_LAUNCH`: Launch a new instance regardless of current running instances.
  * `REUSE_ONLY`: Never launch an executable; only locate and move existing running windows.
* **REQ-F-APP-03 (Shell Injection Prevention)**: Executables must be spawned strictly via tokenized argument lists without invoking `cmd.exe`, PowerShell, or `shell=True`.
* **REQ-F-APP-04 (Process Isolation & Non-Termination)**: The manager must **never kill, terminate, or terminate child trees** of running application processes.

### 2.3 Window Filtering & Desktop Assignment (REQ-F-WIN)

* **REQ-F-WIN-01 (Top-Level Filtering)**: Only genuine, visible top-level windows (`WS_VISIBLE`, non-zero client geometry, not `WS_EX_TOOLWINDOW`) may be considered for movement. Invisible helper processes, background workers, and tray icons must be filtered out.
* **REQ-F-WIN-02 (Multi-Window Policies)**: Support configurable policies:
  * `MAIN_ONLY`: Move only the primary/active top-level window.
  * `ALL_MATCHING`: Move all matching top-level windows belonging to the process.
  * `TITLE_CONTAINS`: Move windows whose title contains a specified substring.
  * `TITLE_REGEX`: Move windows whose title matches a regular expression.
* **REQ-F-WIN-03 (Window Ready Polling)**: Implement non-blocking polling with configurable interval and bounded timeouts (`window_timeout_ms`) to accommodate heavy applications (SSMS, Visual Studio, IDEs) during startup.
* **REQ-F-WIN-04 (Stale HWND Revalidation)**: Window handles (HWND) and process IDs (PID) must be revalidated immediately prior to any move operation to prevent race conditions caused by closed or replaced windows.

### 2.4 User Interface & Entry Points (REQ-F-UI)

* **REQ-F-UI-01 (Fluent Windows 11 GUI)**: Deliver a responsive, high-contrast Tkinter interface adhering to Windows 11 styling tokens.
* **REQ-F-UI-02 (Two User-Facing Desktop Shortcuts)**:
  * `Virtual Desktop Workspace Manager — Configure.lnk`: Exclusively opens configuration and management UI; never launches workspace or moves windows.
  * `Virtual Desktop Workspace Manager — Run Workspace.lnk`: Explicitly executes the active workspace profile.
* **REQ-F-UI-03 (Profiles)**: Allow creating, editing, switching, importing, and exporting distinct workspace profiles (e.g., Development, Work, Database).
* **REQ-F-UI-04 (Dry-Run Mode)**: Provide non-mutating pre-flight simulation showing exact desktop creations, app launches, and window moves without altering system state.
* **REQ-F-UI-05 (Sync Mode)**: Provide idempotent synchronization reconciling window placements without launching missing applications.
* **REQ-F-UI-06 (Emergency Stop / Pause)**: Allow users to cancel or pause workspace execution mid-flight.

---

## 3. Non-Functional Requirements

### 3.1 Security & Elevation (REQ-NF-SEC)

* **REQ-NF-SEC-01 (Standard User Execution)**: Must operate entirely within standard user privileges (Medium Integrity). Never prompt for automatic elevation or require Administrator rights.
* **REQ-NF-SEC-02 (UIPI Awareness)**: Gracefully detect and report windows belonging to elevated processes that cannot be manipulated from standard user context.
* **REQ-NF-SEC-03 (Privacy & Redaction)**: Diagnostic export must automatically redact Windows usernames, passwords, API tokens, and private user paths.
* **REQ-NF-SEC-04 (Zero Telemetry)**: 100% offline operation with no network requests, tracking, or telemetry.

### 3.2 Reliability & Fault Tolerance (REQ-NF-REL)

* **REQ-NF-REL-01 (Atomic Configuration Writes)**: Configuration files (`workspace.json`) must be written to temporary files and replaced atomically.
* **REQ-NF-REL-02 (Rolling Backups)**: Maintain `workspace.backup.json` and up to 5 historical timestamped snapshots.
* **REQ-NF-REL-03 (Crash Markers)**: Detect interrupted runs via ephemeral marker files and prompt for safe synchronization upon next startup.
* **REQ-NF-REL-04 (Failure Isolation)**: Failure of one application to launch or move must never abort remaining operations.
* **REQ-NF-REL-05 (Thread Safety)**: Background execution must never lock the UI thread or cause deadlocks in logging handlers.

---

## 4. Requirements Traceability Matrix

| Requirement ID | Specification | Architectural Component | Implementation File | Verification Test |
| --- | --- | --- | --- | --- |
| REQ-F-VD-01 | Enumerate Desktops | Virtual Desktop Providers | `app/providers/windows_vda_provider.py` | `tests/test_workspace_scenarios.py` |
| REQ-F-VD-02 | Never Delete Desktops | Execution Planner | `app/core/execution_plan.py` | `tests/test_workspace_scenarios.py` |
| REQ-F-VD-03 | Incremental Creation | Execution Planner | `app/core/execution_plan.py` | `tests/test_workspace_scenarios.py` |
| REQ-F-APP-01 | 7-Layer App Discovery | App Detector | `app/discovery/app_detector.py` | `tests/test_workspace_scenarios.py` |
| REQ-F-APP-02 | Three Launch Modes | Models & Execution Plan | `app/models/workspace.py` | `tests/test_workspace_scenarios.py` |
| REQ-F-APP-03 | Safe Subprocess Execution | Process Service | `app/services/process_service.py` | `tests/test_workspace_scenarios.py` |
| REQ-F-WIN-01 | Visible Top-Level Filter | Window Service | `app/services/window_service.py` | `tests/test_window_matching.py` |
| REQ-F-WIN-02 | Multi-Window Policies | Window Service | `app/services/window_service.py` | `tests/test_window_matching.py` |
| REQ-F-WIN-04 | Stale HWND Revalidation | Window Service | `app/services/window_service.py` | `tests/test_window_matching.py` |
| REQ-F-UI-02 | Two Desktop Shortcuts | Shortcut Service | `app/services/shortcut_service.py` | `tests/test_shortcut_service.py` |
| REQ-NF-SEC-01 | Standard User Safety | Security Boundary | `app/services/startup_service.py` | `tests/test_config.py` |
| REQ-NF-SEC-03 | Sanitized Diagnostics | Diagnostics Service | `app/services/diagnostics_service.py` | `tests/test_diagnostics.py` |
| REQ-NF-REL-01 | Atomic JSON Persistence | Config Store | `app/configuration/config_store.py` | `tests/test_config.py` |
| REQ-NF-REL-02 | Rolling Backups | Config Store | `app/configuration/config_store.py` | `tests/test_config.py` |
