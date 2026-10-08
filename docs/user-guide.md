# Virtual Desktop Workspace Manager — User Guide

## 1. Overview

**Virtual Desktop Workspace Manager** is a reliable Windows 10/11 desktop utility designed to organize, launch, monitor, and synchronize application windows across Windows Virtual Desktops.

Key capabilities:
- Assign one or multiple applications to specific Virtual Desktops.
- Add and configure applications dynamically without modifying source code.
- Prevent duplicate launches by detecting already-running processes and existing windows.
- Perform safe **Dry Run** simulations before changing any system state.
- Audit past executions with persistent operation history and redacted structured logs.
- Strictly safe: never kills processes, never uninstalls apps, never deletes user files or desktops, and operates completely offline.

---

## 2. System Requirements

- **Operating System:** Windows 10 (Build 19041+) or Windows 11 (64-bit recommended).
- **Python Runtime:** Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13, 3.14 supported).
- **Privileges:** Standard User (Medium Integrity) — Administrator / elevated privileges are not required and discouraged.
- **Network:** 100% Offline-capable. No network access or telemetry.

---

## 3. Getting Started

### 3.1 First-Run Experience
When launching the application for the first time, a setup wizard guides you through:
1. System compatibility and Windows build detection.
2. Virtual Desktop provider verification.
3. Enumeration of existing Virtual Desktops.
4. Setting up your default workspace profile.
5. Discovering and adding your daily development or productivity applications.
6. Saving configuration without immediately modifying your desktop state.

---

## 4. Main Interface & Navigation

The manager uses a 10-tab navigation system:

| Tab | Purpose | Primary Actions |
|---|---|---|
| **Dashboard** | Overview of workspace health, active desktop, and quick stats | `Launch Workspace`, `Sync Workspace`, `Dry Run`, `Refresh` |
| **Workspaces** | Visual layout of virtual desktops and assigned applications | `Open Desktop`, `Rename Desktop`, `+ Add App`, `Move to...` |
| **Applications** | Searchable table of all applications across all desktops | `Edit`, `Reassign`, `Test Match`, `Remove` |
| **Virtual Desktops** | Mapping table between workspace desktops and Windows desktops | `Refresh Desktops`, `Switch View`, `+ Create Desktop` |
| **Execution & Plan** | Reviewable pre-execution plan and live execution task checklist | `Review Dry Run Plan`, `Run Workspace`, `Stop` |
| **History** | Persistent audit log of past runs with durations and outcomes | `Copy Operation ID`, `Rerun as Dry Run`, `Clear History` |
| **Logs** | Live structured log viewer with automatic secret redaction | `Search`, `Level Filters`, `Export Logs`, `Open Folder` |
| **Diagnostics** | Health checks across 10 categories, crash recovery, support bundles | `Run Health Check`, `Generate Support Bundle` |
| **Settings** | Configuration preferences, timing bounds, and safety switches | `Save Settings`, `Reset to Defaults` |
| **About** | System details, license, and keyboard shortcut reference | Runtime details, provider status |

---

## 5. Daily Workflows

### 5.1 Launch Workspace
- **What it does:** Ensures the target number of Virtual Desktops exist, checks each configured application, launches applications that are not running (if launch mode allows), waits for application windows to appear, and moves windows to their designated Virtual Desktops.
- **Safety guarantee:** Existing running instances are reused where configured; no application is killed.

### 5.2 Sync Workspace
- **What it does:** Reconciles running application windows to their configured Virtual Desktops without launching any missing applications.
- **When to use:** When you already have apps open and want to reorganize them into their proper desktops.

### 5.3 Dry Run
- **What it does:** Simulates what `Launch Workspace` would do, evaluating process detection and window placement rules.
- **Safety guarantee:** 100% read-only; no windows are moved, no processes launched, no desktops created.

---

## 6. Managing Applications

### 6.1 Adding Applications
Click **+ Add Application** from the Dashboard or Workspaces tab:
- **Browse for EXE:** Select any `.exe`, `.bat`, or `.cmd` file.
- **Detect Running:** Pick from currently active application windows.
- **Use Template:** Choose from pre-configured templates for common tools (Brave, VS Code, Git Bash, Postman, Docker, SSMS, etc.).

### 6.2 Window Matching Policies
Under **Window Policy** in application settings:
- **Move main window only:** Identifies the primary top-level window.
- **Move all matching windows:** Moves all windows owned by the process.
- **Match window title contains:** Matches windows whose titles contain specific text (e.g., `GitHub`).
- **Match window title regex:** Matches windows using a regular expression.

### 6.3 Diagnostic Test Match Tool
Click **🔍 Test Match** in the application editor or Applications table to evaluate your matching rules against active processes and windows. Shows confidence score, PID, HWND, and current desktop without moving anything.

---

## 7. Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+S` | Save configuration changes |
| `Ctrl+R` or `F5` | Refresh all detections and status badges |
| `Ctrl+F` | Jump to Applications tab and focus search bar |
| `Ctrl+L` | Jump to Logs tab |
| `Ctrl+,` | Jump to Settings tab |
| `Esc` | Clear search filters or close dialogs |

---

## 8. Diagnostics & Support Bundles

If you encounter unexpected behavior:
1. Open the **Diagnostics** tab.
2. Review the 10 subsystem categories (System, Virtual Desktops, Provider, Configuration, Applications, Windows, Permissions, Storage, Dependencies, Recent Errors).
3. Click **🩺 Run Health Check** to verify all subsystems.
4. Click **📦 Generate Support Bundle** to produce a sanitized `.zip` archive containing diagnostic reports, redacted logs, and system details suitable for sharing with engineers.
