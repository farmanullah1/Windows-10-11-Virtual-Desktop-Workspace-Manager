# Windows Virtual Desktop Workspace Manager

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Platform Windows](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011%20(64--bit)-0078d4.svg)](https://microsoft.com)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-quality utility for **Windows 10 and Windows 11** that manages Windows Virtual Desktops and organizes your applications into persistent, customized virtual workspaces. Applications are automatically launched or moved to designated virtual desktops with zero destructive behavior, failure isolation, and transparent observability.

---

## 1. What the Application Does

* **Virtual Desktop Detection**: Detects currently available Windows Virtual Desktops.
* **Safe Desktop Creation**: Automatically creates required virtual desktops up to your workspace layout; **never** deletes existing user desktops.
* **Intelligent Window Movement**: Identifies visible top-level windows and moves them to their assigned virtual desktop.
* **Process Pre-Detection**: Detects already running applications and reuses existing windows without spawning unnecessary duplicate processes.
* **Multi-App Desktop Layouts**: Allows assigning any number of applications to the same virtual desktop.
* **Non-Destructive Design**: Never terminates running processes, never uninstalls software, and never deletes user files or repositories.
* **Workspace Profiles**: Switch between dedicated profiles (e.g., Development, Database, Work, Personal) with one click.
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
   git clone "https://github.com/your-username/virtual-desktop-workspace-manager.git"
   cd "Virtual Desktop Workspace Manager"
   ```

2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

3. (Optional) Install in development mode:
   ```cmd
   pip install -e .
   ```

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

---

## 12. Troubleshooting & Recovery

* **Window not moving?** Check if the application runs as Administrator. Due to Windows UIPI security, non-elevated managers cannot control elevated windows.
* **App executable missing?** Click **Edit** -> **Browse...** to specify the exact path.
* **Crash recovery?** If Windows restarted during a previous run, the manager detects the marker and prompts to run **Sync Workspace** to reconcile window positions safely.
* Refer to [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed diagnostics.

---

## 13. Logs & Diagnostics

* Logs are written daily to: `%APPDATA%\VirtualDesktopWorkspaceManager\logs\workspace_YYYYMMDD.log`.
* View live streaming logs with level filtering and search in the bottom panel of the GUI.
* Click **Export Diagnostics** to produce a complete system report (`workspace_diagnostics.txt`) with all passwords, tokens, API keys, and usernames automatically redacted.

---

## 14. Known Windows Limitations

Refer to [docs/LIMITATIONS.md](docs/LIMITATIONS.md) for detailed coverage of:
* Documented vs undocumented COM interfaces.
* Handling Chromium/Electron multi-process helper processes.
* Windows User Interface Privilege Isolation (UIPI).

---

## 15. Security & Safety

* **No Administrator Required**: Operates with standard user permissions.
* **No Command Injection**: Safe tokenized argument passing; `shell=True` is prohibited.
* **No File Deletion**: Never modifies source code, git repositories, or user files.
* **100% Offline**: Zero telemetry, analytics, or external network requests.
* Refer to [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md) for the full security evaluation.

---

## 16. Running the Application

### Running Manually from Source
```cmd
python main.py
```

### Command-Line Arguments
```cmd
python main.py --dry-run          # Print dry run preview and exit
python main.py --sync             # Reconcile window positions and exit
python main.py --minimized        # Start minimized to system tray
python main.py --profile "Work"   # Start with a specific profile
```

### Packaging into a Standalone EXE
```cmd
pyinstaller --noconsole --onefile --name "VirtualDesktopWorkspaceManager" --add-data "config/default_workspace.json;config" main.py
```
Output executable will be in `dist/VirtualDesktopWorkspaceManager.exe`.

---

## 17. Uninstalling

To uninstall:
1. In manager **Settings**, uncheck **Start Workspace Manager with Windows**.
2. Delete the application directory.
3. If you wish to remove your saved configurations and logs, delete:
   ```cmd
   %APPDATA%\VirtualDesktopWorkspaceManager
   ```
