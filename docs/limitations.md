# Windows Virtual Desktop API Limitations & Platform Constraints

This document details known technical limitations of the Windows Virtual Desktop platform and the mitigations implemented in this application.

---

## 1. Documented vs Undocumented Windows APIs

### Official Microsoft API (`IVirtualDesktopManager`)

* **Available Methods**:
  * `IsWindowOnCurrentVirtualDesktop(HWND, BOOL*)`
  * `GetWindowDesktopId(HWND, GUID*)`
  * `MoveWindowToDesktop(HWND, REFGUID)`
* **Limitation**: Microsoft's official, documented COM interface provides **no methods** to:
  * Enumerate the list of virtual desktops.
  * Create a new virtual desktop programmatically.
  * Switch the user view to a specific virtual desktop.
  * Reorder or rename virtual desktops.

### Internal Windows COM Interfaces (`IVirtualDesktopManagerInternal`)

* Used by tools including `pyvda`, `VirtualDesktop11`, and `PSVirtualDesktop`.
* **Limitation**: Because these interfaces are not publicly documented by Microsoft, their vtable offsets and GUIDs can change between major Windows builds (such as Windows 10 1909 vs 21H2, or Windows 11 21H2 vs 24H2/26xxx).
* **Mitigation**:
  * The application isolates all desktop operations behind `IVirtualDesktopProvider`.
  * If `WindowsVdaProvider` cannot communicate with COM interfaces, it reports `is_available() == False` and falls back gracefully to `OfficialComDesktopManager` for window movement or `KeyboardFallbackProvider`.
  * The application logs explicit warnings rather than claiming unsupported operations succeeded.

---

## 2. Elevated Processes and User Interface Privilege Isolation (UIPI)

* **Limitation**: Windows security prevents a standard user-level application from sending messages or manipulating top-level windows of applications running with Administrator (High/System Integrity) privileges.
* **Example**: If SQL Server Management Studio (SSMS) is launched with "Run as administrator", a standard-integrity workspace manager cannot query or move its HWND.
* **Mitigation**: The manager logs an explicit warning explaining that the window belongs to an elevated process and cannot be moved from standard user mode without running the manager elevated.

---

## 3. Chromium / Electron Multi-Process Window Binding

* **Limitation**: Applications like Brave Browser, Google Chrome, VS Code, and Postman spawn multiple background renderer and utility processes before creating the primary visible window frame.
* **Mitigation**:
  * The manager queries the parent PID, resolves associated child processes, and filters for actual top-level visible windows (`WS_VISIBLE`, non-zero client dimensions, excluded `WS_EX_TOOLWINDOW`).
  * Non-blocking polling with configurable timeouts (`window_timeout_ms`, default 15,000 ms) ensures the window is ready before move attempts.

---

## 4. Virtual Desktop Renaming Support

* **Limitation**: While Windows 11 allows users to assign custom names to virtual desktops in Task View, Windows 10 does not reliably expose desktop renaming through standard APIs.
* **Mitigation**: The manager stores and displays user-friendly custom labels persistently in `workspace.json`, regardless of whether the underlying Windows build supports syncing labels back to Task View.
