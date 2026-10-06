# Build a Production-Ready Windows 10/11 Virtual Desktop Workspace Manager

## 1. ROLE

Act as a senior Windows desktop software engineer and build a **production-quality Windows 10/11 Virtual Desktop Workspace Manager**.

The application will manage Windows Virtual Desktops and allow the user to create a persistent workspace where applications are automatically launched and/or moved to specific virtual desktops.

The application must have a **modern, clean desktop UI**, persistent configuration, safe execution, strong error handling, detailed logging, and recovery mechanisms.

This is NOT a prototype, proof of concept, or simple keyboard-macro script.

Build it as a reliable utility that I can actually use daily.

---

# 2. PRIMARY OBJECTIVE

Create a Windows application that can:

1. Detect the currently available Windows Virtual Desktops.
2. Create additional Virtual Desktops when required.
3. Maintain a configurable workspace layout.
4. Assign one or multiple applications to the same Virtual Desktop.
5. Launch applications automatically.
6. Detect applications that are already running.
7. Detect their windows.
8. Move existing application windows to their assigned Virtual Desktop whenever technically possible.
9. Allow the user to change application-to-desktop assignments from the UI.
10. Allow the user to add new applications later without modifying source code.
11. Allow applications to be removed from the workspace.
12. Allow multiple applications on the same desktop.
13. Allow an application to be reassigned from one desktop to another.
14. Save all configuration persistently.
15. Restore the workspace later.
16. Provide a "Launch Workspace" button.
17. Provide a "Sync / Repair Workspace" button.
18. Provide a "Stop / Cancel" mechanism where practical.
19. Provide detailed logs and diagnostics.
20. Never automatically launch or modify applications simply because the manager starts unless the user explicitly enables that behavior.

---

# 3. VERY IMPORTANT DEVELOPMENT RULE

## DO NOT RUN THE CREATED APPLICATION AUTOMATICALLY

When developing this project inside Google Antigravity:

- Create the complete project.
- Create all source files.
- Create configuration files.
- Create documentation.
- Create tests.
- Perform static validation where possible.
- Do NOT launch the generated application.
- Do NOT execute the launcher against my actual Windows desktops.
- Do NOT create/move virtual desktops.
- Do NOT launch Brave.
- Do NOT launch Antigravity.
- Do NOT launch SSMS.
- Do NOT launch Postman.
- Do NOT modify my Windows workspace.

Only build the application.

Wait for my explicit instruction before running the generated application.

If a build/test command is completely necessary, prefer static validation or isolated tests that do not modify the host desktop environment.

---

# 4. PLATFORM

Target:

- Windows 10
- Windows 11
- 64-bit Windows preferred
- PowerShell and/or Python may be used.

Choose the implementation language based on reliability.

Do NOT choose a technology merely because it is easier.

The most important requirements are:

1. Windows Virtual Desktop reliability
2. Window detection
3. Window-to-desktop movement
4. Process management
5. Persistent configuration
6. UI usability
7. Safe execution
8. Maintainability

If Python is selected, prefer appropriate Windows APIs/libraries such as:

- pywin32
- pyvda or another maintained Virtual Desktop integration library
- psutil
- tkinter / PySide / PyQt for UI, depending on the chosen architecture

If PowerShell is selected, use appropriate Windows APIs/modules and avoid relying exclusively on simulated keyboard input.

Before implementation, verify that the chosen Virtual Desktop API/library actually supports the required operations.

Do not blindly assume that an API supports functionality that it does not actually provide.

---

# 5. IMPORTANT WINDOWS VIRTUAL DESKTOP REQUIREMENT

Windows Virtual Desktops are not ordinary application windows.

The implementation must clearly separate:

### Desktop operations

- Enumerate desktops
- Create desktops
- Determine desktop order/index
- Determine desktop IDs where available
- Determine the current desktop
- Switch desktop
- Move a window between desktops
- Detect desktop changes

### Window operations

- Enumerate top-level windows
- Determine HWND
- Determine process ID
- Determine executable
- Determine title
- Determine visibility
- Determine minimized/maximized state
- Determine whether the window is usable
- Move the window to a target Virtual Desktop

Do not treat a process ID as equivalent to a window.

One application can have:

- multiple processes
- multiple windows
- child windows
- background processes
- splash screens
- helper processes

The system must therefore identify the **correct top-level application window**.

---

# 6. DEFAULT WORKSPACE

Create the following initial configuration:

### Desktop 1 — Browser

Application:

- Brave Browser

### Desktop 2 — Development

Application:

- Google Antigravity

### Desktop 3 — Database

Application:

- SQL Server Management Studio

### Desktop 4 — API Development

Application:

- Postman

However, these defaults must NOT be hard-coded permanently.

They must be editable through the UI.

---

# 7. USER-CONFIGURABLE WORKSPACE

The user must be able to completely customize the workspace.

Example:

```text
Desktop 1
 ├── Brave
 ├── Chrome
 └── Spotify

Desktop 2
 ├── Antigravity
 ├── VS Code
 └── File Explorer

Desktop 3
 ├── SSMS
 └── Azure Data Studio

Desktop 4
 ├── Postman
 ├── Docker Desktop
 └── Browser
```

There must be NO limitation that one desktop can contain only one application.

A desktop can contain:

- 0 applications
- 1 application
- 2 applications
- 10 applications
- or more

subject only to practical Windows limitations.

---

# 8. UI REQUIREMENTS

Build a proper desktop GUI.

Do NOT make the UI just a terminal menu.

The UI should contain the following major sections.

---

## 8.1 Dashboard

Display:

```text
Virtual Desktop Workspace Manager

Current Desktop: Desktop 2

Workspace Status:
✓ Desktop 1 Ready
✓ Desktop 2 Ready
⚠ Desktop 3 Missing Application
✓ Desktop 4 Ready
```

Display:

- Current Virtual Desktop
- Total Virtual Desktops
- Configured applications
- Running applications
- Missing applications
- Workspace status
- Last workspace launch time

Provide buttons:

- Launch Workspace
- Sync Workspace
- Refresh
- Stop/Cancel
- Open Settings
- View Logs

---

# 9. VIRTUAL DESKTOP PANEL

Display each desktop as a card.

Example:

```text
┌─────────────────────────────────────┐
│ Desktop 1                           │
│ Browser                             │
│                                     │
│ ✓ Brave                             │
│ ✓ Chrome                            │
│                                     │
│ [Open] [Edit] [Add App]             │
└─────────────────────────────────────┘
```

For Desktop 2:

```text
┌─────────────────────────────────────┐
│ Desktop 2                           │
│ Development                         │
│                                     │
│ ✓ Antigravity                       │
│ ✓ VS Code                            │
│ ✓ Git Bash                           │
│                                     │
│ [Open] [Edit] [Add App]             │
└─────────────────────────────────────┘
```

Each desktop card should display:

- Desktop number
- Custom desktop name
- Assigned applications
- Running/stopped state
- Missing application warning
- Current desktop indicator
- Open desktop button
- Edit button
- Add Application button

---

# 10. APPLICATION MANAGEMENT

Create an application management interface.

The user must be able to:

### Add application

Fields:

```text
Application Name
Executable Path
Arguments
Target Desktop
Launch Enabled
Move Existing Window Enabled
Launch Delay
Window Matching Strategy
```

Provide:

### Browse

Allow the user to select an `.exe` file through a standard Windows file picker.

### Detect

Attempt to automatically detect:

- executable
- process name
- application name
- installation path
- currently running windows

---

# 11. APPLICATION DISCOVERY

The application should provide a convenient way to add applications.

Support:

### Method 1 — Browse for EXE

Example:

```text
C:\Program Files\...\application.exe
```

### Method 2 — Detect running application

Show currently running applications:

```text
Application       Process        Window
Brave             brave.exe      Brave
Postman           Postman.exe    Postman
SSMS              Ssms.exe       SQL Server Management Studio
```

User can select one and click:

```text
Add to Workspace
```

### Method 3 — Start Menu / Shortcut discovery

Where practical, allow discovering applications from:

- Start Menu shortcuts
- Desktop shortcuts
- common installation locations

Do not modify shortcuts.

---

# 12. APPLICATION ASSIGNMENT

The user must be able to change:

```text
Application: Brave
Desktop: 1
```

to:

```text
Application: Brave
Desktop: 3
```

without editing code.

Provide a dropdown:

```text
Target Desktop

[ Desktop 1 — Browser ▼ ]
```

The change must be persisted.

---

# 13. MULTIPLE APPLICATIONS PER DESKTOP

This is a mandatory feature.

For example:

```text
Desktop 1
 ├── Brave
 ├── Chrome
 ├── Spotify
 └── File Explorer
```

The UI should support:

```text
[ + Add Application ]
```

at both:

- workspace level
- desktop level

Adding an application must NOT overwrite existing applications.

---

# 14. REASSIGN APPLICATION

Provide an easy way to move an application between desktops.

Example:

```text
Brave

Current:
Desktop 1

Move to:
[ Desktop 3 ▼ ]

[ Save ]
```

The application should then use Desktop 3 the next time the workspace is synchronized/launched.

If the application is already running, provide an optional immediate action:

```text
Move currently running window now?
[ Move Now ] [ Later ]
```

---

# 15. REMOVE APPLICATION

Allow removing an application from the workspace.

Important:

Removing an application from the workspace must NOT uninstall it.

It must only remove its workspace configuration.

Confirmation:

```text
Remove "Brave" from Desktop 1?

This will not uninstall Brave.

[ Cancel ] [ Remove ]
```

---

# 16. DESKTOP MANAGEMENT

Allow the user to configure:

```text
Desktop Number
Desktop Name
Applications
```

Example:

```text
Desktop 1 → Browser
Desktop 2 → Development
Desktop 3 → Database
Desktop 4 → API Testing
```

Allow renaming desktop labels inside the application.

Important:

Do not assume Windows itself permanently supports arbitrary custom names unless the implementation actually provides such functionality.

The custom name can simply be stored by this manager.

---

# 17. DESKTOP COUNT

Before workspace execution:

1. Enumerate current Virtual Desktops.
2. Determine current count.
3. Compare against required desktop count.
4. Create only the number required.

Example:

```text
Existing desktops: 2
Required desktops: 4

Create:
Desktop 3
Desktop 4
```

If:

```text
Existing desktops: 5
Required desktops: 4
```

DO NOT delete Desktop 5.

DO NOT rearrange unrelated desktops.

DO NOT destroy user-created desktops.

Use the first required desktops for the configured workspace.

---

# 18. NEVER DELETE USER DESKTOPS AUTOMATICALLY

This is a critical safety requirement.

The application must NEVER automatically:

- delete a Virtual Desktop
- close user applications
- kill processes
- uninstall software
- modify registry settings unnecessarily
- delete files
- change Windows system settings

The workspace manager should only create/reuse desktops and manage configured application windows.

---

# 19. PROCESS DETECTION

Before launching an application:

Determine whether it is already running.

Use process information such as:

- executable name
- executable path
- process ID
- command line where available

Do not rely only on the process name.

For example:

```text
brave.exe
```

may represent multiple Brave windows.

---

# 20. WINDOW DETECTION

After detecting a process, enumerate its top-level windows.

Check:

- HWND
- visibility
- title
- process ID
- executable
- minimized state
- maximized state

Ignore:

- invisible helper windows
- system windows
- child windows
- notification-only windows

Prefer the main visible application window.

---

# 21. MULTI-WINDOW APPLICATIONS

Support applications that have multiple windows.

Example:

```text
Brave
 ├── Window 1
 ├── Window 2
 └── Window 3
```

Configuration should provide a window policy:

### Policy A — Move all matching windows

### Policy B — Move only the main window

### Policy C — Ask the user

### Policy D — Match by title

### Policy E — Match by process

Document limitations clearly.

---

# 22. APPLICATION LAUNCH MODES

Each application should support:

### Launch if not running

Default behavior.

### Always launch new instance

Only when supported safely.

### Reuse existing instance

Prefer this for applications such as browsers where appropriate.

### Do not launch

Only move an already-running window.

Example:

```text
Brave
Launch behavior:
[ Reuse existing / Launch if missing ]
```

---

# 23. STARTUP SEQUENCE

Do not launch every application simultaneously.

Use controlled sequencing.

Example:

```text
1. Ensure desktops exist
2. Launch Desktop 1 applications
3. Wait for windows
4. Move windows
5. Launch Desktop 2 applications
6. Wait for windows
7. Move windows
8. Continue...
```

Allow configurable launch delays.

Example:

```text
Default delay: 1 second
Window timeout: 15 seconds
```

Do not use unnecessarily long fixed sleeps.

Prefer event/state polling.

---

# 24. WINDOW READY DETECTION

Do not assume:

```text
Process started = Window ready
```

Instead:

1. Start process.
2. Poll for process.
3. Poll for main window.
4. Verify HWND.
5. Verify window visibility.
6. Attempt desktop assignment.
7. Verify assignment if API allows verification.

Use configurable timeout.

Example:

```text
Window timeout: 15 seconds
Polling interval: 250 ms
```

---

# 25. DESKTOP ASSIGNMENT

Prefer direct Windows API/library integration.

Do NOT make keyboard automation the primary mechanism.

Avoid depending on:

```text
Win + Ctrl + D
Win + Ctrl + Left
Win + Ctrl + Right
```

as the main implementation.

Keyboard shortcuts may be used only as a documented fallback when direct API functionality is unavailable.

If a fallback is used:

- detect focus
- restore focus
- verify current desktop
- perform action
- verify result
- recover if action failed

Never assume simulated keypresses succeeded.

---

# 26. DESKTOP ASSIGNMENT VERIFICATION

After moving a window:

Verify that it actually belongs to the intended Virtual Desktop when possible.

Example log:

```text
[INFO] Moving Brave → Desktop 1
[SUCCESS] Brave assigned to Desktop 1
```

If verification is impossible due to Windows API limitations:

```text
[WARNING] Window move requested, but Windows API does not expose reliable verification.
```

Never report success when the operation was not verified.

---

# 27. SPECIAL APPLICATION CONFIGURATION

Create default detection logic for:

## Brave

Search common locations such as:

```text
%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe
%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe
%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe
```

Also support user-selected paths.

---

# 28. GOOGLE ANTIGRAVITY

Do NOT assume that Antigravity is a web page.

Attempt to detect the actual installed application/shortcut.

Possible sources:

- Start Menu shortcuts
- user-selected executable
- known installation locations
- currently running process

If it cannot be detected automatically:

Display:

```text
Antigravity was not detected.

[Browse for Application]
[Select Running Application]
```

Store the selected executable path.

Do not hard-code a random web URL as a replacement for the installed application.

---

# 29. SQL SERVER MANAGEMENT STUDIO

Attempt to dynamically locate SSMS.

Support installation/version variations.

Search:

- Program Files
- Program Files (x86)
- Start Menu shortcuts
- registry where appropriate
- user-configured executable path

Do not assume a single SSMS version.

The user may have SSMS 20, 21, 22, or another supported version.

---

# 30. POSTMAN

Support versioned installations.

Search locations such as:

```text
%LocalAppData%\Postman\
```

Detect:

```text
app-*\Postman.exe
```

Select the newest valid version where appropriate.

Also support manually selected paths.

---

# 31. APPLICATION PROFILE

Each application should have a configuration object similar to:

```json
{
  "id": "brave",
  "name": "Brave Browser",
  "executable": "C:\\Path\\brave.exe",
  "arguments": "",
  "desktop": 1,
  "enabled": true,
  "launchIfMissing": true,
  "moveExistingWindow": true,
  "windowPolicy": "main",
  "launchDelayMs": 1000,
  "windowTimeoutMs": 15000
}
```

Use a unique stable ID rather than relying only on display names.

---

# 32. PERSISTENT CONFIGURATION

Configuration must survive application restarts.

Store configuration in an appropriate user-level location.

For example:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\
```

Possible files:

```text
config.json
workspace.json
logs\
backups\
```

Do not store user configuration inside the application's installation directory if avoidable.

---

# 33. CONFIGURATION VERSIONING

Include a configuration schema version.

Example:

```json
{
  "schemaVersion": 1,
  ...
}
```

Future versions must be able to migrate older configuration where possible.

Never silently discard user configuration.

---

# 34. CONFIGURATION BACKUPS

Before modifying configuration:

Create a backup when appropriate.

Example:

```text
workspace.json
workspace.backup.json
```

Do not create hundreds of backups.

Use a reasonable retention strategy.

---

# 35. IMPORT / EXPORT

The UI must support:

```text
Export Workspace
Import Workspace
```

Export should produce a human-readable JSON configuration.

Example:

```text
my-development-workspace.json
```

Import must validate the file before replacing the current configuration.

Never overwrite configuration without validation.

---

# 36. DRY-RUN MODE

Provide:

```text
Dry Run
```

Before making changes.

Dry run should show:

```text
Existing desktops: 2
Required desktops: 4
Would create: Desktop 3, Desktop 4

Desktop 1:
✓ Brave detected

Desktop 2:
✓ Antigravity detected

Desktop 3:
✓ SSMS detected

Desktop 4:
⚠ Postman not detected
```

Dry run must not:

- create desktops
- launch applications
- move windows
- terminate processes

---

# 37. SAFE EXECUTION MODE

Normal execution should require an explicit user action:

```text
[ Launch Workspace ]
```

Do not automatically execute the workspace merely because the UI opens.

Provide an optional setting:

```text
Launch workspace when Windows starts
```

This setting must default to:

```text
OFF
```

If enabled, explain that Windows startup integration will be created.

Do not silently create startup tasks.

---

# 38. STARTUP OPTION

If the user enables startup:

Provide a clear option such as:

```text
☐ Start Workspace Manager with Windows
☐ Automatically launch configured workspace
```

These must be separate settings.

Possible configurations:

```text
Manager starts only
Manager starts + workspace automatically launches
```

Default:

```text
Both OFF
```

---

# 39. LOGGING

Create structured logs.

Example:

```text
2026-10-06 14:30:01 [INFO] Workspace launch started
2026-10-06 14:30:02 [INFO] Detected 2 Virtual Desktops
2026-10-06 14:30:02 [INFO] Creating Desktop 3
2026-10-06 14:30:03 [SUCCESS] Desktop 3 created
2026-10-06 14:30:03 [INFO] Creating Desktop 4
2026-10-06 14:30:04 [SUCCESS] Desktop 4 created
2026-10-06 14:30:05 [INFO] Launching Brave
2026-10-06 14:30:07 [SUCCESS] Brave window detected
2026-10-06 14:30:07 [SUCCESS] Brave assigned to Desktop 1
```

Use:

- INFO
- SUCCESS
- WARNING
- ERROR
- DEBUG

---

# 40. LOG UI

The UI must include a live log panel.

Features:

- clear logs
- copy logs
- open log folder
- filter by level
- search logs
- export diagnostics

Example filters:

```text
[ALL] [INFO] [SUCCESS] [WARNING] [ERROR]
```

---

# 41. ERROR HANDLING

Never allow one application failure to terminate the entire workspace operation.

Example:

```text
Brave      ✓
Antigravity ✓
SSMS       ✓
Postman    ✗
```

The manager should continue.

At the end:

```text
Workspace completed with warnings.

Successful: 3
Failed: 1
Skipped: 0
```

---

# 42. MISSING APPLICATION

If an application is unavailable:

```text
Postman was not found.

Search locations:
- C:\Users\...\AppData\Local\Postman
- configured path

What would you like to do?

[Browse]
[Skip]
[Remove From Workspace]
```

Do not uninstall anything.

---

# 43. PERMISSION HANDLING

Do NOT automatically elevate to Administrator.

The application should work with normal user permissions whenever possible.

If an operation requires elevation:

Explain exactly why.

Example:

```text
Administrator privileges are not required for normal workspace operations.

This operation requires elevated permissions because...
```

Never silently run:

```text
RunAs Administrator
```

---

# 44. COMMAND EXECUTION SAFETY

Avoid unsafe command construction.

Do not use:

- encoded PowerShell commands
- downloaded scripts
- remote code execution
- shell injection-prone string concatenation
- hidden background commands
- arbitrary command execution from configuration

Executable paths and arguments must be validated.

Use safe process creation APIs.

---

# 45. USER DATA SAFETY

The application must NOT modify or delete:

- Documents
- Downloads
- Desktop files
- source code
- Git repositories
- Docker data
- SQL databases
- browser profiles
- application data

unless explicitly required by a future feature and explicitly confirmed.

The launcher should only manage:

- Virtual Desktop state
- configured application processes/windows
- its own configuration
- its own logs

---

# 46. IDE / DEVELOPMENT ENVIRONMENT SAFETY

The default workspace must NOT interfere with:

- Git
- Docker
- Visual Studio
- VS Code
- Node.js
- Python
- SQL Server
- Postman
- Brave
- development repositories

The application should never terminate development processes automatically.

---

# 47. DUPLICATE PREVENTION

The manager itself should not launch duplicate copies of the same application unnecessarily.

Example:

```text
Brave already running.
Reusing existing Brave window.
```

However, respect application-specific behavior.

Some applications support multiple windows/instances.

Configuration must control this.

---

# 48. IDEMPOTENCY

Running:

```text
Launch Workspace
```

multiple times must not produce:

```text
Brave
Brave
Brave
Brave
```

or duplicate Virtual Desktops.

Instead:

```text
Existing desktop detected.
Existing application detected.
Existing window detected.
Synchronizing state.
```

---

# 49. WORKSPACE SYNCHRONIZATION

Add a dedicated:

```text
Sync Workspace
```

operation.

It should compare:

### Desired state

versus

### Actual state

Example:

```text
Desired:

Brave → Desktop 1
Antigravity → Desktop 2
SSMS → Desktop 3
Postman → Desktop 4

Actual:

Brave → Desktop 3
Antigravity → Desktop 2
SSMS → Desktop 3
Postman → Not Running
```

Then:

```text
Brave → move to Desktop 1
Postman → launch
```

This should be the primary repair mechanism.

---

# 50. "LAUNCH WORKSPACE" VS "SYNC WORKSPACE"

Keep these concepts separate.

### Launch Workspace

Ensure applications are launched and assigned.

### Sync Workspace

Do not necessarily launch missing applications unless configuration says so.

Instead reconcile the current state with the desired state.

Document this behavior.

---

# 51. CURRENT DESKTOP

Display:

```text
Current Desktop: Desktop 2 — Development
```

Update it when the user changes Virtual Desktops outside the manager, if practical.

Provide:

```text
Refresh
```

fallback.

---

# 52. OPEN DESKTOP

Each desktop card should have:

```text
[ Open Desktop ]
```

Clicking it should switch to that Virtual Desktop.

Do not launch any applications when merely opening a desktop.

---

# 53. ADD DESKTOP

If practical, provide:

```text
[ + Add Desktop ]
```

But distinguish between:

### Physical Windows Virtual Desktop

and

### Workspace configuration.

If the user adds a new Windows Virtual Desktop manually, the manager should detect it.

If the manager creates one, it should track it where possible.

---

# 54. DESKTOP ORDER

Do not assume desktop IDs are always:

```text
1, 2, 3, 4
```

Internally use stable identifiers when the Windows API exposes them.

Display:

```text
Desktop 1
Desktop 2
Desktop 3
Desktop 4
```

as user-friendly positions.

If Windows changes ordering/IDs, refresh the mapping.

---

# 55. WINDOW TITLE MATCHING

Some applications may have dynamic titles.

Support configurable matching:

```text
Process name
Executable path
Window title contains
Window title regex
HWND
```

Default to process/executable-based matching.

Use title matching only when necessary.

---

# 56. APPLICATION ARGUMENTS

Allow optional launch arguments.

Example:

```text
Executable:
brave.exe

Arguments:
--profile-directory="Default"
```

Arguments must be stored separately from the executable path.

Validate them safely.

Do not allow arbitrary shell expressions.

---

# 57. ENVIRONMENT VARIABLES

Support environment-variable expansion where appropriate:

```text
%ProgramFiles%
%ProgramFiles(x86)%
%LocalAppData%
%AppData%
%UserProfile%
%SystemDrive%
```

Do not blindly expand arbitrary values.

---

# 58. PATH DISCOVERY

Use a layered resolution strategy:

1. User-configured executable
2. Currently running process
3. Start Menu shortcut
4. Registry where appropriate
5. Known installation directories
6. Environment variables
7. Controlled filesystem search

Do not recursively scan the entire C:\ drive.

Avoid expensive searches.

---

# 59. UI SETTINGS

Create a Settings page.

Settings should include:

### General

- Start with Windows
- Automatically launch workspace
- Confirm before workspace launch
- Minimize to tray
- Start minimized

### Execution

- Window timeout
- Polling interval
- Launch delay
- Retry count

### Logging

- Log level
- Log retention
- Open log directory

### Safety

- Require confirmation
- Dry-run default
- Never kill processes

---

# 60. SYSTEM TRAY

If implementing a system tray:

Provide:

```text
Open Manager
Launch Workspace
Sync Workspace
Pause Automation
View Logs
Exit
```

The tray must NOT silently execute workspace operations.

---

# 61. PAUSE / DISABLE

Provide:

```text
Automation Enabled: ON/OFF
```

When disabled:

- Do not launch applications
- Do not move windows
- Do not modify desktop state

The UI itself can still be used.

---

# 62. EMERGENCY STOP

Provide:

```text
STOP
```

This should stop the current workspace operation where possible.

It must NOT kill applications.

It simply prevents additional actions from being performed.

---

# 63. TRANSACTION-LIKE EXECUTION

Treat workspace execution as a sequence of operations.

Example:

```text
Phase 1:
Detect

Phase 2:
Prepare desktops

Phase 3:
Launch applications

Phase 4:
Wait for windows

Phase 5:
Assign windows

Phase 6:
Verify

Phase 7:
Report
```

If something fails, continue safely where possible.

---

# 64. RETRY POLICY

For temporary failures:

```text
Attempt 1
Attempt 2
Attempt 3
```

Use exponential or bounded delays where appropriate.

Do not retry indefinitely.

---

# 65. CRASH RECOVERY

If the manager crashes while performing an operation:

It must not leave behind dangerous processes or modify unrelated system state.

On next startup:

```text
Previous workspace operation may not have completed.

[Review]
[Sync Workspace]
[Ignore]
```

---

# 66. CONFIGURATION VALIDATION

Before execution validate:

- desktop number exists
- executable path exists where required
- configuration IDs are unique
- no duplicate application IDs
- invalid arguments
- invalid timeout values
- unsupported configurations

Show errors before execution.

---

# 67. UI VALIDATION

The UI should immediately show:

```text
✓ Valid executable
⚠ Executable not found
✓ Desktop assignment valid
⚠ Window matching rule invalid
```

---

# 68. TESTING

Create tests for:

### Configuration

- load config
- save config
- malformed config
- migration
- backup

### Application discovery

- valid path
- missing path
- versioned Postman
- SSMS detection

### Process handling

- process running
- process missing
- multiple processes

### Window handling

- visible window
- hidden window
- minimized window
- multiple windows

### Workspace logic

- 1 desktop
- 2 desktops
- 4 desktops
- more than 4 desktops
- multiple apps on one desktop
- duplicate launch
- missing application

---

# 69. MOCK / DRY-RUN TESTING

The tests must NOT manipulate the user's real Virtual Desktops.

Create abstractions/interfaces so that desktop operations can be mocked.

For example:

```text
VirtualDesktopProvider
WindowProvider
ProcessProvider
ApplicationLauncher
ConfigurationStore
```

Then provide mock implementations for automated tests.

This is extremely important.

---

# 70. ARCHITECTURE

Use a clean architecture.

Suggested structure:

```text
VirtualDesktopWorkspaceManager/
│
├── app/
│   ├── main
│   ├── ui/
│   ├── core/
│   ├── services/
│   ├── models/
│   ├── providers/
│   ├── discovery/
│   ├── configuration/
│   └── logging/
│
├── tests/
│
├── config/
│
├── docs/
│
├── logs/
│
└── README.md
```

Separate:

```text
UI
Business Logic
Windows API Integration
Application Discovery
Configuration
Logging
```

Do not place everything in one giant script.

---

# 71. WINDOWS API ABSTRACTION

Create an abstraction layer around Windows-specific functionality.

For example:

```text
IVirtualDesktopProvider
IWindowProvider
IProcessProvider
IApplicationLauncher
```

The rest of the application should not directly depend on low-level Windows API calls.

This makes testing and future maintenance easier.

---

# 72. NO HARD-CODED APPLICATION PATHS

Default paths may be used for discovery, but they must not be mandatory.

Users must be able to configure any application.

Example:

```text
Application:
Docker Desktop

Executable:
C:\Program Files\Docker\Docker\Docker Desktop.exe

Desktop:
2
```

---

# 73. APPLICATION TEMPLATES

Provide optional templates for common applications:

- Brave
- Chrome
- Edge
- Firefox
- VS Code
- Visual Studio
- Antigravity
- SSMS
- Postman
- Docker Desktop
- Git Bash
- Windows Terminal
- File Explorer

Templates should only assist discovery.

They must not install anything.

---

# 74. DOCKER / DEVELOPMENT SAFETY

Do not automatically manipulate Docker Desktop's internal windows unless explicitly configured.

Do not:

- stop Docker
- restart Docker
- modify Docker data
- modify WSL
- modify containers

The workspace manager only controls the application window.

---

# 75. SQL SERVER SAFETY

Do not:

- stop SQL Server
- restart SQL Server
- change SQL configuration
- modify databases

SSMS should be treated as an ordinary application window.

---

# 76. BROWSER SAFETY

Do not modify:

- browser profile
- cookies
- saved passwords
- extensions
- history

The manager should only launch/move the browser window.

---

# 77. USER CONFIRMATION

Before the first real execution, show:

```text
Workspace Execution

The following actions will occur:

✓ Create missing Virtual Desktops
✓ Launch configured applications
✓ Move application windows

No applications will be uninstalled.
No processes will be terminated.

Continue?

[Cancel] [Run Workspace]
```

Allow the user to disable this confirmation later in Settings.

---

# 78. FIRST-RUN EXPERIENCE

On first launch:

Show a setup wizard.

### Step 1

Welcome

### Step 2

Detect Virtual Desktops

### Step 3

Configure desktops

### Step 4

Detect applications

### Step 5

Assign applications

### Step 6

Review

### Step 7

Save configuration

### Step 8

Do NOT execute automatically.

Show:

```text
Workspace configuration completed.

When you are ready:

[Launch Workspace]
```

---

# 79. EXAMPLE DEFAULT CONFIGURATION

Create the initial workspace:

```text
Desktop 1 — Browser
 └── Brave

Desktop 2 — Development
 └── Google Antigravity

Desktop 3 — Database
 └── SQL Server Management Studio

Desktop 4 — API
 └── Postman
```

The user must be able to change everything.

---

# 80. ADDING NEW APPLICATION LATER

This must be easy.

Example:

User opens:

```text
Desktop 2 → Add Application
```

Selects:

```text
Visual Studio Code
```

Then:

```text
Desktop 2
 ├── Antigravity
 └── Visual Studio Code
```

Save.

No source-code modification should be required.

---

# 81. MOVING AN APPLICATION LATER

Example:

```text
Desktop 1
 └── Brave
```

User changes:

```text
Brave → Desktop 4
```

After saving:

```text
Desktop 4
 ├── Postman
 └── Brave
```

The configuration should persist.

---

# 82. WORKSPACE PROFILES

Implement multiple workspace profiles if practical.

Example:

```text
Work
Development
Database
Personal
```

Each profile can have different application assignments.

Example:

### Work

```text
Desktop 1 → Browser
Desktop 2 → CRM
Desktop 3 → Outlook
Desktop 4 → Teams
```

### Development

```text
Desktop 1 → Browser
Desktop 2 → Antigravity + VS Code
Desktop 3 → SSMS
Desktop 4 → Postman + Docker
```

The active profile can be selected from the UI.

This feature should be implemented only if it does not compromise reliability.

---

# 83. PROFILE IMPORT/EXPORT

Each workspace profile should be exportable.

Example:

```text
development-workspace.json
```

---

# 84. ACCESSIBILITY

UI should support:

- keyboard navigation
- readable text
- sufficient contrast
- clear status indicators
- tooltips
- sensible tab order
- scalable UI where possible

Do not rely solely on color to communicate status.

---

# 85. UI DESIGN

The UI should look like a professional Windows utility.

Avoid:

- excessive gradients
- unnecessary animations
- "AI-looking" glowing interfaces
- excessive rounded cards
- giant empty areas
- flashy dashboards

Prefer:

- clean Windows-style layout
- clear typography
- compact controls
- useful status indicators
- professional spacing
- light/dark theme support if practical

---

# 86. DARK / LIGHT THEME

If supported:

```text
Theme:
[System]
[Light]
[Dark]
```

Default:

```text
System
```

---

# 87. ACCESS TO RAW CONFIGURATION

Provide:

```text
Open Configuration Folder
```

and optionally:

```text
Open workspace.json
```

But warn the user that manually invalid configuration can break workspace execution.

---

# 88. DIAGNOSTICS

Provide:

```text
Generate Diagnostic Report
```

The report should include:

- Windows version
- application version
- Virtual Desktop count
- configured applications
- detected executable paths
- process detection results
- API capability information
- recent errors

Do NOT include sensitive information unnecessarily.

Redact:

- passwords
- tokens
- authentication data
- browser profile data
- full command lines containing secrets

---

# 89. PRIVACY

The application should operate locally.

Do not send:

- process data
- window titles
- configuration
- logs

to external servers.

Do not add telemetry unless explicitly requested.

---

# 90. UPDATE MECHANISM

Do NOT implement automatic downloading/updating in the first version.

If an update mechanism is considered later, it must be separately designed and explicitly approved.

---

# 91. DOCUMENTATION

Create a comprehensive README.

Include:

1. What the application does
2. Supported Windows versions
3. Requirements
4. Installation
5. First-run setup
6. Configuration
7. Adding applications
8. Moving applications between desktops
9. Multiple applications per desktop
10. Workspace profiles
11. Dry-run mode
12. Troubleshooting
13. Logs
14. Diagnostics
15. Known Windows limitations
16. Uninstall instructions
17. Security considerations

---

# 92. PREREQUISITES

Document all dependencies.

If Python is used, provide:

```text
Python version
pip packages
```

If PowerShell is used, provide:

```text
PowerShell version
required modules
```

Pin versions where appropriate.

Do not blindly install dependencies from untrusted sources.

Use official package repositories.

---

# 93. INSTALLER

If practical, create an optional packaging method.

For Python, consider:

```text
PyInstaller
```

or another appropriate Windows packaging system.

The packaged application should not require Python to be manually installed.

However, development mode must remain available.

---

# 94. EXECUTION POLICY

If PowerShell is selected:

Do NOT tell the user to permanently weaken system-wide security settings.

Avoid:

```powershell
Set-ExecutionPolicy Unrestricted
```

If an execution-policy adjustment is genuinely necessary, use the narrowest appropriate scope and explain the security implications.

Prefer:

```text
CurrentUser
```

over system-wide changes where appropriate.

---

# 95. ADMINISTRATOR REQUIREMENTS

Clearly document:

```text
Administrator required: No
```

if normal functionality does not require it.

If a specific operation requires elevation:

- explain why
- request elevation only for that operation
- do not run the entire application as Administrator unnecessarily

---

# 96. INSTALLATION SAFETY

Do not:

- download arbitrary executables
- modify PATH automatically
- modify registry unnecessarily
- disable Windows Defender
- disable SmartScreen
- disable UAC
- modify firewall rules

---

# 97. UNINSTALL

Provide documentation for removing the application.

Uninstall should remove:

- application files
- optional startup entry

But ask whether the user wants to preserve:

```text
Workspace configuration
Logs
```

Do not delete user configuration silently.

---

# 98. IMPORTANT WINDOWS LIMITATIONS

Research and document actual limitations of the selected Virtual Desktop API.

Do not claim that Windows exposes functionality if it does not.

If an operation cannot be reliably implemented:

1. Detect that limitation.
2. Tell the user.
3. Provide the safest fallback.
4. Clearly mark the fallback.
5. Do not pretend it succeeded.

---

# 99. API COMPATIBILITY

Before implementation, investigate the currently supported Windows APIs/libraries for:

- Virtual Desktop enumeration
- desktop creation
- desktop switching
- moving windows
- determining window desktop membership

Prefer actively maintained approaches.

If a third-party library is used, document:

- project/package name
- version
- license
- maintenance status
- limitations
- why it was selected

---

# 100. DO NOT USE OBSOLETE / FRAGILE TECHNIQUES AS PRIMARY IMPLEMENTATION

Avoid making the entire application dependent on:

```text
SendKeys
pyautogui
Win + Ctrl + D
Win + Ctrl + Left
Win + Ctrl + Right
```

unless there is no reliable API alternative.

If used as fallback, isolate it inside a dedicated fallback provider.

---

# 101. OBSERVABILITY

Every major action should produce a traceable event.

Example:

```text
WorkspaceLaunchStarted
DesktopDiscoveryCompleted
DesktopCreated
ApplicationDiscoveryStarted
ApplicationLaunchStarted
WindowDetected
WindowMoveStarted
WindowMoveCompleted
VerificationCompleted
WorkspaceLaunchCompleted
```

This will make troubleshooting much easier.

---

# 102. FINAL STATUS REPORT

At the end of every operation, show:

```text
Workspace Operation Complete

Virtual Desktops:
4 / 4

Applications:
4 configured
4 detected
3 launched/reused
4 assigned
1 warning

Errors:
0

Warnings:
1

Duration:
8.42 seconds
```

---

# 103. DEVELOPMENT WORKFLOW FOR ANTIGRAVITY

Before writing the final code:

## Phase 1 — Analyze

Identify:

- Windows Virtual Desktop API options
- chosen implementation approach
- library limitations
- window-management limitations
- packaging requirements

## Phase 2 — Design

Create:

- architecture
- data models
- configuration schema
- UI structure
- execution flow
- error-handling strategy

## Phase 3 — Safety Review

Create a table:

| Risk | Mitigation |
|---|---|
| Duplicate applications | Process/window detection |
| Duplicate desktops | Desktop enumeration |
| Wrong window moved | HWND/process verification |
| Missing application | Discovery + graceful skip |
| API failure | Retry + fallback |
| Configuration corruption | Validation + backups |
| Unexpected execution | Explicit user action |
| Permission problems | No automatic elevation |
| Data loss | No file/application deletion |

## Phase 4 — Implementation

Build the complete application.

## Phase 5 — Static Validation

Check:

- syntax
- imports
- configuration schema
- UI references
- dependency declarations
- obvious runtime errors
- unsafe subprocess usage
- hard-coded user paths
- unsafe elevation
- accidental destructive commands

## Phase 6 — Tests

Run only safe/non-destructive tests where possible.

Mock Windows desktop operations.

## Phase 7 — Final Review

Perform a final production-readiness review.

Do NOT launch the application.

---

# 104. REQUIRED DELIVERABLES

Provide:

### Application

Complete production-ready source code.

### UI

Complete functional GUI.

### Configuration

Default workspace configuration.

### Tests

Unit/integration tests with Windows API operations mocked where necessary.

### Documentation

README.md.

### Dependency file

For example:

```text
requirements.txt
```

or equivalent.

### Configuration schema

Document the JSON configuration format.

### Troubleshooting

Detailed troubleshooting guide.

### Security Review

Document:

- permissions
- process execution
- filesystem access
- network access
- configuration security
- logging/privacy

### Architecture Document

Explain:

```text
UI
 ↓
Workspace Manager
 ↓
Desktop Provider
Window Provider
Process Provider
Application Discovery
Configuration Store
Logging
```

---

# 105. FINAL QUALITY STANDARD

The finished application must feel like a real Windows utility rather than a generated script.

It must be:

- reliable
- maintainable
- idempotent
- configurable
- testable
- safe
- transparent
- recoverable
- user-controlled
- production-oriented

Do not sacrifice reliability for visual effects.

Do not sacrifice safety for automation.

Do not sacrifice maintainability by putting everything into one script.

---

# 106. FINAL ACCEPTANCE TEST

Before considering the project complete, verify that the design supports all of these scenarios:

### Scenario 1

User has 2 Virtual Desktops.

Application requires 4.

Result:

```text
2 additional desktops created.
```

### Scenario 2

User already has 4 desktops.

Result:

```text
No additional desktops created.
```

### Scenario 3

User has 6 desktops.

Result:

```text
Existing 6 desktops preserved.
Workspace uses first 4 configured desktops.
```

### Scenario 4

Brave is already running.

Result:

```text
No unnecessary duplicate launch.
Existing window assigned to configured desktop.
```

### Scenario 5

Postman is not running.

Result:

```text
Postman launched.
Window detected.
Window assigned.
```

### Scenario 6

Postman is not installed.

Result:

```text
Warning displayed.
Other applications continue.
```

### Scenario 7

Desktop 2 contains:

```text
Antigravity
VS Code
Git Bash
```

Result:

```text
All three can be assigned to Desktop 2.
```

### Scenario 8

User moves Brave from Desktop 1 to Desktop 4 in the UI.

Result:

```text
Configuration saved.
Future workspace launches use Desktop 4.
```

### Scenario 9

User adds Docker Desktop to Desktop 2.

Result:

```text
Existing applications remain.
Docker Desktop is added.
```

### Scenario 10

User runs Launch Workspace twice.

Result:

```text
No unnecessary duplicate desktops.
No unnecessary duplicate processes.
Workspace is synchronized safely.
```

### Scenario 11

User starts the manager.

Result:

```text
Manager opens.
Nothing is launched automatically by default.
```

### Scenario 12

User clicks:

```text
Launch Workspace
```

Result:

```text
Confirmation appears if enabled.
Workspace execution begins only after explicit confirmation.
```

---

# 107. MOST IMPORTANT RULES

The following rules override convenience:

1. **Never automatically execute the generated application during development.**
2. **Never automatically delete Virtual Desktops.**
3. **Never automatically kill application processes.**
4. **Never uninstall applications.**
5. **Never delete user files.**
6. **Never modify development data.**
7. **Never silently elevate to Administrator.**
8. **Never silently create startup automation.**
9. **Never claim an operation succeeded without verification when verification is available.**
10. **Never depend entirely on keyboard simulation when a reliable Windows API is available.**
11. **Never hard-code application paths as the only method of discovery.**
12. **Never limit a desktop to one application.**
13. **Never require source-code changes to add or reassign applications.**
14. **Never overwrite existing workspace configuration without validation/backup.**
15. **Never automatically launch the workspace simply because the manager was opened.**
16. **Do not run the generated application until I explicitly tell you to run it.**

---

# FINAL INSTRUCTION TO GOOGLE ANTIGRAVITY

Start by analyzing the requirements and producing the architecture/design internally in the project documentation.

Then implement the complete application.

Do not stop at a prototype.

Do not create a fake UI with non-functional buttons.

Every UI control that is presented as functional must be connected to real application logic or clearly marked as not yet implemented.

Prioritize reliable Windows API integration, safe process/window management, persistent configuration, and idempotent workspace synchronization.

After implementation, perform static validation and safe mocked tests.

Finally, provide me with:

1. Project structure
2. Files created
3. Dependencies
4. Installation instructions
5. Configuration instructions
6. Testing results
7. Known Windows/API limitations
8. Security/safety review
9. How to package the application
10. How to run it manually

**DO NOT RUN THE APPLICATION.**

Wait for my explicit instruction before executing the generated workspace manager.