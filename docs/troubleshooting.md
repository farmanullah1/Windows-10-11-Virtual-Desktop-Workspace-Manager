# Troubleshooting Guide

This guide covers common issues and resolution procedures for the Windows Virtual Desktop Workspace Manager.

---

## 1. Application Executable Not Located

### Symptoms

* A warning icon `⚠` appears next to the application on the dashboard or desktop card.
* Logs show: `Executable not found at ...`

### Resolutions

1. **Browse for EXE**: Click **Edit** on the application card and click **Browse...** to pick the `.exe` directly.
2. **Use Detect Running**: Open the application manually, then in the manager click **+ Add App** -> **Detect Running...** and select the running process from the list.
3. **Environment Variables**: Verify paths use proper Windows variables (e.g. `%LocalAppData%`, `%ProgramFiles%`, `%ProgramFiles(x86)%`).

---

## 2. Window Does Not Move to Target Desktop

### Symptoms

* Process launches or is running, but the window remains on the current virtual desktop.
* Log warns: `Timed out waiting for visible window for ...`

### Causes & Resolutions

1. **Multi-Process Architecture (Browsers / Electron Apps)**:
   * Browsers like Brave or Chrome launch multiple renderer helper processes (`brave.exe --type=renderer`).
   * The manager inspects the main top-level visible window. If the application takes longer to render its main window, increase the **Window Timeout (ms)** in the app settings (e.g., from 15,000 ms to 25,000 ms).
2. **Elevated Applications**:
   * If an application is running as Administrator (High Integrity), a non-elevated application cannot interact with its HWND due to Windows UIPI (User Interface Privilege Isolation).
   * **Fix**: Run the application at standard user permissions, or launch the workspace manager with matching privileges.
3. **Window Matching Policy**:
   * If an application has dynamic window titles or splash screens, set **Window Policy** to `Move all matching windows` or configure a specific `Title Pattern`.

---

## 3. Windows Virtual Desktop API & Build Compatibility

### Symptoms

* Desktop count reports 1 or fails to switch.
* Log shows COM interface warnings.

### Explanation

Windows Virtual Desktop management relies on Windows internal COM interfaces (`IVirtualDesktopManagerInternal` and `IVirtualDesktopManager`). Microsoft occasionally updates internal COM GUIDs across major Windows 11 feature updates (e.g. 24H2 / 26xxx builds).

### Resolutions

1. **Verify Official COM Status**: Click **View Logs** -> **Export Diagnostics** to inspect COM interface initialization.
2. **Fallback Mechanism**: The manager includes `OfficialComDesktopManager` and `KeyboardFallbackProvider` to preserve essential movement functionality when internal interfaces evolve.

---

## 4. Recovering from an Incomplete Operation (Crash Recovery)

### Symptoms

* Upon opening the manager, a prompt appears: `"Previous workspace operation may not have completed."`

### Resolutions

1. This occurs if Windows restarted, was powered off, or the manager was abruptly stopped while a launch sequence was executing.
2. Click **Sync Workspace** in the prompt to reconcile all window positions without relaunching unnecessary duplicate applications.

---

## 5. Generating and Sharing Diagnostics

When reporting an issue:

1. Open the **Live Operation Logs** panel at the bottom of the manager.
2. Click **Export Diagnostics**.
3. Save `workspace_diagnostics.txt`. The report automatically redacts passwords, tokens, API keys, and usernames.
