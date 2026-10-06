# Workspace Configuration Schema Reference

The configuration file is stored persistently at:
```text
%APPDATA%\VirtualDesktopWorkspaceManager\workspace.json
```

---

## 1. Schema Overview

```json
{
  "schema_version": 1,
  "profiles": [
    {
      "id": "default",
      "name": "Default Workspace",
      "description": "Default 4-desktop developer workspace",
      "desktops": [
        {
          "number": 1,
          "name": "Browser",
          "desktop_id": null
        }
      ],
      "apps": [
        {
          "id": "brave",
          "name": "Brave Browser",
          "executable": "%ProgramFiles%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
          "arguments": "",
          "desktop": 1,
          "enabled": true,
          "launch_mode": "launch_if_missing",
          "move_existing_window": true,
          "window_policy": "main",
          "title_pattern": "",
          "launch_delay_ms": 1000,
          "window_timeout_ms": 15000,
          "process_names": ["brave.exe"]
        }
      ]
    }
  ],
  "general": {
    "start_with_windows": false,
    "auto_launch_workspace": false,
    "confirm_before_execution": true,
    "minimize_to_tray": false,
    "start_minimized": false,
    "theme": "System",
    "active_profile_id": "default",
    "first_run_completed": true
  },
  "execution": {
    "window_timeout_ms": 15000,
    "polling_interval_ms": 250,
    "launch_delay_ms": 1000,
    "retry_count": 3
  },
  "logging": {
    "log_level": "INFO",
    "log_retention_days": 14,
    "log_dir": ""
  },
  "safety": {
    "automation_enabled": true,
    "require_confirmation": true,
    "dry_run_default": false,
    "never_kill_processes": true,
    "never_delete_desktops": true
  }
}
```

---

## 2. Field Definitions

### Root Level
| Field | Type | Description |
|---|---|---|
| `schema_version` | integer | Incremental configuration schema version (current: `1`). |
| `profiles` | array[WorkspaceProfile] | Array of workspace profile objects. |
| `general` | GeneralSettings | Application-level UI and startup settings. |
| `execution` | ExecutionSettings | Timing and polling thresholds for workspace execution. |
| `logging` | LoggingSettings | Logging verbosity, retention, and storage path. |
| `safety` | SafetySettings | Strict execution guardrails and pause toggles. |

---

### WorkspaceProfile
| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the profile. |
| `name` | string | Human-readable profile label (e.g. "Development", "Work"). |
| `description` | string | Optional description of profile purpose. |
| `desktops` | array[DesktopConfig] | Configured virtual desktop cards. |
| `apps` | array[AppConfig] | Applications configured within this profile. |

---

### DesktopConfig
| Field | Type | Description |
|---|---|---|
| `number` | integer | 1-indexed desktop position. |
| `name` | string | Custom label (e.g. "Browser", "Development", "Database"). |
| `desktop_id` | string / null | Optional Windows internal virtual desktop GUID string. |

---

### AppConfig
| Field | Type | Description |
|---|---|---|
| `id` | string | Unique stable application identifier. |
| `name` | string | Display name of the application. |
| `executable` | string | Absolute path or path with environment variables (e.g. `%LocalAppData%`). |
| `arguments` | string | Command-line arguments passed upon launch. |
| `desktop` | integer | Target virtual desktop number (1-indexed). |
| `enabled` | boolean | Whether the application participates in workspace launch/sync. |
| `launch_mode` | string | One of: `"launch_if_missing"`, `"always_launch"`, `"reuse_only"`. |
| `move_existing_window`| boolean | Whether running windows are moved to the target desktop. |
| `window_policy` | string | One of: `"main"`, `"all"`, `"title_contains"`, `"title_regex"`. |
| `title_pattern` | string | Text substring or regex pattern used when policy matches by title. |
| `launch_delay_ms` | integer | Milliseconds to pause after launching this app before the next. |
| `window_timeout_ms` | integer | Maximum milliseconds to wait for a top-level window to appear. |
| `process_names` | array[string] | Candidate process names (e.g. `["brave.exe"]`). |

---

## 3. Schema Migrations

The `ConfigMigration` service verifies and upgrades configurations on load:
* **v0 -> v1**: Legacy configurations with a top-level `apps` list and boolean `launchIfMissing` flags are automatically nested into a default `WorkspaceProfile` with modernized enum properties (`launch_mode`).
