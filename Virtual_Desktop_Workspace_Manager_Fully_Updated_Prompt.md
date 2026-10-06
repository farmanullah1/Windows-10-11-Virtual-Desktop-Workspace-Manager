# BUILD A PRODUCTION-READY WINDOWS 10/11 VIRTUAL DESKTOP WORKSPACE MANAGER

## 1. ROLE

Act as a senior Windows desktop software engineer, Windows API engineer, application architect, security engineer, QA engineer, and UX engineer.

Build a **production-quality Windows 10/11 Virtual Desktop Workspace Manager**.

This is a real desktop utility intended for daily use.

It is NOT:

* a prototype
* a proof of concept
* a toy script
* a keyboard macro
* a fake dashboard
* a UI mockup
* a collection of disconnected buttons
* a one-file automation script

The application must provide a reliable graphical interface for creating, configuring, launching, monitoring, and synchronizing persistent application workspaces across Windows Virtual Desktops.

The application must prioritize:

1. Reliability
2. Safety
3. Correct Windows API integration
4. Accurate window detection
5. Correct Virtual Desktop assignment
6. Idempotent execution
7. User control
8. Persistent configuration
9. Recovery
10. Testability
11. Maintainability
12. Professional UI/UX

Do not sacrifice reliability for visual effects.

Do not sacrifice safety for automation.

Do not sacrifice maintainability by putting everything into one giant script.

---

# 2. ABSOLUTE DEVELOPMENT SAFETY RULE

## DO NOT RUN THE GENERATED APPLICATION

This rule has the highest priority.

While working inside Google Antigravity:

* Create the complete project.
* Create all source files.
* Create configuration files.
* Create documentation.
* Create tests.
* Create mock providers.
* Perform static validation.
* Perform safe isolated tests where possible.

But:

**DO NOT RUN THE GENERATED APPLICATION.**

Do NOT:

* launch the generated GUI
* launch the workspace manager
* create Windows Virtual Desktops
* delete Virtual Desktops
* switch my real desktop
* move my real application windows
* launch Brave
* launch Google Antigravity
* launch SQL Server Management Studio
* launch Postman
* launch Docker
* launch Visual Studio
* launch VS Code
* launch Git Bash
* modify my current workspace
* modify my Windows settings
* create Windows startup entries
* create scheduled tasks
* install the application
* execute the real workspace configuration

Do not "test" the application by accidentally operating on the real Windows desktop.

If validation is required, use:

* static analysis
* syntax checking
* mocked providers
* fake application providers
* fake desktop providers
* fake window providers
* temporary isolated test data
* configuration validation
* unit tests
* integration tests that do not manipulate the real Virtual Desktop environment

If a command could affect the host Windows environment, do not execute it automatically.

Wait for my explicit instruction before running the generated application.

The instruction:

> "Run the application"

must be treated as a separate future authorization.

Do not interpret:

* "build it"
* "finish it"
* "test it"
* "validate it"
* "complete the project"

as permission to launch the application.

---

# 3. PRIMARY OBJECTIVE

Build an application that can:

1. Detect Windows Virtual Desktops.
2. Detect the current Virtual Desktop.
3. Create additional Virtual Desktops when required and when supported.
4. Identify stable desktop IDs where available.
5. Maintain user-defined workspace configurations.
6. Assign one application to a desktop.
7. Assign multiple applications to the same desktop.
8. Add applications later without source-code changes.
9. Remove applications from the workspace without uninstalling them.
10. Reassign applications between desktops.
11. Detect already-running applications.
12. Detect application windows.
13. Identify the correct top-level application window.
14. Move windows to the desired Virtual Desktop when supported.
15. Verify the move when technically possible.
16. Launch applications when configured to do so.
17. Avoid unnecessary duplicate application launches.
18. Synchronize actual state with desired state.
19. Provide dry-run mode.
20. Provide a Launch Workspace operation.
21. Provide a Sync Workspace operation.
22. Provide cancellation.
23. Provide an emergency stop.
24. Persist configuration.
25. Back up configuration.
26. Import/export configuration.
27. Support workspace profiles.
28. Provide diagnostics.
29. Provide detailed logs.
30. Provide a professional Windows desktop UI.
31. Operate without Administrator privileges whenever possible.
32. Never delete user-created Virtual Desktops automatically.
33. Never kill user applications automatically.
34. Never uninstall applications.
35. Never delete user files.
36. Never modify development data.
37. Never silently enable startup automation.
38. Never execute automatically simply because the manager opens.

---

# 4. IMPORTANT TECHNICAL PRINCIPLE

Do not assume that Windows provides one simple public API for every Virtual Desktop operation.

Before implementation, investigate the currently appropriate Windows mechanisms for:

* Virtual Desktop enumeration
* Virtual Desktop creation
* Virtual Desktop deletion
* Virtual Desktop switching
* Virtual Desktop IDs
* current desktop detection
* window desktop detection
* moving windows between desktops

Microsoft's documented `IVirtualDesktopManager` supports operations including obtaining a window's desktop ID, checking whether a window is on the current desktop, and moving a window to a specified desktop.

However, do NOT assume that the documented public API alone provides every operation required by this application.

If enumeration, creation, switching, or other functionality requires undocumented/internal Windows interfaces or a third-party library:

1. Identify that dependency.
2. Verify compatibility.
3. Isolate it behind an abstraction.
4. Detect unsupported environments.
5. Fail gracefully.
6. Do not pretend unsupported functionality succeeded.
7. Document the limitation.
8. Provide the safest fallback possible.

If using `pyvda` or another third-party library, verify the actual current package/version and Windows compatibility before implementation. Do not blindly copy old examples.

---

# 5. TECHNOLOGY SELECTION

You may choose:

* Python
* PowerShell
* another appropriate Windows desktop technology

However, choose based on reliability rather than convenience.

For Python, investigate appropriate technologies such as:

* pywin32
* psutil
* pyvda or another maintained Virtual Desktop integration library
* PySide/PyQt
* tkinter only if it provides an adequate professional UI

For PowerShell, use proper Windows APIs/modules rather than relying primarily on simulated keyboard input.

If another technology is substantially more reliable for Windows desktop integration, explain why it is selected.

Before implementation, create:

`docs/technology-decision.md`

Include:

* selected technology
* alternatives considered
* reasons for selection
* dependencies
* Windows compatibility
* known API limitations
* packaging implications
* maintenance considerations

Do not choose technology merely because it is easiest to code.

---

# 6. WINDOWS COMPATIBILITY

Target:

* Windows 10
* Windows 11
* 64-bit preferred

The application must detect:

* Windows version
* build number
* architecture

Create a compatibility/capability layer.

Example:

```text
Windows Environment
        ↓
Capability Detection
        ↓
Virtual Desktop Provider
        ↓
Workspace Engine
```

The application must not blindly assume that every Windows build behaves identically.

At startup, determine whether required functionality is available.

Display capability status such as:

```text
Virtual Desktop Support
✓ Enumeration
✓ Current Desktop
✓ Window Desktop Detection
✓ Window Movement
✓ Desktop Creation

Compatibility:
Windows 11
Build: XXXXX

Provider:
Supported
```

If functionality is unavailable:

```text
⚠ Virtual Desktop creation is unavailable on this system.

The manager can still provide:
- configuration
- application discovery
- dry-run
- diagnostics
```

Never fake functionality.

---

# 7. DEFAULT WORKSPACE

Create an editable initial workspace:

```text
Desktop 1 — Browser
    └── Brave Browser

Desktop 2 — Development
    └── Google Antigravity

Desktop 3 — Database
    └── SQL Server Management Studio

Desktop 4 — API Development
    └── Postman
```

These are ONLY defaults.

They must never be permanently hard-coded.

The user must be able to:

* rename desktops
* add desktops
* remove workspace configuration
* add applications
* remove applications
* reassign applications
* configure launch behavior
* configure matching rules
* create profiles

---

# 8. CRITICAL DESKTOP IDENTITY RULE

Do NOT permanently identify desktops only by:

```text
Desktop 1
Desktop 2
Desktop 3
Desktop 4
```

The displayed number is a UI position.

Where Windows exposes a stable desktop identifier/GUID, store it.

Use a model such as:

```json
{
  "workspaceDesktopId": "stable-manager-id",
  "windowsDesktopId": "windows-guid-if-available",
  "displayOrder": 1,
  "name": "Browser"
}
```

Important:

Windows Virtual Desktop order may change.

Users may manually create or reorder desktops.

Therefore:

* refresh the desktop mapping before execution
* do not blindly assume Desktop 1 is always the same physical Windows desktop
* do not permanently bind configuration to a position without considering identity
* detect stale mappings
* show conflicts to the user
* require explicit remapping when identity cannot be safely determined

---

# 9. USER-CREATED DESKTOP SAFETY

The manager must NEVER automatically:

* delete user desktops
* remove extra desktops
* rearrange unrelated desktops
* move unrelated application windows
* close unrelated applications

If the system has:

```text
6 existing desktops
```

and the workspace needs:

```text
4 desktops
```

preserve all 6.

Do not assume that the first four are safe to control if their identities cannot be established.

Provide a clear desktop mapping UI.

Example:

```text
Workspace Desktop     Windows Desktop

Browser               Desktop 1
Development           Desktop 2
Database              Desktop 4
API                   Desktop 5
```

Allow the user to change the mapping.

---

# 10. DESKTOP MANAGEMENT

Provide:

* Detect Desktops
* Refresh
* Create Desktop
* Open/Switch Desktop
* Rename workspace label
* Map workspace desktop to Windows desktop
* Add desktop to workspace configuration

Do not imply that a custom workspace name changes Windows' own desktop name unless the Windows API actually supports that behavior.

The manager's custom name is its own metadata.

---

# 11. APPLICATION MANAGEMENT

Each application must have a stable unique ID.

Example:

```json
{
  "id": "brave-browser",
  "name": "Brave Browser",
  "executable": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
  "arguments": [],
  "workspaceDesktopId": "development-browser",
  "enabled": true
}
```

Never use display names as the primary identity.

---

# 12. ADD APPLICATION

The UI must provide:

```text
+ Add Application
```

Support:

### Method 1 — Browse

Select an `.exe` using the Windows file picker.

### Method 2 — Running Applications

Display currently running applications.

Show:

```text
Application
Process
PID
Executable
Window
HWND
Desktop
```

Allow:

```text
Add to Workspace
```

### Method 3 — Start Menu

Discover applications from Start Menu shortcuts where practical.

### Method 4 — Desktop Shortcuts

Discover desktop shortcuts where practical.

### Method 5 — Known Installation Locations

Use controlled discovery.

Never recursively scan the entire `C:\` drive.

Never perform expensive unrestricted searches.

---

# 13. APPLICATION DISCOVERY PRIORITY

Use this resolution order:

1. User-configured executable
2. Currently detected running executable
3. Start Menu shortcut
4. Desktop shortcut
5. Known installation path
6. Registry where appropriate
7. Controlled environment-variable resolution
8. Controlled search

Do not overwrite a valid user-selected executable just because automatic discovery finds another copy.

If multiple candidates exist:

```text
Multiple installations detected.

1. C:\...
2. C:\...
3. C:\...

Select preferred installation.
```

Remember the user's choice.

---

# 14. APPLICATION PROFILE

Support at least:

```text
Application Name
Executable Path
Arguments
Working Directory
Target Workspace Desktop
Enabled
Launch Mode
Move Existing Windows
Window Matching Strategy
Window Policy
Launch Timeout
Window Detection Timeout
Retry Count
Launch Delay
```

Optional:

```text
Environment Variables
Priority
Notes
Custom Detection Rules
```

---

# 15. WORKING DIRECTORY

Allow an optional working directory.

Validate it.

Do not automatically create arbitrary directories.

Do not delete directories.

---

# 16. ARGUMENT SAFETY

Arguments must be stored separately from executable paths.

Prefer a structured representation rather than shell-command strings.

Do NOT execute configuration as a shell command.

Do NOT allow:

* arbitrary PowerShell expressions
* shell pipelines
* encoded commands
* command substitution
* downloaded commands
* remote execution

Use safe process creation APIs.

Do not use:

```text
shell=True
```

unless there is an explicitly justified and isolated case.

Prefer:

```text
executable + argument list
```

rather than concatenated shell commands.

---

# 17. ENVIRONMENT VARIABLES

Allow controlled expansion of variables such as:

```text
%ProgramFiles%
%ProgramFiles(x86)%
%LocalAppData%
%AppData%
%UserProfile%
%SystemDrive%
```

Do not blindly execute environment variables as commands.

---

# 18. APPLICATION LAUNCH MODES

Support:

### Launch if missing

Launch only if the application is not already available.

### Reuse existing

Prefer an existing compatible process/window.

### Always launch

Only if explicitly configured.

### Do not launch

Only detect/move existing windows.

### Ask

Prompt the user when execution begins.

Default:

```text
Launch if missing
```

but user confirmation must still control actual workspace execution.

---

# 19. DUPLICATE PREVENTION

The application must avoid unnecessary duplicate instances.

Before launching:

1. Find matching processes.
2. Determine executable path.
3. Determine command line where available.
4. Enumerate windows.
5. Match configured application.
6. Determine whether an existing compatible window is usable.

Do NOT simply do:

```text
process name == brave.exe
```

because multiple installations/processes may exist.

---

# 20. APPLICATION MATCHING

Provide multiple matching strategies:

### Executable path

Exact executable path.

### Executable name

Example:

```text
brave.exe
```

### Process ID

Only for temporary runtime identification, never persistent identity.

### Process name + path

Preferred fallback.

### Window title

Contains.

### Window title regex

Optional.

### Class name

Optional.

### HWND

Only as a runtime identity because HWNDs can change.

### Custom matching rule

Optional.

Use a confidence score when multiple windows match.

Example:

```text
Executable path match       +50
Executable name match       +20
Process match               +15
Window title match          +10
Class match                  +5
```

If confidence is too low:

```text
⚠ Multiple possible windows detected.

Select the window to manage.
```

Never move a questionable window automatically.

---

# 21. WINDOW DETECTION

A process is NOT the same thing as a window.

One application may have:

* multiple processes
* multiple windows
* child windows
* helper processes
* splash screens
* background processes
* notification windows

Enumerate top-level windows.

Inspect:

* HWND
* PID
* executable
* process path
* title
* class name
* visibility
* minimized state
* maximized state
* owner window
* parent/child relationship
* cloaked state where available

Ignore:

* invisible windows
* child windows
* helper windows
* notification-only windows
* system windows
* irrelevant launcher windows

---

# 22. MULTI-WINDOW POLICY

Support:

1. Move all matching windows
2. Move main window
3. Move selected window
4. Ask user
5. Match by title
6. Match by process
7. Match by configured rule

Example:

```text
Brave
3 matching windows found.

○ Move all
○ Move main window
○ Select specific window
○ Do nothing
```

Never assume every application's window architecture is identical.

---

# 23. WINDOW READY DETECTION

Never assume:

```text
Process started = Window ready
```

Instead:

1. Start process.
2. Poll for process.
3. Enumerate windows.
4. Match candidate window.
5. Verify visibility/usability.
6. Attempt desktop assignment.
7. Verify assignment if possible.

Use:

```text
poll interval: configurable
window timeout: configurable
```

Default example:

```text
Polling: 250 ms
Window timeout: 15 seconds
```

Do not use unnecessarily long fixed sleeps.

Prefer state-based polling.

---

# 24. WINDOW LIFECYCLE RACE CONDITIONS

Account for:

* process starting slowly
* process exiting immediately
* splash screen appearing first
* main window appearing later
* HWND changing
* window being recreated
* application opening multiple windows
* application becoming unresponsive
* user manually moving the window while synchronization is running

Re-check state before destructive or disruptive actions.

If the user changes a window while synchronization is in progress, do not blindly override the user's action unless the user explicitly requested aggressive synchronization.

---

# 25. USER-CONTROLLED VS AUTOMATED MOVES

The application must distinguish:

```text
Manager-initiated move
```

from:

```text
User manually moved window
```

Normal operation should NOT constantly fight the user.

A synchronization operation should reconcile state only when explicitly invoked or when an explicitly enabled automation mode is active.

---

# 26. LAUNCH SEQUENCE

Use controlled sequencing:

```text
1. Validate configuration
2. Detect Windows capabilities
3. Detect desktops
4. Resolve desktop mappings
5. Detect applications
6. Show execution plan
7. Create missing desktops if approved
8. Launch applications where required
9. Wait for windows
10. Identify windows
11. Move windows
12. Verify
13. Produce final report
```

Do not launch everything simultaneously.

Applications assigned to the same desktop may be launched sequentially or concurrently only when safe and explicitly designed.

---

# 27. DRY RUN

Dry Run is mandatory.

Dry Run must perform NO real workspace modifications.

It must NOT:

* create desktops
* switch desktops
* move windows
* launch applications
* kill processes
* modify startup
* modify registry
* modify user files

Example:

```text
DRY RUN

Current desktops: 3
Required workspace desktops: 4

Would create:
Desktop 4

Applications:

Brave
✓ Executable found
✓ Existing window found
→ Would assign to Browser desktop

Antigravity
✓ Executable found
✗ No window
→ Would launch

SSMS
✓ Existing window
→ Would move

Postman
✗ Executable not found
→ Would skip
```

---

# 28. EXECUTION PLAN PREVIEW

Before a real workspace operation, show a plan.

Example:

```text
Workspace Execution Plan

Desktop changes
+ Create Desktop 4

Applications
✓ Reuse Brave
→ Move Brave → Browser
→ Launch Antigravity
→ Move SSMS → Database
⚠ Postman unavailable

No applications will be uninstalled.
No processes will be terminated.
No files will be deleted.

[Cancel] [Run]
```

This should be especially visible on the first execution.

---

# 29. LAUNCH WORKSPACE VS SYNC WORKSPACE

These are separate operations.

## Launch Workspace

Ensures configured applications are launched/reused and assigned.

## Sync Workspace

Compares:

```text
Desired State
```

against:

```text
Actual State
```

and repairs only configured differences.

Define exact behavior in documentation.

Do not make Sync unexpectedly launch applications unless the application configuration explicitly permits it.

---

# 30. DESIRED STATE / ACTUAL STATE MODEL

Represent workspace state explicitly.

Example:

```text
Desired:

Browser
  Brave

Development
  Antigravity
  VS Code

Database
  SSMS

API
  Postman
```

Actual:

```text
Browser
  Brave → wrong desktop

Development
  Antigravity

Database
  SSMS

API
  Postman → not running
```

The synchronization engine should produce:

```text
Plan:

Move Brave
Launch Postman
Verify Antigravity
No action for SSMS
```

The plan must be visible in logs and optionally in the UI.

---

# 31. OPERATION PLANNER

Separate:

```text
Discovery
```

from:

```text
Planning
```

from:

```text
Execution
```

from:

```text
Verification
```

Architecture:

```text
Actual State
     ↓
Desired State
     ↓
Planner
     ↓
Execution Plan
     ↓
User Approval
     ↓
Executor
     ↓
Verification
     ↓
Final State
```

This prevents arbitrary actions from being executed directly from UI callbacks.

---

# 32. OPERATION SNAPSHOT

Before execution, create an in-memory operation snapshot containing:

* current desktop IDs
* current desktop mapping
* configured applications
* detected processes
* detected windows
* relevant window desktop IDs
* planned actions

Do not treat the snapshot as permanent truth.

Revalidate important state before each action.

---

# 33. TRANSACTION-LIKE EXECUTION

Workspace execution is NOT a true database transaction.

Do not claim that all Windows operations can be rolled back.

Instead use:

```text
Plan
→ Execute
→ Verify
→ Recover what can safely be recovered
→ Report
```

If a window move succeeds and a later application fails, do NOT automatically move the successful window back unless the user has explicitly configured rollback behavior.

Never make rollback more dangerous than the original operation.

---

# 34. CANCELLATION

Provide:

```text
Stop / Cancel
```

Cancellation should:

* stop future actions
* stop waiting loops
* prevent new application launches
* prevent new window moves
* allow the current non-interruptible API call to finish if necessary

It must NOT:

* kill applications
* terminate processes
* delete desktops
* forcibly undo already completed actions

The final report must say:

```text
Operation cancelled.

Completed:
3

Skipped:
4

Not executed:
2
```

---

# 35. EMERGENCY STOP

Provide a clearly visible:

```text
STOP
```

button while operations are running.

Its purpose is:

```text
Prevent additional actions.
```

It must NOT kill processes.

It must NOT close applications.

It must NOT delete desktops.

---

# 36. CONCURRENCY

Only one workspace operation may execute at a time.

Prevent:

```text
Launch Workspace
+
Sync Workspace
```

from running simultaneously.

If another operation is requested:

```text
Workspace operation already running.

Please wait or cancel the current operation.
```

Disable conflicting UI actions while execution is active.

---

# 37. SINGLE INSTANCE

The manager itself should normally run as one instance.

If a second instance starts:

```text
Virtual Desktop Workspace Manager is already running.
```

Optionally bring the existing window to the foreground.

Do not create duplicate background managers.

Do not create duplicate tray processes.

---

# 38. AUTOMATION ENABLE/DISABLE

Provide:

```text
Automation Enabled: ON/OFF
```

When OFF:

* do not launch applications
* do not move windows
* do not create desktops
* do not modify desktop state

The UI may still:

* inspect
* display
* validate
* edit configuration
* generate diagnostics
* run dry-run

---

# 39. STARTUP BEHAVIOR

Startup must be completely opt-in.

Provide separate options:

```text
☐ Start Manager with Windows

☐ Automatically launch workspace at Windows login
```

Both default:

```text
OFF
```

These are NOT the same setting.

Possible configurations:

```text
Manager only
Manager + workspace
Nothing
```

Do not silently create:

* Startup folder entries
* Registry Run entries
* Scheduled Tasks
* services

If startup is enabled, explain exactly what is being created.

Provide a UI option to disable/remove it.

---

# 40. SYSTEM TRAY

If implemented, support:

```text
Open Manager
Launch Workspace
Sync Workspace
Pause Automation
View Logs
Settings
Exit
```

Tray actions must follow the same confirmation and safety rules as the main UI.

Do not let the tray silently execute dangerous operations.

---

# 41. FIRST-RUN WIZARD

First launch should provide:

### Step 1

Welcome

### Step 2

Detect Windows capabilities

### Step 3

Detect Virtual Desktops

### Step 4

Choose workspace mapping

### Step 5

Discover applications

### Step 6

Assign applications

### Step 7

Configure launch behavior

### Step 8

Review execution plan

### Step 9

Save configuration

### Step 10

Finish

Do NOT execute the workspace.

Final message:

```text
Workspace configuration completed.

Nothing has been launched or moved.

When ready:

[Launch Workspace]
```

---

# 42. UI STRUCTURE

Create a professional desktop application.

Recommended navigation:

```text
Dashboard
Workspaces
Applications
Virtual Desktops
Execution
Logs
Diagnostics
Settings
About
```

---

# 43. DASHBOARD

Show:

```text
Virtual Desktop Workspace Manager

Current Desktop:
Desktop 2 — Development

Workspace:
Development

Status:
✓ Ready

Virtual Desktops:
4

Configured Applications:
7

Running:
5

Missing:
1

Warnings:
1

Last Sync:
2026-10-06 14:30
```

Buttons:

```text
Launch Workspace
Sync Workspace
Dry Run
Refresh
Stop
Diagnostics
Settings
Logs
```

---

# 44. DESKTOP CARDS

Each desktop card should show:

* desktop number
* custom name
* Windows desktop identity/status
* current indicator
* assigned applications
* running status
* missing applications
* warning state

Actions:

```text
Open
Edit
Add Application
Sync
```

Example:

```text
┌─────────────────────────────┐
│ Desktop 2                   │
│ Development                 │
│                             │
│ ✓ Antigravity               │
│ ✓ VS Code                   │
│ ✓ Git Bash                  │
│                             │
│ [Open] [Edit] [+ Add App]  │
└─────────────────────────────┘
```

---

# 45. APPLICATION LIST

Provide:

```text
Application
Desktop
Executable
Status
Windows
Launch Mode
Enabled
```

Actions:

```text
Edit
Move
Open
Detect
Remove
```

Provide search/filtering.

---

# 46. DRAG-AND-DROP ASSIGNMENT

If practical, allow:

```text
Drag Brave
from Desktop 1
to Desktop 4
```

The UI must ask:

```text
Update workspace assignment?

This changes where Brave will be managed during future workspace operations.

[Cancel] [Save]
```

If Brave is currently running:

```text
Move currently running window now?

[Later] [Move Now]
```

Never move the running window merely because the user dragged a configuration card unless the user explicitly confirms.

---

# 47. DESKTOP EDITOR

Allow:

```text
Name
Mapped Windows Desktop
Description
Applications
```

Do not expose fake desktop names as if they were Windows system names.

---

# 48. APPLICATION EDITOR

Include:

```text
Application Name
Executable
Browse
Detect
Arguments
Working Directory
Desktop
Enabled

Launch Mode
Window Policy
Matching Strategy

Launch Delay
Window Timeout
Retry Count
```

Provide validation indicators:

```text
✓ Executable exists
✓ Desktop mapping valid
⚠ Multiple matching windows
⚠ Executable unavailable
```

---

# 49. REMOVE APPLICATION

Removing an application means:

```text
Remove workspace configuration
```

It does NOT mean:

* uninstall
* delete executable
* delete app data
* kill process
* remove registry entries

Confirmation:

```text
Remove Brave from this workspace?

This will not uninstall Brave.

[Cancel] [Remove]
```

---

# 50. APPLICATION TEMPLATES

Optional templates may assist discovery for:

* Brave
* Chrome
* Edge
* Firefox
* VS Code
* Visual Studio
* Google Antigravity
* SSMS
* Postman
* Docker Desktop
* Git Bash
* Windows Terminal
* File Explorer

Templates must never install applications.

They must never force paths.

They must never override user-selected paths.

---

# 51. BRAVE

Support detection through:

* configured path
* running process
* Start Menu
* known installation locations

Possible locations may include:

```text
%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe
%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe
%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe
```

Do not modify:

* profiles
* cookies
* passwords
* history
* extensions
* browser settings

---

# 52. GOOGLE ANTIGRAVITY

Do NOT assume Antigravity is a website.

Attempt to detect:

* installed application
* Start Menu shortcut
* running process
* user-selected executable
* known installation location

If not detected:

```text
Google Antigravity was not detected.

[Browse]
[Select Running Application]
[Skip]
```

Do not substitute a random web URL.

---

# 53. SQL SERVER MANAGEMENT STUDIO

Support version variations.

Do not assume one SSMS executable path.

Use:

* user-selected executable
* Start Menu discovery
* controlled installation discovery
* running process detection

Do not:

* stop SQL Server
* restart SQL Server
* modify SQL configuration
* modify databases

SSMS is simply an application window for this manager.

---

# 54. POSTMAN

Support versioned installations.

Check appropriate user installation locations such as:

```text
%LocalAppData%\Postman\
```

Support versioned executables.

Do not blindly assume a single version.

If multiple versions are found, allow the user to choose.

---

# 55. DEVELOPMENT SAFETY

Never manipulate:

* Git repositories
* source code
* Docker data
* WSL
* SQL Server databases
* browser profiles
* Node projects
* Python environments
* Visual Studio projects
* VS Code workspaces

The manager only controls:

* configured application processes/windows
* Virtual Desktop state
* its own configuration
* its own logs

---

# 56. FILESYSTEM SAFETY

Do not:

* delete user files
* clean temporary directories
* clean Downloads
* clean Desktop
* modify source code
* modify Git data
* modify Docker storage
* modify SQL databases
* modify browser data

Do not add unrelated "cleanup" features.

---

# 57. NETWORK SAFETY

Version 1 should have no network requirement.

Do not add:

* telemetry
* analytics
* remote logging
* cloud synchronization
* remote commands
* update downloads

unless explicitly requested later.

If the application has zero network requirement, document:

```text
Network access:
Not required
```

---

# 58. CONFIGURATION STORAGE

Use user-level configuration.

Example:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\
```

Possible structure:

```text
config/
    settings.json
    workspaces.json
    applications.json

backups/

logs/

diagnostics/

cache/
```

Do not store mutable user configuration inside the installation directory.

---

# 59. CONFIGURATION VERSIONING

Every configuration must contain:

```json
{
  "schemaVersion": 1
}
```

Support migration.

Never silently discard fields from older configuration versions.

If migration fails:

```text
Configuration migration failed.

Your original configuration has been preserved.

[Restore Backup]
[Export Diagnostic]
```

---

# 60. ATOMIC CONFIGURATION WRITES

Do not directly overwrite the only configuration file.

Use:

```text
write temporary file
→ validate
→ flush
→ replace original
→ retain backup
```

If replacement fails:

* preserve the original
* report the error
* do not leave a partially written configuration

---

# 61. CONFIGURATION BACKUPS

Before significant changes:

* create a backup
* validate backup
* retain reasonable history

Do not generate hundreds of backups.

Use a retention policy such as:

```text
latest backup
+
limited historical backups
```

Never delete the only valid backup.

---

# 62. IMPORT / EXPORT

Support:

```text
Export Workspace
Import Workspace
```

Import must:

1. Parse
2. Validate schema
3. Validate IDs
4. Validate desktop mappings
5. Validate application records
6. Validate paths
7. Validate values
8. Preview changes
9. Ask confirmation
10. Back up existing configuration
11. Apply import atomically

Never replace configuration directly from an unvalidated file.

---

# 63. WORKSPACE PROFILES

Support multiple profiles.

Examples:

```text
Development
Work
Database
Personal
Testing
```

Each profile has its own:

* desktop assignments
* application assignments
* launch policies
* matching policies

Switching profile must NOT automatically execute it.

Example:

```text
Active Profile:
Development

[Switch Profile]
```

Changing profile changes configuration context only.

---

# 64. PROFILE IMPORT/EXPORT

Each profile must be exportable.

Example:

```text
development-workspace.json
```

Import/export must use the same validation and backup rules as normal configuration.

---

# 65. IDEMPOTENCY

Running the same operation multiple times must be safe.

Example:

```text
Launch Workspace
Launch Workspace
Launch Workspace
```

must NOT create:

```text
Brave
Brave
Brave
```

or:

```text
Desktop 1
Desktop 2
Desktop 3
Desktop 4
Desktop 5
Desktop 6
...
```

Instead:

```text
Existing desktop detected.
Existing process detected.
Existing window detected.
Synchronizing.
```

---

# 66. DESKTOP CREATION IDEMPOTENCY

Before creating a desktop:

1. Refresh desktop state.
2. Check required mapping.
3. Check stable identity.
4. Recalculate current count.
5. Create only what is genuinely missing.
6. Refresh after creation.
7. Verify creation.

Never blindly create four desktops every time.

---

# 67. DESKTOP MAPPING CONFLICTS

If the workspace expects:

```text
Database → Desktop GUID A
```

but Windows now reports a different mapping:

```text
Database → unknown
```

do NOT guess.

Show:

```text
Desktop mapping changed.

The manager cannot safely determine whether this is the same desktop.

[Review Mapping]
[Use Current Desktop]
[Cancel]
```

---

# 68. ERROR HANDLING

One application failure must not necessarily stop the entire operation.

Example:

```text
Brave       ✓
Antigravity ✓
SSMS        ✓
Postman     ⚠
```

Continue where safe.

Final result:

```text
Workspace completed with warnings.

Successful: 3
Warnings: 1
Errors: 0
Skipped: 0
```

---

# 69. ERROR CLASSIFICATION

Classify failures:

```text
ConfigurationError
CapabilityError
DiscoveryError
ProcessError
WindowDetectionError
DesktopError
WindowMoveError
PermissionError
TimeoutError
CancellationError
UnexpectedError
```

The UI should show user-friendly explanations while logs retain technical details.

---

# 70. RETRY POLICY

Retry only transient failures.

Example:

```text
Attempt 1
Attempt 2
Attempt 3
```

Use bounded/exponential delays where appropriate.

Never retry forever.

Do not retry configuration errors.

Do not repeatedly launch applications after uncertain launch state.

---

# 71. TIMEOUTS

Every potentially blocking operation must have a timeout.

Examples:

```text
Application launch timeout
Window detection timeout
Desktop creation timeout
Window movement timeout
Provider initialization timeout
```

Never wait indefinitely.

---

# 72. CRASH RECOVERY

Persist operation metadata sufficient to determine whether the previous operation ended unexpectedly.

On next manager startup:

```text
Previous workspace operation did not complete.

[Review]
[Run Dry Run]
[Sync Workspace]
[Ignore]
```

Do not automatically continue execution.

---

# 73. SINGLE OPERATION LOG

Every workspace operation receives a unique operation ID.

Example:

```text
Operation:
20261006-143001-AB12
```

Every log entry for that operation should contain the operation ID.

This makes troubleshooting easier.

---

# 74. STRUCTURED LOGGING

Use:

```text
INFO
SUCCESS
WARNING
ERROR
DEBUG
```

Include:

```text
timestamp
level
operation ID
component
action
result
error code where applicable
```

Never log passwords or tokens.

---

# 75. LIVE LOG UI

Provide:

* live log
* clear
* copy
* search
* filter
* export
* open log directory

Filters:

```text
ALL
INFO
SUCCESS
WARNING
ERROR
DEBUG
```

---

# 76. DIAGNOSTIC REPORT

Provide:

```text
Generate Diagnostic Report
```

Include:

* Windows version/build
* architecture
* manager version
* provider version
* capability detection
* desktop count
* desktop IDs where safe
* configured applications
* executable resolution results
* process detection results
* window detection results
* recent errors
* dependency versions

Redact:

* passwords
* tokens
* credentials
* authentication headers
* browser profile data
* secrets inside arguments
* sensitive command-line values

---

# 77. PRIVACY

The application operates locally.

Do not send data externally.

No telemetry by default.

No analytics by default.

No cloud synchronization.

No external process monitoring service.

No remote management.

---

# 78. SECURITY

Treat the configuration file as potentially sensitive.

Do not allow configuration to become an arbitrary command-execution mechanism.

Validate:

* executable path
* arguments
* working directory
* environment variables
* matching rules
* regex patterns
* timeouts
* retry counts
* file paths

Reject unsafe configuration.

---

# 79. REGEX SAFETY

If window-title regex matching is supported:

* validate regex
* catch invalid patterns
* prevent catastrophic/unbounded matching where practical
* provide a timeout or safe regex strategy if the implementation supports it

Invalid regex must not crash the application.

---

# 80. PROCESS EXECUTION SAFETY

Use safe APIs.

Do not use:

* encoded PowerShell
* downloaded scripts
* remote commands
* hidden arbitrary command execution
* shell injection
* arbitrary configuration-as-code

Do not execute:

```text
powershell.exe -EncodedCommand ...
```

Do not dynamically download and execute anything.

---

# 81. ADMINISTRATOR SAFETY

Do NOT automatically elevate.

Normal functionality should run as a standard user.

If an operation requires elevation:

```text
Administrator permission required.

Reason:
<specific reason>

[Cancel]
[Continue]
```

Request elevation only for that operation if genuinely necessary.

Do not run the whole application elevated unnecessarily.

---

# 82. WINDOWS SECURITY

Never:

* disable UAC
* disable Defender
* disable SmartScreen
* modify firewall
* weaken execution policy system-wide
* install services unnecessarily
* modify security policies

---

# 83. INSTALLATION

Provide a development mode and optional packaged mode.

If Python is used, consider a reputable packaging method such as PyInstaller only after the application works correctly.

Packaging must not hide unsafe behavior.

The packaged application must:

* use the same configuration
* use the same safety rules
* preserve logs
* preserve user configuration
* not automatically launch the workspace

---

# 83A. TWO DESKTOP SHORTCUTS — CONFIGURE AND RUN

The finished application must provide **two separate user-facing Desktop shortcuts** for the current Windows user. These shortcuts are a core product requirement, not an optional convenience.

## Shortcut 1 — Configuration GUI

Create a Desktop shortcut named:

```text
Virtual Desktop Workspace Manager — Configure
```

Its only purpose is to open the graphical configuration/management interface.

Launching this shortcut must:

* open the GUI
* load the previously saved configuration
* show the active profile
* allow the user to edit desktops, applications, mappings, launch policies, matching rules, and settings
* allow discovery, diagnostics, validation, import/export, backup, and restore
* save valid configuration changes for future use

Launching the Configure shortcut must **NEVER** by itself:

* launch the workspace
* launch configured applications
* move application windows
* create Virtual Desktops
* switch the user's Virtual Desktop
* synchronize the workspace
* enable startup automation

Even if automation is enabled in settings, `--config` mode remains configuration-only.

## Shortcut 2 — Run Workspace

Create a Desktop shortcut named:

```text
Virtual Desktop Workspace Manager — Run Workspace
```

Its purpose is to explicitly execute the currently selected/saved workspace profile using the persisted configuration.

The shortcut must use a dedicated run entry point, for example:

```text
VirtualDesktopWorkspaceManager.exe --run
```

or the equivalent safe packaged/runtime command for the selected technology.

The run shortcut must:

1. Load the persisted configuration from the normal user configuration directory.
2. Validate the configuration before doing anything.
3. Detect capabilities and current desktop state.
4. Build and display/log the execution plan when the selected UX supports it.
5. Respect the configured confirmation policy.
6. Execute only the active profile/workspace.
7. Apply the same safety, cancellation, verification, timeout, retry, and logging rules as the GUI's Launch Workspace action.
8. Return a meaningful exit code when running in command-line/headless mode.
9. Never install, uninstall, or modify unrelated applications or user data.

Double-clicking the **Run Workspace** shortcut is considered an explicit user request to run the configured workspace. This is different from merely opening the manager/configuration GUI.

If confirmation is enabled, the run entry point must show the configured confirmation before real execution. If confirmation is disabled by the user, that preference must have been explicitly saved in configuration and must still obey all other safety restrictions.

If configuration is missing, malformed, invalid, or has unresolved desktop/application mappings, the Run shortcut must fail safely and must **not** guess, partially execute dangerous actions, or silently fall back to defaults.

## Command-Line Entry-Point Contract

Implement explicit, documented modes. At minimum:

```text
--config       Open configuration GUI only
--run          Run the active workspace/profile
--dry-run      Build/show a dry-run plan only; make no real changes
--diagnostics  Run diagnostics only
--version      Print version
--help         Print supported commands
```

Do not make an unspecified/default invocation ambiguous. The default packaged GUI invocation should behave like configuration mode, not run mode.

The run entry point must never interpret arbitrary command-line text as shell commands. Arguments must be parsed by a structured argument parser.

## Shortcut Creation Rules

The project must support creation of these shortcuts through the packaging/installation process.

Important development-safety rule:

**Google Antigravity must not create the shortcuts on my real Desktop merely while building the project.**

Instead, create the installer/packaging logic and documentation required to create them when the user explicitly installs or sets up the application.

Shortcut creation must:

* target the packaged application/approved launcher
* use stable explicit arguments (`--config` and `--run`)
* use the correct working directory or an application-safe working directory
* use an application icon
* be created for the current user unless elevation is genuinely required
* never create a Windows service
* never create a scheduled task
* never create a Run registry entry merely because shortcuts are installed
* never enable startup automation implicitly

If the application is portable and no installer is used, provide an explicit **Create Desktop Shortcuts** action/script that the user can run manually. Do not execute that setup action automatically during development.

## Shortcut Repair and Ownership

The application/installer must know which shortcuts it owns.

On reinstall/update:

* update only its own shortcuts
* preserve unrelated Desktop shortcuts
* repair broken targets when appropriate
* do not duplicate identical shortcuts

On uninstall, offer to remove only the application's owned shortcuts. Never delete unrelated shortcuts.

## Shortcut Safety Boundary

The two shortcuts must remain semantically separate:

```text
Configure shortcut
    ↓
Configuration/inspection only

Run Workspace shortcut
    ↓
Explicit workspace execution
```

Do not make the Configure shortcut secretly execute the Run behavior.
Do not make the Run shortcut silently open the full configuration editor unless configuration is invalid and user intervention is required.

---

# 84. UNINSTALLATION

Document uninstall.

Uninstall may remove:

* application files
* optional startup entry

But ask whether to preserve:

```text
Workspace configuration
Logs
Backups
Profiles
```

Never silently delete user configuration.

---

# 85. SETTINGS

Provide:

## General

* Start with Windows
* Start minimized
* Minimize to tray
* Confirm before execution
* Automation enabled

## Execution

* launch timeout
* window timeout
* polling interval
* retry count
* launch delay
* concurrency mode

## Safety

* dry-run default
* confirmation requirement
* never kill processes
* never delete desktops

## Logging

* log level
* retention
* diagnostic retention

## Appearance

* System
* Light
* Dark

---

# 85A. PERSISTENT GUI SETTINGS AND SAVE BEHAVIOR

All user-editable settings shown in the GUI must persist between application sessions.

The GUI must not rely on in-memory state as the only source of truth.

At minimum, persist:

* active profile
* workspace desktop definitions
* desktop mappings
* application assignments
* application executable paths
* arguments
* working directories
* launch modes
* window matching rules
* window policies
* timeout/retry settings
* dry-run preference
* confirmation preference
* automation setting
* startup preferences
* tray preferences
* logging preferences
* appearance/theme preference
* polling settings
* other user-configurable manager settings

## Save Model

Provide a clear save state in the GUI:

```text
Saved
Unsaved changes
Saving...
Save failed
```

Use an explicit **Save** action for important configuration changes and, where appropriate, safe debounced auto-save for ordinary settings. The implementation must never silently discard valid user changes when the GUI closes.

If auto-save is used:

* validate before saving
* use atomic writes
* create an appropriate backup before significant changes
* never save partially edited invalid records
* show save failures clearly

When the GUI starts, it must load the latest valid configuration. If the latest file is corrupt:

1. Preserve the corrupt file for diagnostics.
2. Attempt recovery from a known-good backup.
3. Tell the user exactly what happened.
4. Do not execute any workspace operation.
5. Require explicit confirmation before restoring a backup.

## Configuration Location

Use a stable user-level directory such as:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\
```

Do not store mutable configuration beside the executable.

Use a clear separation such as:

```text
config/
settings.json
profiles.json
workspaces.json
applications.json

backups/
logs/
diagnostics/
cache/
state/
```

The exact structure may differ by implementation, but the responsibility of each file must be documented.

## Configuration Reload

Provide a safe **Reload from Disk** action.

If there are unsaved changes, warn the user before discarding them.

Do not reload configuration in the middle of an active workspace operation.

## Configuration Conflict Handling

If configuration changes externally while the GUI is open:

* detect the conflict when practical
* do not silently overwrite newer valid data
* offer Reload, Compare/Review, or Save-As/Backup behavior

## First-Run Persistence

After the user completes first-run configuration and clicks Save/Finish:

* persist all settings
* persist the selected profile
* persist desktop mappings
* persist application assignments
* persist the selected launch policies
* do not execute the workspace

When the user opens the Configure shortcut next time, the same saved configuration must be shown.

---

# 86. ACCESSIBILITY

Support:

* keyboard navigation
* logical tab order
* readable text
* sufficient contrast
* tooltips
* clear focus states
* status text
* scalable UI where possible

Never communicate status using color alone.

Use icons + text.

---

# 87. UI DESIGN

Create a professional Windows utility.

Avoid:

* excessive gradients
* glowing AI interfaces
* excessive rounded cards
* giant empty areas
* unnecessary animations
* flashy dashboards

Prefer:

* Windows-like design
* clear typography
* compact layout
* clear hierarchy
* useful status indicators
* professional spacing
* light/dark/system theme
* predictable navigation

The UI should feel like a real Windows productivity utility.

---

# 88. NO FAKE UI

Every button must either:

1. perform its actual intended operation,

or

2. be clearly labeled as unavailable/not implemented.

Do NOT create buttons that appear functional but do nothing.

Do NOT implement fake success messages.

Do NOT use mock data in the production UI unless explicitly marked as demonstration/test mode.

---

# 89. STATUS SYSTEM

Use explicit statuses:

```text
Ready
Running
Completed
Warning
Error
Unavailable
Not Detected
Disabled
Cancelled
Unknown
```

Do not show "Success" if the underlying operation was not verified.

---

# 90. VERIFICATION

After an operation:

```text
Requested
→ Executed
→ Verified
```

Example:

```text
Requested:
Move Brave → Desktop 1

Executed:
MoveWindowToDesktop succeeded

Verified:
GetWindowDesktopId == Desktop 1

Result:
SUCCESS
```

If verification is unavailable:

```text
WARNING

Move was requested successfully, but the selected API does not provide
reliable post-operation verification.
```

Never falsely report success.

---

# 91. CURRENT DESKTOP

Show:

```text
Current Desktop:
Desktop 2 — Development
```

Refresh when:

* application opens
* user presses Refresh
* desktop changes are detected
* workspace operation begins

Do not aggressively poll if unnecessary.

---

# 92. USER EXPERIENCE WITH DESKTOP SWITCHING

The application should NOT unexpectedly switch the user to another Virtual Desktop merely to perform background operations unless explicitly required and clearly communicated.

Prefer direct APIs that do not require switching.

If switching is unavoidable:

1. Warn the user when appropriate.
2. Preserve the user's original desktop.
3. Perform the required operation.
4. Restore the user's original desktop if safe.
5. Verify restoration when possible.

Never leave the user on an unexpected desktop without explanation.

---

# 93. OPEN DESKTOP

Clicking:

```text
Open Desktop
```

should only switch to that desktop.

It must NOT launch applications.

It must NOT synchronize the workspace.

It must NOT move windows.

---

# 94. APPLICATION "OPEN" BUTTON

Distinguish:

```text
Open Application
```

from:

```text
Launch Workspace
```

If the user manually clicks Open Application:

* explicitly launch that configured application
* do not execute the entire workspace
* do not modify other desktops

---

# 95. WORKSPACE PROTECTION

Before executing:

Show a clear summary:

```text
This operation may:

✓ Create missing Virtual Desktops
✓ Launch configured applications
✓ Move configured application windows

It will NOT:

✗ Delete desktops
✗ Kill processes
✗ Uninstall applications
✗ Delete files
✗ Modify application data
```

---

# 96. CONFIGURATION VALIDATION

Validate before execution:

* schema version
* profile ID
* desktop IDs
* duplicate IDs
* application IDs
* executable paths
* working directories
* arguments
* desktop mappings
* matching rules
* regex
* timeouts
* retry counts
* launch delays
* unsupported capabilities

Show all blocking errors before execution.

---

# 97. ARCHITECTURE

Use clean separation:

```text
UI
 ↓
Application Controller
 ↓
Workspace Engine
 ↓
State Discovery
 ↓
Planner
 ↓
Execution Engine
 ↓
Verification
 ↓
Reporting
```

Infrastructure:

```text
Virtual Desktop Provider
Window Provider
Process Provider
Application Launcher
Application Discovery
Configuration Store
Profile Store
Logging Service
Diagnostics Service
Startup Integration
```

---

# 98. REQUIRED ABSTRACTIONS

Create interfaces/abstractions such as:

```text
IVirtualDesktopProvider
IWindowProvider
IProcessProvider
IApplicationLauncher
IApplicationDiscovery
IConfigurationStore
IWorkspaceRepository
IWorkspacePlanner
IWorkspaceExecutor
IVerificationService
ILogService
IDiagnosticsService
IStartupManager
```

The core business logic must not directly depend on Windows COM calls.

---

# 99. MOCK PROVIDERS

Provide:

```text
MockVirtualDesktopProvider
MockWindowProvider
MockProcessProvider
MockApplicationLauncher
MockConfigurationStore
```

Automated tests must use these.

Tests must never manipulate my real Virtual Desktops.

---

# 100. RECOMMENDED PROJECT STRUCTURE

Use an appropriate structure such as:

```text
VirtualDesktopWorkspaceManager/
│
├── app/
│   ├── main/
│   ├── ui/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── providers/
│   ├── discovery/
│   ├── execution/
│   ├── verification/
│   ├── configuration/
│   ├── profiles/
│   ├── diagnostics/
│   ├── logging/
│   └── security/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── mocks/
│   └── fixtures/
│
├── config/
│
├── docs/
│
├── scripts/
│
├── packaging/
│
├── README.md
├── CHANGELOG.md
├── LICENSE
└── dependency file
```

Adapt the structure to the selected technology.

---

# 101. TESTING

Create tests for:

## Configuration

* valid config
* malformed config
* missing fields
* duplicate IDs
* migration
* backup
* restore
* atomic write
* import
* export

## Application discovery

* valid executable
* missing executable
* multiple installations
* running application
* Start Menu discovery
* SSMS detection
* Postman detection
* Brave detection

## Process handling

* process exists
* process missing
* multiple processes
* process exits during detection
* path mismatch

## Window handling

* visible window
* hidden window
* minimized window
* multiple windows
* child windows
* helper windows
* title matching
* executable matching
* ambiguous match

## Desktop handling

* one desktop
* two desktops
* four desktops
* more than four desktops
* missing desktop
* extra desktop
* desktop identity mismatch
* unsupported capability
* desktop creation failure

## Workspace

* multiple applications per desktop
* duplicate launch prevention
* missing application
* reassignment
* synchronization
* dry-run
* cancellation
* retry
* partial failure
* crash recovery

---

# 102. PROPERTY / INVARIANT TESTS

Test important invariants.

Examples:

```text
Launching workspace twice does not intentionally create duplicates.

Removing an application never uninstalls it.

A failed application does not prevent unrelated applications from being processed.

Dry Run performs no real workspace modification.

Configuration import cannot replace configuration before validation.

Cancellation prevents future operations.

Extra user-created desktops are preserved.
```

---

# 103. ACCEPTANCE TESTS

Before considering the project complete:

### Scenario 1

Existing desktops:

```text
2
```

Required:

```text
4
```

Result:

```text
Only the required additional desktops are created.
```

### Scenario 2

Existing:

```text
4
```

Required:

```text
4
```

Result:

```text
No unnecessary desktops created.
```

### Scenario 3

Existing:

```text
6
```

Required:

```text
4
```

Result:

```text
All 6 remain.
```

### Scenario 4

Brave is already running.

Result:

```text
No unnecessary duplicate launch.
```

### Scenario 5

Postman is missing.

Result:

```text
Warning.
Other applications continue.
```

### Scenario 6

One desktop contains:

```text
Antigravity
VS Code
Git Bash
```

Result:

```text
All three are allowed.
```

### Scenario 7

User changes:

```text
Brave
Desktop 1 → Desktop 4
```

Result:

```text
Configuration persists.
```

### Scenario 8

User adds:

```text
Docker Desktop
```

to Desktop 2.

Result:

```text
Existing applications remain.
Docker Desktop is added.
```

### Scenario 9

Launch Workspace is clicked twice.

Result:

```text
No unnecessary duplicates.
```

### Scenario 10

Manager opens.

Result:

```text
Nothing launches automatically.
```

### Scenario 11

User clicks Launch Workspace.

Result:

```text
Confirmation appears if enabled.
No operation begins before confirmation.
```

### Scenario 12

User clicks Dry Run.

Result:

```text
No real Windows workspace modification occurs.
```

### Scenario 13

User clicks Stop during execution.

Result:

```text
Future actions stop.
Existing applications are not killed.
```

### Scenario 14

Configuration is malformed.

Result:

```text
Execution blocked.
Existing configuration preserved.
Useful error displayed.
```

### Scenario 15

Virtual Desktop API unavailable.

Result:

```text
Application remains usable for configuration/diagnostics.
No fake success.
Clear capability warning.
```

---

# 104. STATIC VALIDATION

Before declaring the project complete, inspect the complete source tree.

Check:

* syntax
* imports
* type errors where applicable
* missing files
* missing references
* broken UI handlers
* configuration schema
* dependency declarations
* unsafe subprocess usage
* unsafe shell execution
* encoded PowerShell
* hidden commands
* arbitrary command execution
* hard-coded personal paths
* accidental administrator elevation
* destructive file operations
* registry modifications
* startup creation
* fake success states
* unhandled exceptions
* race conditions
* cancellation handling
* duplicate execution
* configuration corruption risks

---

# 105. STATIC SECURITY REVIEW

Perform a final source review specifically for:

```text
Command Injection
Path Injection
Arbitrary Command Execution
Unsafe Subprocess
Privilege Escalation
Untrusted Configuration
Secret Leakage
Sensitive Logging
Unexpected Network Access
Startup Persistence
Registry Modification
File Deletion
Process Termination
```

Produce:

`docs/security-review.md`

---

# 106. API COMPATIBILITY DOCUMENTATION

Create:

`docs/windows-api-compatibility.md`

Document:

* Windows APIs used
* COM interfaces used
* third-party libraries
* library versions
* Windows versions tested/supported
* undocumented/internal APIs if any
* risks
* fallback behavior
* limitations
* detection strategy

Do not hide the use of undocumented Windows interfaces.

---

# 107. DEPENDENCY MANAGEMENT

Document:

* package name
* version
* purpose
* license
* source
* maintenance status
* compatibility

Pin versions where appropriate.

Do not blindly install packages from arbitrary URLs.

Use reputable package repositories.

Do not silently install dependencies while merely building the project unless explicitly necessary and safe.

---

# 108. LOG PRIVACY

Never log:

* passwords
* access tokens
* API keys
* cookies
* browser credentials
* authentication headers
* sensitive environment variables

If application arguments may contain secrets, redact them.

Example:

```text
--token=********
```

rather than:

```text
--token=actual-secret
```

---

# 109. USER CONFIGURATION SECURITY

If configuration contains executable paths and arguments, treat it as executable-adjacent data.

Display a warning when importing external workspace configurations:

```text
Imported configuration contains application launch definitions.

Review before execution.
```

Never execute an imported workspace automatically.

---

# 110. IMPORTED WORKSPACE SAFETY

Import must never automatically:

* launch applications
* create desktops
* move windows
* enable startup
* modify system settings

Import only changes configuration after validation and confirmation.

---

# 111. BACKUP AND RECOVERY

Provide:

```text
Backup Configuration
Restore Configuration
```

Restoration must be validated before applying.

Do not restore automatically on startup without user confirmation.

---

# 112. OPERATION HISTORY

Maintain a lightweight history of workspace operations.

Show:

```text
Time
Profile
Operation
Result
Duration
Warnings
Errors
```

Do not store sensitive process data unnecessarily.

Allow clearing operation history.

---

# 113. HEALTH CHECK

Provide:

```text
Run Health Check
```

Check:

```text
✓ Windows supported
✓ Virtual Desktop provider available
✓ Configuration valid
✓ Desktop mappings valid
✓ Applications detected
✓ Permissions sufficient
✓ Configuration writable
✓ Logging writable
```

This must be diagnostic only.

Do not execute workspace operations during Health Check.

---

# 114. OFFLINE-FIRST DESIGN

The manager must work without internet access.

No network should be necessary for:

* desktop management
* application detection
* configuration
* logging
* diagnostics

---

# 115. NO AUTOMATIC UPDATER IN VERSION 1

Do not implement automatic downloading/updating.

If updates are implemented later, they must be separately designed and explicitly approved.

---

# 116. DOCUMENTATION

Create comprehensive documentation:

`README.md`

Include:

1. Purpose
2. Features
3. Supported Windows versions
4. Requirements
5. Architecture
6. Installation
7. First-run setup
8. Configuration
9. Adding applications
10. Removing applications
11. Moving applications
12. Multiple applications per desktop
13. Workspace profiles
14. Dry Run
15. Launch Workspace
16. Sync Workspace
17. Logs
18. Diagnostics
19. Troubleshooting
20. Known Windows limitations
21. API limitations
22. Security
23. Privacy
24. Startup behavior
25. Uninstall
26. Packaging
27. Testing

---

# 117. CHANGELOG

Create:

`CHANGELOG.md`

Document versioned changes.

---

# 118. CONFIGURATION SCHEMA

Create documentation for the complete configuration model.

Include examples for:

* one desktop
* multiple desktops
* multiple apps per desktop
* profiles
* launch settings
* matching rules
* import/export

---

# 119. SAMPLE CONFIGURATION

Provide a safe sample configuration.

The sample configuration must NOT automatically execute during development.

Example:

```json
{
  "schemaVersion": 1,
  "activeProfile": "development",
  "profiles": [
    {
      "id": "development",
      "name": "Development",
      "desktops": [],
      "applications": []
    }
  ]
}
```

---

# 120. NO PERSONAL PATHS

Do not hard-code paths belonging specifically to my machine.

Do not hard-code:

```text
C:\Users\farma\
```

as a required path.

Use:

```text
%USERPROFILE%
%APPDATA%
%LOCALAPPDATA%
```

or dynamically discover paths.

---

# 121. NO UNRELATED FEATURES

Do not add:

* system cleaners
* debloat functionality
* registry cleaners
* startup cleaners
* antivirus controls
* process killers
* RAM cleaners
* disk cleaners
* browser cleaners
* telemetry
* cryptocurrency
* remote control

This is a Virtual Desktop Workspace Manager.

Keep the scope focused.

---

# 122. PERFORMANCE

The manager should be lightweight.

Avoid:

* continuous full process scans
* continuous full filesystem scans
* aggressive polling
* unnecessary CPU usage
* memory leaks
* unbounded log growth

Use event-driven mechanisms where practical.

If polling is required:

* use configurable intervals
* stop polling when not needed
* avoid duplicate polling loops

---

# 123. RESOURCE MANAGEMENT

Ensure:

* subprocess handles are released
* Windows handles are closed
* COM resources are handled correctly
* threads/tasks terminate
* timers are disposed
* log handlers do not multiply
* UI callbacks do not leak

---

# 124. THREADING / UI SAFETY

Long-running operations must not freeze the GUI.

Use an appropriate worker/background execution model.

The UI must remain responsive during:

* application discovery
* launch waiting
* window detection
* desktop operations
* synchronization

All UI updates must occur through the correct UI-thread mechanism.

---

# 125. LOGGING DURING BACKGROUND OPERATIONS

Background operations must report progress:

```text
Preparing desktops... 25%
Launching applications... 50%
Moving windows... 75%
Verifying... 90%
Complete... 100%
```

Never make progress percentages fake.

If exact progress is unavailable:

```text
Working...
```

is preferable to false precision.

---

# 126. FINAL OPERATION REPORT

At the end:

```text
Workspace Operation Complete

Profile:
Development

Virtual Desktops:
4 / 4

Applications:
7 configured
6 detected
4 launched/reused
5 windows assigned
1 skipped

Warnings:
1

Errors:
0

Cancelled:
No

Duration:
8.42 seconds
```

Provide:

```text
[View Details]
[Open Logs]
[Run Diagnostics]
```

---

# 127. USER ACTION AUDIT

Log user-initiated management actions such as:

```text
Application Added
Application Removed
Application Reassigned
Desktop Mapping Changed
Profile Switched
Configuration Imported
Configuration Restored
Startup Enabled
Startup Disabled
Workspace Launch Started
Workspace Launch Cancelled
```

Do not log sensitive information.

---

# 128. APPLICATION REMOVAL SAFETY

Removing a workspace entry must never remove:

* executable
* installation
* process
* application data
* user files

Only configuration changes.

---

# 129. DESKTOP CREATION SAFETY

Before creating a desktop, show it in the execution plan.

During real execution:

```text
Create Desktop
→ Verify
→ Update mapping
```

If creation fails:

```text
Desktop creation failed.

No additional desktop actions will be attempted for this mapping.
```

Do not repeatedly retry indefinitely.

---

# 130. DESKTOP DELETION

Do NOT implement automatic desktop deletion.

If a future version supports manual deletion:

* require explicit user action
* show warning
* explain that applications may be affected
* never delete a desktop during normal workspace synchronization

For Version 1, prefer not implementing desktop deletion at all.

---

# 131. WINDOW MOVE SAFETY

Before moving a window:

Verify:

```text
HWND still exists
PID still exists
Executable still matches
Window still matches configured application
Target desktop still exists
Operation not cancelled
```

If any critical condition changes:

```text
Skip move and re-evaluate.
```

Do not move a reused/stale HWND blindly.

---

# 132. WINDOW HANDLE SAFETY

HWNDs are runtime identifiers.

Never persist HWNDs as permanent application identity.

Use them only for the current runtime operation.

---

# 133. PROCESS ID SAFETY

PIDs can be reused by Windows.

Never trust an old PID without revalidating:

* process exists
* executable path matches
* process identity still matches

---

# 134. APPLICATION EXIT RACE

If an application closes during synchronization:

```text
Application exited before window assignment.

Result:
Skipped safely.
```

Do not immediately relaunch unless configuration explicitly allows recovery and the user has authorized workspace automation.

---

# 135. USER MANUAL INTERVENTION

If the user manually closes an application during a workspace operation:

Do not automatically fight the user.

Record:

```text
Application closed by user during operation.
```

Continue safely.

---

# 136. PAUSE

If practical, provide:

```text
Pause Automation
```

Pause must stop future workspace actions.

It must not kill or modify already-running applications.

---

# 137. PROFILE SWITCHING SAFETY

Switching profiles must NOT automatically launch the new profile.

Example:

```text
Profile changed:
Development → Work

No applications were launched.

[Launch Work Workspace]
```

---

# 138. CONFIGURATION CHANGE DURING EXECUTION

Do not allow unsafe configuration mutations while an operation is running.

Options:

```text
Disable editing during execution
```

or:

```text
Queue configuration change for next operation
```

Do not let the executor operate on partially edited configuration.

---

# 139. VERSIONING

Display:

```text
Virtual Desktop Workspace Manager v1.0.0
```

Use semantic versioning where appropriate.

---

# 140. ABOUT PAGE

Show:

* application version
* build
* Python/runtime version if relevant
* dependency versions
* license
* project information
* API provider
* diagnostics shortcut

---

# 141. TEST ENVIRONMENT

Do not require real application launches for unit tests.

Create fixtures for:

```text
Brave
Antigravity
SSMS
Postman
VS Code
Docker
```

These should be simulated.

---

# 142. MOCK EXECUTION EXAMPLE

Example mock state:

```text
Desktop 1
Desktop 2
Desktop 3

Brave → Desktop 3
Antigravity → Desktop 2
SSMS → Desktop 1
Postman → not running
```

Desired:

```text
Brave → Desktop 1
Antigravity → Desktop 2
SSMS → Desktop 3
Postman → Desktop 4
```

The planner should produce:

```text
Create Desktop 4

Move Brave
No action for Antigravity
Move SSMS
Launch Postman
Move Postman
Verify
```

No real Windows operation should occur.

---

# 143. FINAL SAFETY REVIEW TABLE

Create:

`docs/safety-review.md`

At minimum:

| Risk                        | Mitigation                            |
| --------------------------- | ------------------------------------- |
| Duplicate applications      | Process/window detection              |
| Duplicate desktops          | Desktop enumeration + stable identity |
| Wrong window                | HWND/PID/executable verification      |
| Stale HWND                  | Revalidation                          |
| PID reuse                   | Process-path verification             |
| Missing application         | Discovery + graceful skip             |
| API failure                 | Capability detection + bounded retry  |
| API incompatibility         | Version/capability detection          |
| Configuration corruption    | Validation + atomic writes + backups  |
| Unsafe import               | Validation + preview + confirmation   |
| Unexpected execution        | Explicit action                       |
| Startup persistence         | Explicit opt-in                       |
| Privilege escalation        | No automatic elevation                |
| Data loss                   | No deletion                           |
| User desktop deletion       | Never automatic                       |
| Process termination         | Prohibited                            |
| Secret leakage              | Log redaction                         |
| Arbitrary command execution | Safe subprocess API                   |
| Race condition              | State revalidation                    |
| Duplicate operations        | Single-operation lock                 |
| Manager duplication         | Single-instance guard                 |
| UI freezing                 | Background execution                  |
| Cancellation failure        | Cooperative cancellation              |
| False success               | Verification                          |
| API limitation              | Explicit warning                      |
| User intervention conflict  | State-aware synchronization           |

---

# 144. DEVELOPMENT WORKFLOW FOR GOOGLE ANTIGRAVITY

Follow these phases.

## PHASE 1 — ANALYZE

Before implementation, inspect:

* requirements
* Windows API options
* available libraries
* compatibility
* risks
* packaging
* application discovery
* window matching
* desktop identity

Create:

`docs/requirements-analysis.md`

---

## PHASE 2 — TECHNOLOGY DECISION

Create:

`docs/technology-decision.md`

Explain the selected stack.

---

## PHASE 3 — ARCHITECTURE

Create:

`docs/architecture.md`

Include:

```text
UI
 ↓
Application Controller
 ↓
Workspace Engine
 ↓
State Discovery
 ↓
Planner
 ↓
Executor
 ↓
Verification
 ↓
Reporting
```

---

## PHASE 4 — DATA MODEL

Create:

`docs/configuration-schema.md`

Define:

* workspace
* profile
* desktop
* application
* matching rule
* execution settings
* safety settings
* schema version

---

## PHASE 5 — SAFETY REVIEW

Create:

`docs/safety-review.md`

Identify risks before implementation.

---

## PHASE 6 — IMPLEMENTATION

Build the complete application.

Do not stop after creating the UI.

Do not create fake controls.

Connect every intended feature to real logic.

---

## PHASE 7 — STATIC VALIDATION

Review:

* syntax
* imports
* references
* types
* configuration
* dependencies
* unsafe process execution
* unsafe filesystem access
* elevation
* startup
* logging
* exception handling
* cancellation
* concurrency

---

## PHASE 8 — SAFE TESTING

Run only:

* unit tests
* mock tests
* configuration tests
* static validation
* isolated tests

Do NOT manipulate the real Windows Virtual Desktop environment.

---

## PHASE 9 — FINAL REVIEW

Perform a production-readiness review.

Check every requirement in this prompt.

Create:

`docs/final-review.md`

Mark each requirement:

```text
PASS
PARTIAL
NOT IMPLEMENTED
UNSUPPORTED
```

Do not mark something PASS merely because the UI exists.

---

# 145. REQUIREMENT TRACEABILITY

Create:

`docs/requirements-traceability.md`

Map requirements to:

```text
Requirement
Implementation
Source File
Test
Status
```

Example:

```text
REQ-VD-001
Detect Virtual Desktops
providers/virtual_desktop.py
tests/test_virtual_desktop.py
PASS
```

This prevents requirements from silently being forgotten.

---

# 146. NO HIDDEN TODOs

Before completion, search the project for:

```text
TODO
FIXME
pass
NotImplemented
stub
mock success
fake
placeholder
coming soon
```

Any remaining item must be explicitly documented.

Do not declare production-ready while critical functionality is stubbed.

---

# 147. NO FAKE SUCCESS

Never write:

```text
SUCCESS
```

unless the underlying operation actually succeeded.

Never write:

```text
Desktop created
```

if creation was only requested but not verified when verification is available.

Use:

```text
REQUESTED
```

or:

```text
UNVERIFIED
```

where appropriate.

---

# 148. FINAL ACCEPTANCE CHECKLIST

Before completion verify:

* [ ] Application builds
* [ ] UI is complete
* [ ] Configuration persists
* [ ] Multiple applications per desktop work
* [ ] Applications can be added without code changes
* [ ] Applications can be reassigned
* [ ] Applications can be removed without uninstalling
* [ ] Profiles work
* [ ] Import/export works
* [ ] Dry Run works
* [ ] Launch Workspace works architecturally
* [ ] Sync Workspace works architecturally
* [ ] Duplicate prevention exists
* [ ] Desktop identity is handled safely
* [ ] Window matching is robust
* [ ] Cancellation exists
* [ ] Single-instance protection exists
* [ ] Concurrency is controlled
* [ ] Logs work
* [ ] Diagnostics work
* [ ] Configuration backups work
* [ ] Validation works
* [ ] API capabilities are detected
* [ ] Windows limitations are documented
* [ ] No automatic elevation
* [ ] No destructive operations
* [ ] No automatic startup unless explicitly enabled
* [ ] No telemetry
* [ ] No network dependency
* [ ] Security review completed
* [ ] Tests completed
* [ ] Static review completed
* [ ] Documentation completed
* [ ] Application has NOT been launched
* [ ] Configure Desktop shortcut is defined
* [ ] Run Workspace Desktop shortcut is defined
* [ ] Configure shortcut never executes the workspace
* [ ] Run shortcut uses the persisted active configuration
* [ ] `--config` entry point exists
* [ ] `--run` entry point exists
* [ ] GUI settings persist across restarts
* [ ] Unsaved-change handling exists
* [ ] Shortcut creation is installer/setup driven, not silently performed during development
* [ ] Shortcut repair does not duplicate shortcuts
* [ ] Uninstall removes only application-owned shortcuts
* [ ] Shortcut acceptance tests are implemented


# 148A. DESKTOP SHORTCUT ACCEPTANCE TESTS

The following tests are mandatory:

### Shortcut Test 1 — Configure

Double-clicking the Configure shortcut must:

```text
Open GUI
Load saved settings
Perform no workspace execution
```

### Shortcut Test 2 — Run

Double-clicking the Run Workspace shortcut must:

```text
Load saved settings
Validate configuration
Respect confirmation policy
Execute the active workspace only when authorized
```

### Shortcut Test 3 — Persistence

Change:

```text
Brave → Desktop 4
```

Save configuration, close the GUI, reopen Configure, and verify:

```text
Brave → Desktop 4
```

remains configured.

### Shortcut Test 4 — Configure Does Not Run

Even when a workspace is configured to launch applications, opening Configure must not launch any application.

### Shortcut Test 5 — Missing Configuration

Run Workspace with no valid configuration must stop safely with a clear message and must not launch applications or alter desktops.

### Shortcut Test 6 — Broken Shortcut

The installer/repair mechanism must be able to identify and repair an application-owned shortcut whose target no longer exists.

### Shortcut Test 7 — No Duplicate Shortcuts

Repeated setup/repair must not create multiple copies of the same application-owned shortcut.

### Shortcut Test 8 — Uninstall Safety

Uninstall removes only application-owned shortcuts and leaves unrelated Desktop shortcuts untouched.

---

# 149. REQUIRED DELIVERABLES

Provide:

## Application

Complete production-oriented source code.

## UI

Complete functional GUI.

## Configuration

Default workspace configuration.

## Tests

Unit and mock integration tests.

## Documentation

* README.md
* architecture.md
* requirements-analysis.md
* technology-decision.md
* configuration-schema.md
* windows-api-compatibility.md
* safety-review.md
* security-review.md
* troubleshooting.md
* final-review.md
* requirements-traceability.md

## Dependency Information

Dependency file with versions.

## Packaging

Instructions for creating a Windows executable/package.

The packaging deliverables must also include:

* Configure entry point
* Run Workspace entry point
* `--config` / `--run` command-line behavior
* Desktop shortcut creation for both entry points
* shortcut icons
* shortcut ownership/repair behavior
* uninstall behavior for owned shortcuts
* portable-mode shortcut setup instructions if supported
* explicit confirmation that packaging does not enable startup automation

## Diagnostics

Diagnostic-report functionality.

## Logs

Structured logging.

---

# 150. FINAL OUTPUT TO ME

After completing the project, report:

1. Project structure
2. Files created
3. Technology selected
4. Why it was selected
5. Dependencies
6. API/library versions
7. Windows compatibility
8. Implemented features
9. Tests created
10. Tests executed
11. Static validation results
12. Security review results
13. Known limitations
14. Unsupported Windows features
15. Packaging instructions
16. Manual run instructions
17. Configuration location
18. Log location
19. Diagnostic instructions
20. Remaining issues, if any

Do NOT claim the application was tested interactively if it was not launched.

Clearly distinguish:

```text
Static Validation
Mock Testing
Real Windows Testing
```

---

# 151. MOST IMPORTANT RULES

These rules override convenience.

1. **NEVER run the generated application during development unless I explicitly authorize it.**
2. **NEVER launch my configured applications during development.**
3. **NEVER create or modify my real Virtual Desktop workspace during development.**
4. **NEVER automatically delete Virtual Desktops.**
5. **NEVER automatically kill application processes.**
6. **NEVER uninstall applications.**
7. **NEVER delete user files.**
8. **NEVER modify development data.**
9. **NEVER silently elevate to Administrator.**
10. **NEVER silently create startup automation.**
11. **NEVER silently modify Windows security settings.**
12. **NEVER claim an operation succeeded without appropriate verification.**
13. **NEVER rely entirely on keyboard simulation when a reliable API is available.**
14. **NEVER assume a process is equivalent to a window.**
15. **NEVER trust stale HWNDs or PIDs without revalidation.**
16. **NEVER hard-code application paths as the only discovery mechanism.**
17. **NEVER limit a desktop to one application.**
18. **NEVER require source-code changes to add applications.**
19. **NEVER overwrite configuration without validation and safe persistence.**
20. **NEVER import and automatically execute a workspace.**
21. **NEVER launch the workspace merely because the manager starts.**
22. **NEVER create duplicate manager instances unnecessarily.**
23. **NEVER allow concurrent workspace executions.**
24. **NEVER allow one failed application to unnecessarily destroy the whole operation.**
25. **NEVER use unsafe arbitrary shell commands.**
26. **NEVER add telemetry without explicit approval.**
27. **NEVER add an automatic updater in Version 1.**
28. **NEVER hide unsupported API functionality.**
29. **NEVER create fake UI functionality.**
30. **NEVER sacrifice safety for automation.**
31. **NEVER sacrifice reliability for visual effects.**
32. **NEVER treat Windows desktop positions as permanently stable identities.**
33. **NEVER automatically switch the user's desktop unless required and explicitly handled.**
34. **NEVER fight the user indefinitely when they manually change application state.**
35. **NEVER run the finished application until I explicitly tell you to run it.**

---

# 151A. ENTRY-POINT AND PERSISTENCE RULES

These rules are mandatory:

1. The **Configure** shortcut is configuration-only.
2. The **Run Workspace** shortcut is the explicit execution entry point.
3. The Configure shortcut must never launch configured applications.
4. The Configure shortcut must never create/move/delete/switch real desktops as a side effect of opening the GUI.
5. The Run Workspace shortcut must load the saved configuration rather than using a separate hidden configuration file.
6. GUI changes must persist and be available to the Run Workspace shortcut.
7. The Run Workspace shortcut must never use hard-coded workspace assignments that bypass saved configuration.
8. A missing or invalid configuration must block real execution.
9. Desktop shortcut creation must be performed by explicit setup/installation, not automatically by Google Antigravity during development.
10. Re-running setup must not duplicate application-owned shortcuts.
11. Shortcut repair must not modify unrelated shortcuts.
12. The two shortcuts must have clearly different names, icons, and command-line modes.
13. The default application launch mode must be configuration-only unless the user explicitly invokes `--run` or the GUI's equivalent Run Workspace action.
14. Configuration persistence must use the same validated user-level configuration source for GUI, Run shortcut, Dry Run, diagnostics, and other entry points.
15. No entry point may silently enable startup automation.

---

# 152. FINAL INSTRUCTION TO GOOGLE ANTIGRAVITY

Start by analyzing this entire specification.

Pay special attention to the required **two Desktop shortcuts** and the persistent configuration model:

```text
Desktop shortcut 1 → Virtual Desktop Workspace Manager — Configure
Desktop shortcut 2 → Virtual Desktop Workspace Manager — Run Workspace
```

The Configure shortcut must open the GUI only.
The Run Workspace shortcut must execute the saved active workspace according to the safety and confirmation rules.
All settings changed in the GUI must persist and be reused by the Run Workspace shortcut.
Create the installer/packaging logic for these shortcuts, but do not create or click the real shortcuts on my Desktop during development.


Do not immediately execute the application.

First create the design and architecture documentation.

Then implement the application.

Then perform static validation and safe mocked tests.

Do not launch the application.

Do not manipulate my real Windows Virtual Desktops.

Do not launch Brave.

Do not launch Google Antigravity.

Do not launch SSMS.

Do not launch Postman.

Do not launch Docker.

Do not launch Visual Studio.

Do not launch VS Code.

Do not create startup automation.

Do not modify my Windows workspace.

Do not perform real workspace execution.

Every functional UI control must connect to real application logic.

Every unsupported feature must be clearly identified.

Every important Windows API limitation must be documented.

Every safety-sensitive action must require the appropriate explicit user authorization.

When implementation and safe validation are complete, stop.

Report the project status.

Then wait.

**DO NOT RUN THE APPLICATION.**

**DO NOT RUN THE WORKSPACE.**

**WAIT FOR MY EXPLICIT INSTRUCTION BEFORE EXECUTING ANY REAL WORKSPACE OPERATION.**
