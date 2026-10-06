# Windows Virtual Desktop Workspace Manager — Architecture Specification

## 1. System Overview

The **Windows Virtual Desktop Workspace Manager** is a production-grade utility designed for Windows 10 and Windows 11 (64-bit). It orchestrates Windows Virtual Desktops and organizes user applications across dedicated virtual spaces with zero destructive behavior, persistent configuration, failure isolation, and transparent observability.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                            │
│  MainWindow (Tkinter / TTK with Windows 11 Modern Theme)               │
│  ├── DashboardView (Status Badges, Counters, Action Triggers)         │
│  ├── DesktopCardsPanel (Virtual Desktops, App Lists, Quick Actions)    │
│  ├── LiveLogPanel (Live Log Streaming, Filtering, Diagnostics Export)  │
│  ├── AppDialog (Add/Edit Apps, Exe Browser, Running Apps Discovery)   │
│  ├── SetupWizardDialog (8-step First-Run Onboarding)                   │
│  ├── SettingsDialog (General, Execution Timers, Logging, Safety)       │
│  └── TrayIconManager (pystray System Tray Background Control)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     Core Orchestration Engine                          │
│  WorkspaceManager (Central Facade)                                     │
│  ├── WorkspaceExecutionPlan (Phased 7-Stage Idempotent Execution)      │
│  ├── WorkspaceSynchronizer (Reconciles Actual State vs Desired State)  │
│  ├── DryRunInspector (Non-mutating Action Previews)                    │
│  └── Cancellation / Emergency Stop Token                               │
└───────┬──────────────┬──────────────┬──────────────┬───────────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌────────────────────────┐
│ Virtual      ││ Window       ││ Process      ││ Application            │
│ Desktop API  ││ Management   ││ Management   ││ Discovery              │
│ Providers    ││ Providers    ││ & Execution  ││ Subsystem              │
│              ││              ││              ││                        │
│ • PyVDA COM  ││ • Win32      ││ • Safe       ││ • 7-Layer Resolver:    │
│ • Official   ││   EnumWindows││   Subprocess ││   1. Configured Exe    │
│   IVirtual   ││ • Top-Level  ││   (No Shell) ││   2. Running Process   │
│   Desktop    ││   Filter     ││ • Psutil     ││   3. Start Menu .lnk   │
│   Manager    ││ • Policy     ││   Process    ││   4. App Paths Registry│
│ • MockProvider││  Matcher    ││   Inspector  ││   5. Known Templates   │
│ • Keyboard   ││              ││ • Never-Kill ││   6. Env Expansion     │
│   Fallback   ││              ││   Guarantee  ││   7. Versioned Wildcards│
└──────────────┘└──────────────┘└──────────────┘└────────────────────────┘
        │              │              │              │
        └──────────────┴───────┬──────┴──────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Persistence, Logging & Recovery Layer                    │
│  ├── ConfigStore (%APPDATA%\VirtualDesktopWorkspaceManager)            │
│  │   ├── Atomic File Replacement (tempfile + move)                     │
│  │   ├── Automated Backups (workspace.backup.json, max 5 snapshots)    │
│  │   ├── Schema Migrations (v0 -> v1)                                  │
│  │   └── Crash Marker Detection (operation_in_progress.marker)         │
│  ├── Structured Logger (Console, Daily Disk Log, Memory Ring Buffer)   │
│  └── DiagnosticsService (Sanitized, Privacy-Redacted Diagnostics)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 Domain Models (`app/models/`)

* **`AppConfig`**: Encapsulates unique application IDs, names, executable paths with environment variable expansion, target desktop assignments, launch modes (`LAUNCH_IF_MISSING`, `ALWAYS_LAUNCH`, `REUSE_ONLY`), window policies (`MAIN_ONLY`, `ALL_MATCHING`, `TITLE_CONTAINS`, `TITLE_REGEX`), and bounded execution timeouts.
* **`DesktopConfig`**: Defines virtual desktop indices, friendly labels, and internal GUID references.
* **`WorkspaceProfile`**: Groups virtual desktop definitions and app configurations under isolated profile containers (e.g., Development, Work, Database).
* **`WorkspaceConfig`**: Root schema encompassing profiles, general preferences, execution timing thresholds, logging options, and safety guardrails.
* **`ExecutionReport`**: Immutable summary of an execution run, tracking desktops created, apps launched/reused, windows moved, warnings, errors, and precise run duration.

### 2.2 Providers & Abstraction Layer (`app/providers/`)

* **`IVirtualDesktopProvider`**: Abstract interface for desktop enumeration, creation, switching, window assignment, and verification.
  * **`WindowsVdaProvider`**: Production provider integrating with Windows 10/11 COM interfaces through `pyvda`.
  * **`OfficialComDesktopManager`**: Microsoft official COM `IVirtualDesktopManager` wrapper for direct verification and secondary desktop assignment.
  * **`MockVirtualDesktopProvider`**: In-memory test provider enabling 100% non-destructive automated testing.
  * **`KeyboardFallbackProvider`**: Documented fallback simulating Win+Ctrl shortcuts if direct COM interfaces are unavailable.
* **`IWindowProvider`**: Discovers usable top-level HWNDs, filtering out invisible helper windows, tooltip utilities, and system trays.
* **`IProcessProvider`**: Inspects running operating system processes via `psutil`.
* **`IApplicationLauncher`**: Spawns application executables safely using `subprocess.Popen` without shell interpretation.

### 2.3 Application Discovery (`app/discovery/`)

* Implements the strict **7-Layer Resolution Strategy**:
  1. User-configured executable path.
  2. Currently running matching processes.
  3. Start Menu and Desktop shell shortcuts (`.lnk` target resolution).
  4. Windows `App Paths` registry keys (HKCU and HKLM).
  5. Built-in application templates (Brave, Chrome, Edge, Firefox, VS Code, Visual Studio, Antigravity, SSMS, Postman, Docker Desktop, Terminal, Explorer).
  6. Environment variable expansion (`%ProgramFiles%`, `%LocalAppData%`, `%SystemRoot%`).
  7. Controlled directory scans for versioned applications (e.g. `%LocalAppData%\Postman\app-*\Postman.exe` or SSMS 18–22).

### 2.4 Core Execution Engine (`app/core/`)

* **`WorkspaceExecutionPlan`**: Executes a 7-stage sequence:
  * **Phase 1: Detect Desktops** — Enumerate available virtual desktops.
  * **Phase 2: Prepare Desktops** — Create only missing desktops up to target; never delete existing user desktops.
  * **Phase 3: Launch / Discover Applications** — Check running status; launch missing apps if configured.
  * **Phase 4: Wait for Top-Level Windows** — Non-blocking polling with configurable intervals and timeouts.
  * **Phase 5: Move Windows** — Assign top-level HWNDs to target desktops based on window policy.
  * **Phase 6: Verify Placement** — Confirm window desktop membership and log status.
  * **Phase 7: Generate Execution Report** — Produce comprehensive audit report.
* **`WorkspaceSynchronizer`**: Primary repair mechanism. Reconciles existing windows without launching missing instances.
* **`DryRunInspector`**: Generates pre-flight previews without mutating desktop or process state.

### 2.5 Persistence & Observability (`app/configuration/`, `app/logging/`)

* **Atomic Writes**: Writes changes to temporary files before replacing `workspace.json`.
* **Backups**: Automatically preserves `workspace.backup.json` and retains up to 5 historical timestamped snapshots.
* **Logging**: Structured logs with `INFO`, `SUCCESS`, `WARNING`, `ERROR`, `DEBUG` levels, daily log rotation, and thread-safe UI ring buffering.
* **Sanitized Diagnostics**: Generates developer diagnostics while redacting tokens, passwords, and user paths.
