# Windows Compatibility Matrix

This document defines the verified, conditional, and unsupported capabilities across Windows 10 and Windows 11 builds for **Virtual Desktop Workspace Manager** per Sections 6, 62, 63, and 106 of the Master Specification.

---

## 1. Core API Capability Matrix

The application interacts with Virtual Desktops via internal Windows COM interfaces (`IVirtualDesktopManager`, `IVirtualDesktopManagerInternal`, `IServiceProvider`). Because internal COM interfaces evolve between Windows major builds, capabilities are classified as follows:

| Capability | Windows 10 (Build 1809–22H2) | Windows 11 (21H2, 22H2) | Windows 11 (23H2+) | Verification Status | Fallback / Behavior when Unavailable |
|---|---|---|---|---|---|
| **Enumerate Desktops** | **Supported** | **Supported** | **Supported** | Verified via PyWinCtl / COM fallback | Returns current desktop list or falls back to configured profile desktop list. |
| **Get Current Desktop** | **Supported** | **Supported** | **Supported** | Verified via GUID matching | UI displays "Unknown Desktop" without halting manager operations. |
| **Window Desktop Detection** | **Supported** | **Supported** | **Conditional** | Verified via `IVirtualDesktopManager.GetWindowDesktopId` | Diagnostic "Test Match" tool detects HWND presence; if GUID lookup fails, marked as `Desktop ?`. |
| **Window Movement** | **Supported** | **Supported** | **Conditional** | Verified via `IVirtualDesktopManager.MoveWindowToDesktop` | Moves to desktop ID; if restricted or pinned window, logs `WIN-002` warning without failing. |
| **Create Virtual Desktop** | **Supported** | **Supported** | **Supported** | Verified via COM internal | Safely creates up to target count; does not duplicate if already existing. |
| **Switch Desktop (Focus)** | **Conditional** | **Conditional** | **Conditional** | Requires internal COM activation | If OS restricts background switching, leaves switch optional and logs informational message. |
| **Delete Desktop** | **Unsupported** | **Unsupported** | **Unsupported** | Intentionally disabled for safety | Prevents accidental destruction of user applications or existing desktop layouts. |
| **Process Launching** | **Supported** | **Supported** | **Supported** | Verified via `subprocess.Popen` with safe argument lists | Zero shell execution; logs PID audit entry. |
| **Window Detection / Wait** | **Supported** | **Supported** | **Supported** | Verified via `EnumWindows` and title/class/exe matching | Configurable timeout with polling interval; graceful timeout reporting. |

---

## 2. Feature Capability Matrix & UI Degradation

Per Section 63, the UI dynamically derives available user actions based on detected OS capabilities. Controls are never grayed out silently; each displays an explicit reason when unavailable.

| Feature / UI Action | Capability Status | UI Indicator | User-Facing Explanation |
|---|---|---|---|
| **Create Desktop** | Available | ✓ Available | Safe idempotent creation supported on this OS build. |
| **Move Window** | Available | ✓ Available | Standard desktop relocation supported. |
| **Switch to Desktop** | Conditional | ⚠ Conditional | Requires active desktop switching provider capability. If unavailable, manual switch required. |
| **Delete Desktop** | Prohibited | ✕ Not Implemented | Disabled by design to protect user windows and workflows. |
| **Launch Application** | Available | ✓ Available | Direct executable invocation with audit logging. |
| **Test Match** | Available | ✓ Available | Read-only window discovery and pattern inspection. |

---

## 3. Supported Operating Systems

- **Windows 10 64-bit:** Versions 1809 (Build 17763) through 22H2 (Build 19045).
- **Windows 11 64-bit:** Versions 21H2 (Build 22000), 22H2 (Build 22621), 23H2 (Build 22631), and 24H2.
- **ARM64 Windows:** Python emulation mode supported, subject to 64-bit Python compatibility.
- **Windows Server / Non-Desktop SKUs:** Unsupported (Virtual Desktop API is absent or restricted).
