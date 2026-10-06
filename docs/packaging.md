# Application Packaging and Distribution Guide

This document describes how to package **Windows Virtual Desktop Workspace Manager** into a standalone Windows executable.

---

## 1. Prerequisites

1. **Python 3.10+ (64-bit)** installed on Windows.
2. Install project dependencies and PyInstaller:

   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

---

## 2. Packaging with PyInstaller

To build a standalone executable:

```cmd
pyinstaller --noconsole --onefile --name "VirtualDesktopWorkspaceManager" --add-data "config/default_workspace.json;config" main.py
```

### Build Parameters Explained

* `--noconsole`: Hides the command-prompt window so the application runs as a clean desktop GUI.
* `--onefile`: Bundles the Python runtime, dependencies (`pyvda`, `pywin32`, `psutil`, `pystray`), and assets into a single `.exe` file.
* `--name`: Sets the output binary name in the `dist/` directory (`dist/VirtualDesktopWorkspaceManager.exe`).
* `--add-data`: Copies the initial default workspace configuration template into the bundle.

---

## 3. Running in Development Mode

To run directly from source without packaging:

```cmd
python main.py
```

### Available CLI Flags

* `python main.py --dry-run` — Runs pre-flight dry run preview in the console without opening GUI.
* `python main.py --sync` — Reconciles window positions non-interactively and exits.
* `python main.py --minimized` — Starts the GUI minimized to the system tray.
* `python main.py --profile "Development"` — Activates a specific profile on startup.
