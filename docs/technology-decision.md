# Technology Decision Record — Windows Virtual Desktop Workspace Manager

This document records the architectural evaluation and technology selection rationale for the **Windows Virtual Desktop Workspace Manager**.

---

## 1. Context and Problem Statement

Windows Virtual Desktops require low-level integration with the Windows operating system:

1. COM interop with both official Microsoft interfaces (`IVirtualDesktopManager`) and internal shell interfaces (`IVirtualDesktopManagerInternal`).
2. Win32 window enumeration, style filtering (`WS_VISIBLE`, `WS_EX_TOOLWINDOW`), and handle revalidation.
3. Process inspection and child-process tree resolution.
4. Clean graphical user interface that runs on Windows 10 and Windows 11 without requiring Administrator privileges or massive external frameworks.
5. Absolute safety: zero destructive behavior, mock-driven non-destructive testability, and isolated deployment.

---

## 2. Alternatives Considered

| Technology Candidate | Advantages | Disadvantages | Decision |
| --- | --- | --- | --- |
| **Python 3.10+ (Selected)** | Direct Win32/COM bindings (`pywin32`, `pyvda`, `comtypes`), fast iteration, native Tkinter UI without extra runtimes, isolated unit/mock testability, single-file PyInstaller packaging. | Minor startup overhead compared to pure C++. | **SELECTED** |
| **C# / .NET 8 (WPF / WinUI 3)** | Native COM interop via CsWinRT, modern Windows 11 Fluent controls. | Requires .NET Desktop Runtime or large 90MB+ self-contained distribution; WinUI 3 has complex MSIX/appx packaging requirements and Windows 10 version gates. | Rejected |
| **C++ / Win32 Native** | Zero dependency, minimal memory footprint. | High complexity for GUI event handling, profile migrations, JSON schema validation, and mocking; prone to memory bugs during rapid development. | Rejected |
| **Rust (`windows-rs`)** | High memory safety, fast execution. | GUI ecosystem on Windows (e.g. `iced`, `slint`) lacks mature native Windows 11 theming; COM vtable bindings for undocumented interfaces require substantial manual FFI scaffolding. | Rejected |
| **Electron / Node.js** | Familiar web UI technologies. | 150MB+ bundle size, 200MB+ RAM consumption; Node.js native Win32/COM bindings (`win32-api`) require node-gyp C++ compilation and frequent rebuilds across Node versions. | Rejected |

---

## 3. Technology Stack Breakdown

### 3.1 Core Language and Runtime

* **Language**: Python 3.10+ (tested on Python 3.14.5 64-bit on Windows 11 Pro).
* **Rationale**: Strong typing via `typing` / `dataclasses`, native JSON schema support, battle-tested standard library, and rock-solid Win32 ecosystem.

### 3.2 Win32 & COM Interop Libraries

* **`pyvda` (>= 0.6.0)**:
  * Purpose: Encapsulates Windows 10 and Windows 11 COM virtual desktop internal interfaces (`IVirtualDesktopManagerInternal`, `IVirtualDesktopNotification`).
  * Safety: Isolated behind our `IVirtualDesktopProvider` interface; if COM fails, gracefully falls back to official Microsoft COM or hotkey emulation.
* **`pywin32` (>= 306)**:
  * Purpose: Provides access to `win32gui`, `win32process`, `win32api`, `win32con`, and shell shortcut resolution via `win32com.client`.
  * Capabilities: Safe window enumeration, style filtering, and process path resolution without elevated access.
* **`comtypes` (>= 1.4.0)**:
  * Purpose: Direct pure-Python COM client for official Microsoft `IVirtualDesktopManager` GUID interfaces.
* **`psutil` (>= 5.9.0)**:
  * Purpose: High-performance process inspection, command-line inspection, executable path resolution, and child process trees without invoking shell processes.

### 3.3 User Interface Framework

* **Python `tkinter` / `ttk` with Windows 11 Fluent Design System Tokens**:
  * Purpose: Delivers a clean, responsive, high-contrast GUI matching Windows 11 dark/light themes.
  * Rationale: Standard library module requiring zero third-party GUI packages; no external native DLL compilation or C++ build tools required.
  * Accessibility: Full keyboard navigation, high-contrast borders, WCAG AA compliant contrast ratios.

### 3.4 System Tray Integration

* **`pystray` (>= 0.19.5)** & **`Pillow` (>= 10.0.0)**:
  * Purpose: Non-intrusive background operation in system notification area when minimized.

### 3.5 Test Architecture

* **`pytest` (>= 8.0.0)**:
  * Purpose: Executes unit tests, property invariants, and scenario simulations.
  * Invariant: All automated tests run against `MockVirtualDesktopProvider`, isolated temporary directories, and mock processes to guarantee zero side-effects on host desktops.

---

## 4. Packaging and Distribution Strategy

* **PyInstaller (>= 6.0.0)**:
  * Single-file executable (`--onefile --noconsole`) or portable folder (`--onedir`).
  * Bundles default configuration template (`config/default_workspace.json`).
  * Dedicated entry points:
    * `VirtualDesktopWorkspaceManager.exe --config` (Configuration GUI)
    * `VirtualDesktopWorkspaceManager.exe --run` (Direct Workspace Execution)
