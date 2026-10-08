# Test Strategy & Quality Assurance Architecture

## 1. Quality Objectives

The test strategy ensures that **Virtual Desktop Workspace Manager** is 100% reliable, deterministic, and safe under all operating conditions while strictly adhering to the **Development Execution Boundary** (Section 0.2 & Section 98):

> **Absolute Boundary:** During development and testing, tests must execute against isolated mock providers. Under no circumstances should test suites spawn real user applications, create or delete real Virtual Desktops, or modify host window placement.

---

## 2. Test Architecture Layers

```text
┌────────────────────────────────────────────────────────┐
│ UI View Tests (Mocked Tkinter components)              │
├────────────────────────────────────────────────────────┤
│ Scenario Acceptance Tests (11 User Scenarios)          │
├────────────────────────────────────────────────────────┤
│ Failure Injection Tests (Timeouts, Disconnects)        │
├────────────────────────────────────────────────────────┤
│ Fuzz & Robustness Tests (Malformed inputs, edge cases) │
├────────────────────────────────────────────────────────┤
│ Provider Contract Tests (Interface verification)       │
├────────────────────────────────────────────────────────┤
│ Unit Tests (Configuration, Redaction, Shortcuts, CLI)  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Test Suites Overview

### 3.1 Unit Test Suite
- **`test_config.py`**: Configuration loading, validation, schema migration, and default profile construction.
- **`test_cli.py`**: Command-line interface argument parsing, flags (`--sync`, `--dry-run`, `--profile`), and output formatting.
- **`test_redactor_and_error_catalog.py`**: Automatic masking of passwords, tokens, API keys, and error catalog code resolution.
- **`test_single_instance.py`**: Mutex-based single instance enforcement and secondary instance handoff.
- **`test_support_bundle_and_categories.py`**: 10-category health check parsing and redacted support bundle ZIP packaging.

### 3.2 Provider Contract Tests
- Verifies that all `IVirtualDesktopProvider`, `IProcessProvider`, `IWindowProvider`, and `IApplicationLauncher` implementations conform to identical contracts and error behaviors.

### 3.3 Acceptance Scenario Tests (`test_workspace_scenarios.py`)
Covers the core production scenarios:
1. Creating missing Virtual Desktops when insufficient exist.
2. Preserving desktop count when sufficient desktops exist.
3. Preserving extra user-created Virtual Desktops.
4. Reusing running applications without duplicate process launches.
5. Launching missing applications and placing windows.
6. Isolating failures when an uninstalled app is missing without aborting the run.
7. Assigning multiple applications to a single desktop.
8. Reassigning applications between desktops.
9. Dynamically adding new applications to an active profile.
10. Idempotent re-runs producing identical stable states.
11. Emergency STOP cooperative cancellation without process termination.

### 3.4 Failure Injection & Robustness
- Injects missing executable paths, window timeout expirations, COM provider failures, and malformed configuration JSON strings.

### 3.5 UI View Tests (`test_ui_views.py`)
- Instantiates `MainWindow` in headless mode, tests 10 tab indices, table selection, search filtering, unsaved change tracking, and shortcut callbacks.
