# Windows Virtual Desktop Workspace Manager

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Platform Windows](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011%20(64--bit)-0078d4.svg)](https://microsoft.com)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-53%20passed-brightgreen.svg)](tests/)

A production-quality utility for **Windows 10 and Windows 11** that manages Windows Virtual Desktops and organizes your applications into persistent, customized virtual workspaces. Applications are automatically launched or moved to designated virtual desktops with zero destructive behavior, failure isolation, and transparent observability.

---

## 1. What the Application Does

* **Virtual Desktop Detection**: Detects currently available Windows Virtual Desktops using COM interop (`IVirtualDesktopManager` / Windows 10/11 VDA).
* **Safe Desktop Creation**: Automatically creates required virtual desktops up to your workspace layout; **never** deletes existing user desktops.
* **Intelligent Window Movement**: Identifies visible top-level windows and moves them to their assigned virtual desktop.
* **Process Pre-Detection**: Detects already running applications and reuses existing windows without spawning unnecessary duplicate processes.
* **Multi-App Desktop Layouts**: Allows assigning any number of applications to the same virtual desktop.
* **Non-Destructive Design**: Never terminates running processes, never uninstalls software, and never deletes user files or repositories.
* **Workspace Profiles**: Switch between dedicated profiles (e.g., Development, Database, Work, Personal) with one click.
* **Single-Instance Protection**: Enforces single-instance execution via Windows named mutex (`Local\VirtualDesktopWorkspaceManager_SingleInstance_Mutex`) and brings existing window to foreground on duplicate launches.
* **8-Point Health Check**: Built-in non-destructive diagnostic verification of Windows version, API providers, permissions, configuration, and logging storage.
* **Dry-Run Inspection**: Previews all pending actions without executing any changes.
* **Crash Recovery**: Detects incomplete operations and offers one-click state reconciliation.
* **Live Observability**: Live log panel with filtering, searching, and privacy-redacted diagnostic reports.

---

## 2. Supported Windows Versions

* **Windows 11 (64-bit)**: Builds 22000, 22621 (22H2), 22631 (23H2), 26100 (24H2), and 26300+ series.
* **Windows 10 (64-bit)**: Builds 19041 (2004), 19042 (20H2), 19043 (21H1), 19044 (21H2), 19045 (22H2).
* **Architecture**: 64-bit (x64) Windows required.

---

## 3. Requirements

* **Python**: 3.10 or newer (tested on Python 3.14).
* **Dependencies**:
  * `pyvda>=0.6.0` — Windows Virtual Desktop COM interop
  * `pywin32>=306` — Win32 window enumeration and shell shortcut resolution
  * `psutil>=5.9.0` — Process tree inspection
  * `comtypes>=1.4.0` — Microsoft COM interfaces
  * `pystray>=0.19.5` & `Pillow>=10.0.0` — System tray background controls
  * `pytest>=8.0.0` — Test suite runner

---

## 4. Installation

1. Clone or download the repository:

   ```cmd
   git clone "https://github.com/farmanullah1/Windows-10-11-Virtual-Desktop-Workspace-Manager.git"
   cd "Windows-10-11-Virtual-Desktop-Workspace-Manager"
   ```

2. Install dependencies:

   ```cmd
   pip install -r requirements.txt
   ```

3. (Optional) Install in development mode:

   ```cmd
   pip install -e .
   ```

### 4.1 System Setup & Bootstrap Runner (`run.py`)

For automated, idempotent environment initialization and shortcut setup, use the root-level setup runner:

```cmd
python run.py             # Perform complete idempotent setup
python run.py --setup     # Explicit setup mode
python run.py --check     # Non-destructive diagnostics (makes zero system changes)
python run.py --repair    # Verify and repair application-owned shortcuts and folders
python run.py --version   # Display setup runner version
```

> **Strict Guarantee (Section 83B):** `run.py` is exclusively a setup and bootstrap tool. It **never** executes the workspace, never launches configured applications, and never manipulates Windows Virtual Desktops.

---

## 5. First-Run Setup Wizard

Upon first launch, the manager displays an **8-step Setup Wizard**:

1. **Welcome**: Introduces safety principles and capabilities.
2. **Detect Virtual Desktops**: Verifies available virtual desktops.
3. **Configure Desktops**: Allows assigning custom names (Browser, Development, Database, API Testing).
4. **Detect Applications**: Scans system for installed development tools.
5. **Assign Applications**: Maps each tool to your chosen virtual desktop.
6. **Review**: Previews your layout.
7. **Save Configuration**: Writes configuration persistently to `%APPDATA%\VirtualDesktopWorkspaceManager`.
8. **Ready**: Completes setup. **Strict Guarantee**: Does **not** launch or alter any windows until you explicitly click "Launch Workspace".

---

## 6. Default Workspace Configuration

Out of the box, the manager configures a 4-desktop developer layout:

```text
Desktop 1 — Browser
 └── Brave Browser

Desktop 2 — Development
 └── Google Antigravity

Desktop 3 — Database
 └── SQL Server Management Studio (SSMS)

Desktop 4 — API Development
 └── Postman
```

All items are fully editable from the UI without modifying source code.

---

## 7. Adding Applications Later

You can add applications at any time through the UI:

1. Click **+ Add Application** on the main dashboard, or **+ Add App** on any specific desktop card.
2. Choose one of three discovery options:
   * **Template**: Select from built-in templates (Brave, Chrome, Edge, Firefox, VS Code, Visual Studio, Antigravity, SSMS, Postman, Docker Desktop, Terminal, Explorer).
   * **Detect Running**: Choose from a list of currently running visible application windows.
   * **Browse**: Select an `.exe` file using the Windows file picker.
3. Configure launch mode, window policy, and timeouts, then click **Save Application**.

---

## 8. Moving Applications Between Desktops

To change an application's desktop assignment:

1. On the application row, click **Move to...**.
2. Select the target desktop from the dropdown.
3. Check **Move currently running window immediately** if you want the window moved right away, or leave unchecked to apply on next workspace launch/sync.
4. Click **Save**.

---

## 9. Multiple Applications Per Desktop

Each virtual desktop can contain any number of applications:

```text
Desktop 2 — Development
 ├── Google Antigravity
 ├── Visual Studio Code
 └── Git Bash
```

Click **+ Add App** on Desktop 2 to add extra tools without disturbing existing assignments.

---

## 10. Workspace Profiles

Switch between completely distinct workspace layouts:

* **Development**: Browser on Desktop 1, IDE on Desktop 2, Database on Desktop 3, Postman on Desktop 4.
* **Work / Meetings**: Browser on Desktop 1, CRM on Desktop 2, Outlook on Desktop 3, Teams on Desktop 4.

Use the **Profile** dropdown in the header to switch active profiles, create new ones (`+`), or export/import them as `.json` files.

---

## 11. Dry-Run Mode

Before executing any desktop operations, click **🔍 Dry Run** to preview what would happen:

* Existing desktops vs required desktops.
* Which new desktops would be created.
* Which applications are already running and would have windows moved.
* Which applications are not running and would be launched.
* Any warnings for missing executables.
* **Guarantees zero modifications during dry-run.**

From the command line:

```cmd
python main.py --dry-run
# or
python configure.py --dry-run
```

---

## 12. Troubleshooting & Recovery

* **Window not moving?** Check if the application runs as Administrator. Due to Windows UIPI security, non-elevated managers cannot control elevated windows.
* **App executable missing?** Click **Edit** -> **Browse...** to specify the exact path.
* **Crash recovery?** If Windows restarted during a previous run, the manager detects the marker and prompts to run **Sync Workspace** to reconcile window positions safely.
* Refer to [docs/troubleshooting.md](docs/troubleshooting.md) for detailed diagnostics.

---

## 13. Two User-Facing Desktop Shortcuts

The application provides two separate user-facing Desktop shortcuts with dedicated purposes and strict ownership boundaries:

1. **Virtual Desktop Workspace Manager — Configure**:
   * Command: `python main.py --config` (or `python configure.py`)
   * Purpose: Exclusively opens the graphical configuration/management interface.
   * Safety Guarantee: Never launches workspaces, creates virtual desktops, or moves application windows.

2. **Virtual Desktop Workspace Manager — Run Workspace**:
   * Command: `python main.py --run` (or `python run_workspace.py`)
   * Purpose: Explicitly executes the currently active workspace profile using persisted configuration.
   * Prompts for confirmation if configured (`prompt_before_launch`), launches missing applications, and assigns windows to their virtual desktops.

### Managing Desktop Shortcuts

* Via Settings: Open manager -> **Settings** -> **User Desktop Shortcuts** -> Click **Create Desktop Shortcuts** or **Remove Owned Shortcuts**.
* Via CLI:

  ```cmd
  python main.py --create-shortcuts    # Create both owned shortcuts on Desktop
  python main.py --remove-shortcuts    # Remove owned shortcuts safely
  ```

* Ownership Guarantee: Removal and maintenance routines strictly touch only these two owned shortcut files. Unrelated user shortcuts are never modified or deleted.

---

## 14. Diagnostics & 8-Point Health Check

The manager includes comprehensive, non-destructive diagnostic tools:

### Diagnostic Health Check

Click **Health Check** in the header toolbar, or run via CLI:

```cmd
python configure.py --health-check
# or
python main.py --health-check
```

Verifies all 8 critical subsystems:

```text
✓ Windows Supported: Windows 10/11 version and build verification
✓ Virtual Desktop Provider Available: COM / pyvda provider readiness
✓ Configuration Valid: Schema and data integrity validation
✓ Desktop Mappings Valid: Validates desktop target numbers
✓ Applications Detected: Locates configured executables on disk
✓ Permissions Sufficient: Verifies Standard User (Medium Integrity)
✓ Configuration Storage Writable: Checks %APPDATA% storage access
✓ Logging Storage Writable: Verifies log directory writability
```

### About Dialog

Click **About** in the header toolbar to view:

* Version and production build details.
* Python runtime architecture and Windows build string.
* Active desktop, process, and window provider backends.
* MIT License and security integrity level.
* Direct shortcut to run the Health Check.

### Live Operation Logs

* Logs are written daily to: `%APPDATA%\VirtualDesktopWorkspaceManager\logs\workspace_YYYYMMDD.log`.
* View live streaming logs with level filtering and search in the bottom panel of the GUI.
* Click **Export Diagnostics** to produce a complete system report (`workspace_diagnostics.txt`) with all passwords, tokens, API keys, and usernames automatically redacted.

---

## 15. Known Windows Limitations

Refer to [docs/limitations.md](docs/limitations.md) and [docs/windows-api-compatibility.md](docs/windows-api-compatibility.md) for detailed coverage of:

* Documented vs undocumented COM interfaces across Windows builds.
* Handling Chromium/Electron multi-process helper processes.
* Windows User Interface Privilege Isolation (UIPI).

---

## 16. Security & Safety

* **No Administrator Required**: Operates with standard user permissions.
* **No Command Injection**: Safe tokenized argument passing; `shell=True` is prohibited.
* **No File Deletion**: Never modifies source code, git repositories, or user files.
* **100% Offline**: Zero telemetry, analytics, or external network requests.
* Refer to [docs/safety-review.md](docs/safety-review.md) and [docs/security-review.md](docs/security-review.md) for complete evaluations.

---

## 17. Running the Application

### Running Manually from Source

```cmd
python main.py                     # Open Configuration GUI
python configure.py                # Dedicated Configure entry point
python run_workspace.py            # Dedicated Run Workspace entry point
```

### Command-Line Arguments

```cmd
python main.py --config           # Open Configuration GUI (default)
python main.py --run              # Execute active workspace profile
python main.py --dry-run          # Print dry run preview and exit
python main.py --sync             # Reconcile window positions and exit
python main.py --health-check     # Run 8-point system diagnostic health check
python main.py --minimized        # Start minimized to system tray
python main.py --profile "Work"   # Activate a specific profile
python main.py --create-shortcuts # Install user Desktop shortcuts
python main.py --remove-shortcuts # Cleanly uninstall Desktop shortcuts
python main.py --no-prompt        # Skip confirmation prompt for --run
python main.py --headless         # Run in headless mode without GUI popups
```

### Packaging into a Standalone EXE

```cmd
pyinstaller --noconsole --onefile --name "VirtualDesktopWorkspaceManager" --add-data "config/default_workspace.json;config" main.py
```

Output executable will be in `dist/VirtualDesktopWorkspaceManager.exe`. See [docs/packaging.md](docs/packaging.md) for details.

---

## 18. Automated Test Suite

The application includes a comprehensive test suite of **53 unit, integration, acceptance, and setup tests**:

```cmd
python -m pytest -v
```

### Test Suite Safety Guarantees

* **100% Non-Destructive**: All tests execute using isolated mock providers (`MockVirtualDesktopProvider`, `MockProcessProvider`, `MockWindowProvider`, `MockApplicationLauncher`).
* **Zero Real Processes**: No third-party tools, browsers, or editors are launched during testing.
* **Zero Virtual Desktop Alterations**: Host virtual desktops are never touched or switched.
* **Isolated Temporary Directories**: All configuration, logging, setup state, and shortcut tests use isolated temporary folders that are automatically cleaned up.
* **Acceptance Coverage**: Tests all 8 desktop shortcut acceptance scenarios, window matching policies, single-instance mutex locks, configuration atomic writes, setup bootstrap idempotency, and crash recovery.

---

## 19. Technical Documentation Index

* [Architecture Specification](docs/architecture.md)
* [Requirements Analysis](docs/requirements-analysis.md)
* [Technology Decision Record](docs/technology-decision.md)
* [Configuration Schema Reference](docs/configuration-schema.md)
* [Windows API Compatibility & Fallbacks](docs/windows-api-compatibility.md)
* [Safety Review & Invariants](docs/safety-review.md)
* [Security Review & UIPI](docs/security-review.md)
* [Setup Security Review](docs/setup-security-review.md)
* [Known Windows Limitations](docs/limitations.md)
* [Packaging & Standalone Guide](docs/packaging.md)
* [Troubleshooting Guide](docs/troubleshooting.md)
* [Final Engineering Review](docs/final-review.md)
* [Requirements Traceability Matrix](docs/requirements-traceability.md)

---

## 20. Uninstalling

To uninstall:

1. In manager **Settings**, uncheck **Start Workspace Manager with Windows**.
2. Click **Remove Owned Shortcuts** in Settings (or run `python main.py --remove-shortcuts`).
3. Delete the application directory.
4. If you wish to remove your saved configurations and logs, delete:

   ```cmd
   %APPDATA%\VirtualDesktopWorkspaceManager
   ```
