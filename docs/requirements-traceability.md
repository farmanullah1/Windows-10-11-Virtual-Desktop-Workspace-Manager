# Requirements Traceability Matrix — Windows Virtual Desktop Workspace Manager

This document maps all system requirements from the technical specification to their architectural implementations, source code files, automated verification tests, and current compliance status.

---

## 1. Compliance Legend

* **PASS**: Completely implemented and verified by automated unit / mock test suite.
* **PARTIAL**: Implemented with documented fallback or operating system limitation.
* **UNSUPPORTED**: Windows API does not expose native capability; handled with explicit fallback warning.

---

## 2. Traceability Matrix

### 2.1 Virtual Desktop Subsystem (REQ-VD)

```text
Requirement:    REQ-VD-001 — Detect and Enumerate Virtual Desktops
Implementation: Query desktop count and active view using PyVDA COM wrapper
Source File:    app/providers/windows_vda_provider.py
Test:           tests/test_workspace_scenarios.py::test_scenario_1_fresh_launch_creates_required_desktops
Status:         PASS
```

```text
Requirement:    REQ-VD-002 — Incremental Desktop Creation
Implementation: Calculate difference between target and existing desktops; create missing
Source File:    app/core/execution_plan.py
Test:           tests/test_workspace_scenarios.py::test_scenario_2_subsequent_launch_no_duplicate_desktops
Status:         PASS
```

```text
Requirement:    REQ-VD-003 — Never Automatically Delete Virtual Desktops
Implementation: Deletion logic strictly excluded from execution planner and synchronizer
Source File:    app/core/execution_plan.py
Test:           tests/test_workspace_scenarios.py::test_scenario_6_existing_extra_desktops_preserved
Status:         PASS
```

```text
Requirement:    REQ-VD-004 — Virtual Desktop Fallback Providers
Implementation: Fallback to Microsoft Official COM and hotkey emulation when internal COM fails
Source File:    app/providers/official_com_provider.py, app/providers/keyboard_fallback_provider.py
Test:           tests/test_workspace_scenarios.py::test_scenario_5_app_fails_graceful_recovery
Status:         PASS
```

---

### 2.2 Application Discovery & Launch Management (REQ-APP)

```text
Requirement:    REQ-APP-001 — 7-Layer Application Resolution Strategy
Implementation: Multi-tier heuristic resolver (Path -> Process -> Shortcut -> Registry -> Template -> Env -> Wildcard)
Source File:    app/discovery/app_detector.py
Test:           tests/test_workspace_scenarios.py::test_scenario_1_fresh_launch_creates_required_desktops
Status:         PASS
```

```text
Requirement:    REQ-APP-002 — Three Distinct Application Launch Modes
Implementation: Enums LAUNCH_IF_MISSING, ALWAYS_LAUNCH, REUSE_ONLY with execution enforcement
Source File:    app/models/workspace.py, app/core/execution_plan.py
Test:           tests/test_workspace_scenarios.py::test_scenario_3_already_running_apps_reused
Status:         PASS
```

```text
Requirement:    REQ-APP-003 — Shell Injection Prevention
Implementation: Tokenized subprocess execution without shell=True or command interpreters
Source File:    app/services/process_service.py
Test:           tests/test_workspace_scenarios.py::test_scenario_1_fresh_launch_creates_required_desktops
Status:         PASS
```

```text
Requirement:    REQ-APP-004 — Never Kill Running Processes
Implementation: Absolute prohibition of process termination; timeouts logged without killing
Source File:    app/services/process_service.py
Test:           tests/test_workspace_scenarios.py::test_scenario_5_app_fails_graceful_recovery
Status:         PASS
```

---

### 2.3 Window Management & Placement (REQ-WIN)

```text
Requirement:    REQ-WIN-001 — Top-Level Window Filtering
Implementation: Win32 style and dimension filter (WS_VISIBLE, non-zero size, not WS_EX_TOOLWINDOW)
Source File:    app/services/window_service.py
Test:           tests/test_window_matching.py::test_filter_invisible_and_tool_windows
Status:         PASS
```

```text
Requirement:    REQ-WIN-002 — Multi-Window Policy Matching
Implementation: Policies MAIN_ONLY, ALL_MATCHING, TITLE_CONTAINS, TITLE_REGEX
Source File:    app/services/window_service.py
Test:           tests/test_window_matching.py::test_window_title_matching_policies
Status:         PASS
```

```text
Requirement:    REQ-WIN-003 — Stale HWND & PID Revalidation
Implementation: Immediate pre-move validation via Win32 IsWindow(hwnd) and image path comparison
Source File:    app/services/window_service.py
Test:           tests/test_window_matching.py::test_stale_hwnd_revalidation
Status:         PASS
```

```text
Requirement:    REQ-WIN-004 — Multiple Applications Per Desktop
Implementation: Grouping multiple distinct applications to the same target desktop index
Source File:    app/core/execution_plan.py
Test:           tests/test_workspace_scenarios.py::test_scenario_7_multiple_apps_on_single_desktop
Status:         PASS
```

---

### 2.4 Persistence, Configuration & Safety (REQ-CFG)

```text
Requirement:    REQ-CFG-001 — Atomic JSON File Replacement
Implementation: Write to tempfile in target folder and replace atomically via os.replace
Source File:    app/configuration/config_store.py
Test:           tests/test_config.py::test_atomic_save_and_reload
Status:         PASS
```

```text
Requirement:    REQ-CFG-002 — Rolling Backups Retention
Implementation: Retain workspace.backup.json and up to 5 historical timestamped snapshots
Source File:    app/configuration/config_store.py
Test:           tests/test_config.py::test_backup_creation_and_rotation
Status:         PASS
```

```text
Requirement:    REQ-CFG-003 — Schema Validation & Migration
Implementation: Strict range/type checking with automatic v0 -> v1 profile migration
Source File:    app/configuration/validator.py, app/configuration/migration.py
Test:           tests/test_config.py::test_config_validation_rules, tests/test_config.py::test_migration_v0_to_v1
Status:         PASS
```

```text
Requirement:    REQ-CFG-004 — Crash Marker Detection
Implementation: Write marker on execution start, unlink on completion, prompt on recovery
Source File:    app/configuration/config_store.py
Test:           tests/test_config.py::test_crash_marker_lifecycle
Status:         PASS
```

---

### 2.5 User Interface & Entry Points (REQ-UI)

```text
Requirement:    REQ-UI-001 — Dedicated Configure Entry Point
Implementation: CLI flag --config and standalone configure.py opening management GUI
Source File:    configure.py, app/main.py
Test:           tests/test_cli.py::test_parse_args_defaults
Status:         PASS
```

```text
Requirement:    REQ-UI-002 — Dedicated Run Workspace Entry Point
Implementation: CLI flag --run and standalone run_workspace.py executing active profile
Source File:    run_workspace.py, app/main.py
Test:           tests/test_cli.py::test_parse_args_run_mode
Status:         PASS
```

```text
Requirement:    REQ-UI-003 — Two Owned Desktop Shortcuts
Implementation: ShortcutService creating and safely removing owned Desktop shortcuts
Source File:    app/services/shortcut_service.py
Test:           tests/test_shortcut_service.py::test_shortcut_service_creation_and_check
Status:         PASS
```

```text
Requirement:    REQ-UI-004 — Preserve Unrelated Desktop Shortcuts
Implementation: ShortcutService unlink restricted strictly to owned filenames
Source File:    app/services/shortcut_service.py
Test:           tests/test_shortcut_service.py::test_shortcut_service_safe_removal_preserves_unrelated
Status:         PASS
```

```text
Requirement:    REQ-UI-005 — Non-Mutating Dry-Run Preview
Implementation: DryRunSimulator calculating changes without executing system modifications
Source File:    app/core/dry_run.py
Test:           tests/test_workspace_scenarios.py::test_scenario_11_dry_run_zero_modifications
Status:         PASS
```

```text
Requirement:    REQ-UI-006 — Sanitized Privacy-Redacted Diagnostics
Implementation: DiagnosticsService redacting usernames, tokens, and private paths
Source File:    app/services/diagnostics_service.py
Test:           tests/test_diagnostics.py::test_diagnostics_generation_and_redaction
Status:         PASS
```
