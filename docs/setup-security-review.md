# Setup & Bootstrap Security Review

## 1. Executive Summary

This document evaluates the security architecture, threat model, and safety boundaries of the **Virtual Desktop Workspace Manager** setup and bootstrap mechanism (`setup.py`), as specified in Section 83B through 83G of the engineering requirements.

The setup process prepares the application environment on Windows 10 and Windows 11 without executing application workspaces, launching third-party processes, modifying host virtual desktops, or escalating privileges.

---

## 2. Threat Model & Security Invariants

| Threat / Risk | Severity | Mitigation & Architecture Enforcement |
| :--- | :--- | :--- |
| **Accidental Workspace Execution** | Critical | `setup.py` contains **zero** workspace execution logic, process launcher calls, or window movement APIs. It cannot launch applications or alter virtual desktops. |
| **Privilege Escalation Abuse** | High | The setup runner operates entirely under **Standard User (Medium Integrity)** permissions. No `runas`, UAC triggers, or auto-elevation requests are made. |
| **Dependency Supply-Chain Tampering** | High | Dependencies are strictly pinned and declared in `requirements.txt`. `setup.py` never accepts arbitrary package names from untrusted configuration or remote endpoints. |
| **Destructive Shortcut Deletion** | High | `ShortcutService` uses deterministic names and ownership checks. Setup repair and uninstallation routines touch **only** application-owned shortcuts. Unrelated desktop shortcuts are never touched. |
| **User Configuration Overwrite** | High | Setup initializes `workspace.json` only if it does not already exist. Existing valid configurations and profiles are validated and preserved intact. |
| **State File Pollution** | Medium | Setup metadata is isolated in `%APPDATA%\VirtualDesktopWorkspaceManager\state\setup.json`, strictly separated from operational workspace configurations. |
| **Sensitive Data Exposure** | Medium | Setup logging writes to `logs/setup.log` with zero credential, token, or secret logging. User paths are sanitized. |
| **Remote Network Exposure** | Low | The setup runner is **100% offline-first**. Network access is only invoked if the user explicitly triggers pip package installation. No telemetry or analytics exist. |

---

## 3. Privilege & Execution Boundary

### 3.1 Standard User (Medium Integrity)

`setup.py` adheres to the principle of least privilege:

```text
Host Environment (Windows 10/11)
       │
       ▼
Standard User Account (Medium Integrity)
       │
       ├── Reads: Project directory, Python standard libraries
       ├── Writes: %APPDATA%\VirtualDesktopWorkspaceManager\
       │           ├── config (workspace.json, backups)
       │           ├── state (setup.json)
       │           └── logs (setup.log)
       └── Creates: User Desktop Shortcuts (.lnk)
```

No system directories (`C:\Windows`, `C:\Program Files`), elevated registries (`HKLM`), or Windows security policies are altered during setup.

---

## 4. Desktop Shortcut Ownership & Safety

The setup process creates exactly two user-facing desktop shortcuts:

1. **Virtual Desktop Workspace Manager — Configure**:
   * Target: Python interpreter / packaged executable
   * Arguments: `--config` (or `configure.py`)
   * Scope: Exclusively launches the configuration GUI. Never executes workspaces.

2. **Virtual Desktop Workspace Manager — Run Workspace**:
   * Target: Python interpreter / packaged executable
   * Arguments: `--run` (or `run_workspace.py`)
   * Scope: Executes the active workspace profile after validating saved configuration.

### 4.1 Ownership Rules

* **Deterministic File Naming**: Shortcuts are named `Virtual Desktop Workspace Manager — Configure.lnk` and `Virtual Desktop Workspace Manager — Run Workspace.lnk`.
* **Safe Repair**: Running `setup.py --repair` verifies target existence and recreates missing owned shortcuts without generating duplicates or altering unrelated `.lnk` files on the user's desktop.
* **Safe Uninstallation**: Removal routines filter strictly on owned filenames, ensuring complete safety for user desktop icons.

---

## 5. Setup State & Logging Isolation

* **Setup State**: Stored in `%APPDATA%\VirtualDesktopWorkspaceManager\state\setup.json`. Records application version, Python build, architecture, and timestamp. It is read-only for workspace engines and never serves as a secondary source of truth for workspace mappings.
* **Setup Logging**: Output is written to `%APPDATA%\VirtualDesktopWorkspaceManager\logs\setup.log`. Operational workspace logs remain isolated in daily timestamped files (`workspace_YYYYMMDD.log`).

---

## 6. Diagnostic & Verification Commands

The setup runner provides non-destructive inspection modes:

```cmd
python setup.py --check       # Non-destructive diagnostics (makes 0 changes)
python setup.py --version     # Displays setup runner version
python setup.py --help        # Displays supported CLI commands
python setup.py --repair      # Repairs only application-owned shortcuts and folders
```

All commands return `0` on success and non-zero exit codes on failure, enabling automated validation and CI/CD integration.
