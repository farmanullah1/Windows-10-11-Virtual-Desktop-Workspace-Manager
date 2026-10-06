# Safety Review & Invariant Enforcement — Windows Virtual Desktop Workspace Manager

This document provides a systematic review of the safety guardrails, invariants, failure mitigation policies, and security protections implemented in the **Windows Virtual Desktop Workspace Manager**.

---

## 1. Prime Directive: Non-Destructive Operation

The application enforces absolute non-destructive operation at all architectural layers:

```text
PROHIBITED ACTIONS (Hard Invariants):
❌ Never kill, terminate, or abort application processes.
❌ Never delete, remove, or close user-created Virtual Desktops.
❌ Never delete user files, projects, or source code.
❌ Never silently elevate privileges to Administrator.
❌ Never enable automatic startup without explicit user opt-in.
❌ Never touch or delete unrelated Desktop shortcuts.
```

---

## 2. Comprehensive Safety Review Matrix

| Risk Scenario | Potential Consequence | Architectural Mitigation | Code Location | Status |
| --- | --- | --- | --- | --- |
| **Duplicate Application Instances** | Spawning redundant browser or IDE instances consuming heavy RAM. | Process enumeration via `psutil` + top-level window detection before launch when policy is `LAUNCH_IF_MISSING`. | `app/core/execution_plan.py` | **ENFORCED** |
| **Duplicate Virtual Desktops** | Cluttering user's Task View with redundant desktops on repeated launches. | Pre-flight enumeration of existing desktops. New desktops are created incrementally only when $M < N$. | `app/core/execution_plan.py` | **ENFORCED** |
| **Wrong Window Manipulation** | Moving an unrelated window belonging to a different application. | Triple verification: HWND validity, owning PID image path comparison, and window class/title policy matching. | `app/services/window_service.py` | **ENFORCED** |
| **Stale Window Handle (HWND)** | Attempting to move a window that was closed during execution, causing COM crash. | Handle revalidation using Win32 `IsWindow(hwnd)` immediately before issuing COM move commands. | `app/services/window_service.py` | **ENFORCED** |
| **PID Reuse Race Condition** | OS recycling a process ID after an application exits, targeting another process. | Full executable path verification via `QueryFullProcessImageNameW` ensures PID still belongs to target application. | `app/services/process_service.py` | **ENFORCED** |
| **Missing Application Executable** | User configured an invalid path or uninstalled a tool, blocking execution. | Bounded 7-layer discovery; if completely unresolvable, logs a warning and cleanly skips application without failing whole workspace. | `app/discovery/app_detector.py` | **ENFORCED** |
| **API Failure / COM Hang** | Windows COM interface freezes or returns RPC error. | Bounded timeouts, non-blocking worker threads, and capability checks (`is_available()`). | `app/providers/windows_vda_provider.py` | **ENFORCED** |
| **API Incompatibility Across Windows Builds** | Windows update changes COM vtable offsets, causing crashes. | Multi-tier provider abstraction: graceful fallback from `WindowsVdaProvider` to `OfficialComDesktopManager` and hotkeys. | `app/providers/` | **ENFORCED** |
| **Configuration File Corruption** | Power loss or crash during file write corrupts `workspace.json`. | Atomic file writes (`tempfile` + atomic `os.replace`) plus automated rolling backups (max 5 snapshots). | `app/configuration/config_store.py` | **ENFORCED** |
| **Malicious / Unsafe Profile Import** | Importing a crafted JSON with command injection or malicious arguments. | Strict validation (`ConfigValidator`) preventing shell metacharacters, path traversal, and out-of-range parameters. | `app/configuration/validator.py` | **ENFORCED** |
| **Accidental Workspace Execution** | Workspace starts unexpectedly simply because the manager was opened. | Separation of concerns: Manager GUI (`--config`) is strictly inspection/config; execution requires explicit user trigger (`--run` or "Launch Workspace" button). | `app/main.py` | **ENFORCED** |
| **Unauthorized Startup Persistence** | Application stealthily creates Run keys in Windows Registry. | Startup registration requires explicit toggle in Settings; uses user-scoped `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. | `app/services/startup_service.py` | **ENFORCED** |
| **Privilege Escalation Vulnerability** | Application requesting Admin rights, expanding attack surface. | Standard user (Medium Integrity) execution strictly enforced; never manifests `requireAdministrator`. | `main.py`, `setup.py` | **ENFORCED** |
| **Data Loss / Accidental File Deletion** | Deleting user files or unlinking unrelated desktop shortcuts. | File modifications restricted to `%APPDATA%\VirtualDesktopWorkspaceManager`. Desktop shortcut manager touches only its 2 owned shortcut names. | `app/services/shortcut_service.py` | **ENFORCED** |
| **Accidental Desktop Deletion** | Cleanup routine destroying user's active workspaces. | Desktop deletion logic is completely absent from the execution engine. | `app/core/` | **ENFORCED** |
| **Process Termination** | Forcibly killing an unresponsive application process. | Process termination is strictly prohibited. If an app fails to respond, it is marked timed out in the execution report. | `app/services/process_service.py` | **ENFORCED** |

---

## 3. Shortcut Ownership & Clean Uninstallation

The two user-facing shortcuts maintain strict ownership tokens:

* `Virtual Desktop Workspace Manager — Configure.lnk`
* `Virtual Desktop Workspace Manager — Run Workspace.lnk`

When the user requests removal via Settings or uninstallation, the `ShortcutService` targets **only** these exact two filenames. All other items on the user's Desktop remain completely untouched.
