# Standard Error Catalog

## 1. Overview

Conforming to Section 59 of the product specification, all application errors are categorized and assigned a stable internal error code. This ensures consistent diagnostic reporting, simplified troubleshooting, and clear user remediation guidance.

Error codes follow the standard format:
`[CATEGORY-XXX]`

Where:
- **`VDM`**: Virtual Desktop Management
- **`WIN`**: Window Operations & Placement
- **`APP`**: Application Detection & Launching
- **`CFG`**: Configuration, Validation & Persistence
- **`SETUP`**: Installation, Bootstrap & Shortcuts
- **`SEC`**: Security, Boundaries & Elevation

---

## 2. Complete Error Registry

### 2.1 Virtual Desktop Subsystem (`VDM`)

| Code | Title | User Explanation | Remediation Guidance |
|---|---|---|---|
| **`VDM-001`** | Provider Unavailable | Windows Virtual Desktop COM API is not available or unsupported on this Windows build. | Verify that pyvda is properly installed and that the Windows OS build supports virtual desktop COM interfaces. |
| **`VDM-002`** | Desktop Identity Mismatch | Windows reported a different desktop count or identity than configured in the profile. | Refresh desktop detection in the manager or review desktop mappings under the Virtual Desktops tab. |
| **`VDM-003`** | Desktop Creation Failed | Failed to create a new Virtual Desktop. | Check if the maximum desktop limit has been reached or if desktop creation is restricted by group policy. |
| **`VDM-004`** | Desktop Switch Failed | Failed to switch to the target Virtual Desktop. | Verify the target desktop index exists and Windows Shell is responsive. |

---

### 2.2 Window Operations Subsystem (`WIN`)

| Code | Title | User Explanation | Remediation Guidance |
|---|---|---|---|
| **`WIN-001`** | Window No Longer Exists | The targeted application window closed before placement could complete. | Ensure the application is stable and does not crash or close its splash window prematurely. |
| **`WIN-002`** | Window Move Failed | Windows did not confirm the requested Virtual Desktop window assignment. | Run Health Check diagnostics or test window matching using the Test Match tool. |
| **`WIN-003`** | Ambiguous Window Match | Multiple open windows matched the application rule without unique selection. | Refine the window matching policy or specify a title contains/regex pattern in application settings. |

---

### 2.3 Application Launch & Discovery Subsystem (`APP`)

| Code | Title | User Explanation | Remediation Guidance |
|---|---|---|---|
| **`APP-001`** | Executable Not Found | The configured executable path cannot be located on disk. | Edit the application configuration to specify a valid path or use auto-discovery. |
| **`APP-002`** | Window Wait Timeout | The application was launched, but its top-level window did not appear within the configured timeout. | Increase the application's `window_timeout_ms` setting or check if the app starts minimized to tray. |
| **`APP-003`** | Process Failed to Start | Failed to spawn the configured application process. | Check file permissions, working directory, or command line arguments. |

---

### 2.4 Configuration & Storage Subsystem (`CFG`)

| Code | Title | User Explanation | Remediation Guidance |
|---|---|---|---|
| **`CFG-001`** | Invalid Configuration | The configuration file failed schema or semantic validation. | Restore a backup snapshot from the backups directory or reset to default profile. |
| **`CFG-002`** | Migration Failed | Unable to automatically migrate a legacy configuration format to the current schema. | Inspect the backup file created in the configuration directory. |
| **`CFG-003`** | Backup / Restore Failed | Could not create or restore a configuration snapshot. | Ensure write permissions exist on `%APPDATA%/VirtualDesktopWorkspaceManager`. |

---

### 2.5 Setup & Shortcuts Subsystem (`SETUP`)

| Code | Title | User Explanation | Remediation Guidance |
|---|---|---|---|
| **`SETUP-001`** | Setup Dependency Failure | Setup could not resolve or verify required Python dependencies. | Run setup in an activated virtual environment with required wheels installed. |
| **`SETUP-002`** | Shortcut Creation Failure | Desktop or Start Menu shortcut creation failed. | Check Desktop folder write permissions and ensure `pywin32` COM is registered. |

---

### 2.6 Security & Boundaries (`SEC`)

| Code | Title | User Explanation | Remediation Guidance |
|---|---|---|---|
| **`SEC-001`** | Security Boundary Violation | An operation was blocked because it attempted unauthorized system modification. | The manager strictly forbids process termination, elevation, and arbitrary shell command execution. |
