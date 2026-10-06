# Windows API Compatibility & Interop Specification

This document details all Windows Win32 APIs, COM interfaces, third-party interop libraries, operating system compatibility baselines, risks, and fallback mechanisms implemented in the **Windows Virtual Desktop Workspace Manager**.

---

## 1. Supported Windows Versions

| Windows Edition | Build Numbers | Status | Provider Support |
| --- | --- | --- | --- |
| **Windows 11 (24H2)** | Build 26100+ | Fully Supported | `WindowsVdaProvider` + `OfficialComDesktopManager` |
| **Windows 11 (23H2 / 22H2)** | Build 22621, 22631 | Fully Supported | `WindowsVdaProvider` + `OfficialComDesktopManager` |
| **Windows 11 (21H2)** | Build 22000 | Fully Supported | `WindowsVdaProvider` + `OfficialComDesktopManager` |
| **Windows 10 (22H2 / 21H2)** | Build 19044, 19045 | Fully Supported | `WindowsVdaProvider` + `OfficialComDesktopManager` |
| **Windows 10 (Legacy < 1809)** | Build < 17763 | Degraded Mode | `OfficialComDesktopManager` + `KeyboardFallbackProvider` |

---

## 2. Windows Win32 APIs Used

All Win32 API interactions are executed through `pywin32` (`win32gui`, `win32process`, `win32api`, `win32con`) with standard user permissions:

| Win32 Function | Module | Purpose | Privilege Level |
| --- | --- | --- | --- |
| `EnumWindows` | `user32.dll` | Enumerates all top-level window handles across the system. | Standard User |
| `GetWindowThreadProcessId` | `user32.dll` | Maps HWND to owning thread ID and process ID (PID). | Standard User |
| `IsWindowVisible` | `user32.dll` | Verifies whether the window has `WS_VISIBLE` style. | Standard User |
| `GetWindowLongW` | `user32.dll` | Inspects `GWL_STYLE` and `GWL_EXSTYLE` to filter out tooltips and taskbar trays. | Standard User |
| `GetWindowTextW` | `user32.dll` | Retrieves window caption for title-based policy matching. | Standard User |
| `GetClassNameW` | `user32.dll` | Retrieves window class name (e.g. `Chrome_WidgetWin_1`) for robust matching. | Standard User |
| `GetClientRect` | `user32.dll` | Validates that window client area has non-zero width and height. | Standard User |
| `IsWindow` | `user32.dll` | Immediate revalidation before window movement to avoid stale handle crashes. | Standard User |
| `QueryFullProcessImageNameW` | `kernel32.dll` | Resolves the true executable path for a PID without command-line ambiguity. | Standard User |

---

## 3. Windows Virtual Desktop COM Interfaces

### 3.1 Official Microsoft API (`IVirtualDesktopManager`)

* **Interface GUID**: `{aa509085-ecd9-4eab-ac2a-8f4b63a1e50f}`
* **CLSID**: `{aa509086-ecd9-4eab-ac2a-8f4b63a1e50f}`
* **Supported Capabilities**:
  * `IsWindowOnCurrentVirtualDesktop(HWND, BOOL*)` — Confirms if window is on the active user view.
  * `GetWindowDesktopId(HWND, GUID*)` — Queries the unique desktop GUID containing the window.
  * `MoveWindowToDesktop(HWND, REFGUID)` — Moves a specified window to a target desktop GUID.
* **Limitations**:
  * Microsoft's documented COM API provides **no functions** to enumerate desktop counts, create new desktops, switch views, or read custom names.

### 3.2 Internal Windows Shell COM Interfaces (`IVirtualDesktopManagerInternal`)

* **Supported Capabilities** (via `pyvda`):
  * `GetCount()` — Returns exact count of currently existing virtual desktops.
  * `CreateDesktopW()` — Programmatically creates a new virtual desktop.
  * `SwitchDesktop()` — Switches user view to a designated desktop.
  * `MoveViewToDesktop()` — Moves an application view to a target virtual desktop.
* **Undocumented Interface Acknowledgement**:
  * These internal shell interfaces are private to Windows Explorer (`explorer.exe`).
  * Their internal GUIDs and vtable slot positions can shift between major Windows updates.
* **Risk & Fallback Architecture**:
  1. During initialization, `WindowsVdaProvider` performs a runtime capability probe (`is_available()`).
  2. If the internal COM interface raises an RPC or interface failure, `WindowsVdaProvider` flags itself as unavailable.
  3. The manager automatically falls back to `OfficialComDesktopManager` for window movements where GUIDs are known, and alerts the user to create missing desktops via Task View (Win+Tab).
  4. At no point does the application crash or claim an operation succeeded when an API call fails.

---

## 4. Third-Party Dependencies and Versions

| Library | Installed Version | License | Security & Stability Impact |
| --- | --- | --- | --- |
| `pyvda` | `>= 0.6.0` | MIT | Isolates COM vtable variations across Windows 10/11 builds. |
| `pywin32` | `>= 306` | PSF | Official Python Win32 bindings maintained by Microsoft/Python community. |
| `psutil` | `>= 5.9.0` | BSD | Native C extensions for safe, non-shell process enumeration. |
| `comtypes` | `>= 1.4.0` | MIT | Pure-Python COM client library. |
| `pystray` | `>= 0.19.5` | LGPL / GPL | System tray integration. |
| `Pillow` | `>= 10.0.0` | HPND | Image handling for tray icons. |
| `pytest` | `>= 8.0.0` | MIT | Automated test framework. |
