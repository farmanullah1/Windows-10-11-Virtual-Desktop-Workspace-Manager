# VIRTUAL DESKTOP WORKSPACE MANAGER — PRODUCTION-READY GOOGLE ANTIGRAVITY MASTER PROMPT
## Fully Updated Product, Architecture, Safety, UX, Setup, Testing, and Delivery Specification

> **Revision:** 2.0  
> **Target:** Windows 10/11, primarily 64-bit  
> **Intended use:** Daily-use local desktop productivity utility  
> **Implementation environment:** Google Antigravity  
> **Execution policy:** Build and validate safely; do not run the generated application unless explicitly authorized  
> **Source baseline:** This revision incorporates the original specification and adds the higher-priority product, UX, accessibility, architecture, observability, recovery, setup, and acceptance requirements below.

---

# 0. MASTER INSTRUCTION — READ THIS FIRST

Act as a **senior Windows desktop software engineer, Windows API/COM engineer, software architect, security engineer, QA engineer, reliability engineer, technical writer, and senior UX/product designer**.

Build a **production-oriented Windows 10/11 Virtual Desktop Workspace Manager** intended for real daily use.

This document is a **complete product specification**, not a request for a prototype or a visual mockup.

The application must be:

- reliable;
- safe;
- predictable;
- maintainable;
- testable;
- accessible;
- visually clear;
- responsive;
- configuration-driven;
- offline-first;
- conservative with Windows state;
- explicit about unsupported capabilities;
- resistant to race conditions and stale Windows handles;
- idempotent;
- recoverable after partial failure;
- usable by a non-expert without requiring source-code edits.

## 0.1 Source-of-truth and precedence rule

The detailed requirements contained later in this document remain mandatory.

This revision adds **higher-priority clarification requirements** where the original specification was repetitive, ambiguous, or left product/UX behavior underspecified.

When two requirements appear to conflict, use this precedence order:

1. **Safety and explicit user authorization**
2. **Do-not-run-during-development rule**
3. **Do-not-destroy/modify unrelated Windows state**
4. **Correctness and verified state**
5. **Persistent configuration integrity**
6. **User control and accessibility**
7. **Reliability and recovery**
8. **Maintainability/testability**
9. **Performance**
10. **Visual polish**

Never sacrifice a higher-priority rule to satisfy a lower-priority one.

## 0.2 Absolute development execution boundary

Google Antigravity must **create the product, not operate the user's real Windows environment**.

During development:

- create source code;
- create documentation;
- create tests;
- create mock/fake providers;
- perform static analysis;
- perform syntax/type/lint validation;
- inspect generated files;
- run only isolated tests that cannot manipulate the real Windows workspace.

Do **not**:

- launch the generated GUI;
- execute the generated workspace;
- execute `setup.py`;
- create the real Desktop shortcuts;
- launch configured applications;
- create/delete/switch/move real Virtual Desktops;
- move real application windows;
- create startup persistence;
- create scheduled tasks;
- install services;
- modify unrelated Windows settings;
- modify user files or development data.

The words **build**, **finish**, **test**, **validate**, or **complete** are not authorization to run the product.

Only an explicit future instruction such as **"Run the application"**, **"Run setup"**, or **"Run the workspace"** authorizes the corresponding real-world action.

---

# 1. OBJECTIVE

Create a Windows desktop utility that lets users define persistent **workspace profiles** consisting of:

- named workspace desktops;
- mappings to real Windows Virtual Desktops;
- one or more applications per workspace desktop;
- application launch policies;
- process/window matching rules;
- execution and verification policies;
- saved configuration;
- diagnostics and operation history.

The product must let the user:

1. inspect the current Windows Virtual Desktop environment;
2. configure workspace layouts;
3. add applications without source-code changes;
4. assign multiple applications to one desktop;
5. reassign applications between desktops;
6. save those changes permanently;
7. preview what would happen;
8. explicitly launch a workspace;
9. synchronize desired state with actual state;
10. monitor progress;
11. cancel future work safely;
12. diagnose failures;
13. recover configuration safely;
14. import/export profiles;
15. maintain multiple workspace profiles;
16. use the manager without Administrator privileges whenever possible.

The product must **not** become a general Windows cleaner, debloater, process killer, registry editor, remote-control tool, or system optimizer.

---

# 2. TARGET AUDIENCE

Primary audience:

- Windows 10/11 developers;
- power users;
- technical professionals;
- users who work with multiple applications across Virtual Desktops;
- users who want repeatable workspaces without manually arranging applications every time.

The interface must still be understandable to a technically competent Windows user who does not know Windows COM APIs, HWNDs, PIDs, GUIDs, or internal Virtual Desktop implementation details.

Technical complexity belongs in:

- Advanced Settings;
- Diagnostics;
- Logs;
- API compatibility documentation.

Do not expose implementation complexity unnecessarily in the main workflow.

---

# 3. PRODUCT TONE AND DESIGN LANGUAGE

The product should feel like a **serious Windows productivity utility**, not an AI dashboard.

Use:

- calm visual hierarchy;
- compact but breathable layouts;
- clear labels;
- familiar Windows interaction patterns;
- consistent icons;
- predictable buttons;
- meaningful status text;
- restrained motion;
- strong focus states;
- accessible contrast;
- obvious primary actions.

Avoid:

- excessive gradients;
- neon/glowing effects;
- oversized cards;
- excessive rounded containers;
- decorative animations;
- fake metrics;
- unnecessary charts;
- dense technical jargon;
- ambiguous icon-only controls;
- giant empty dashboard areas.

The UI must prioritize **clarity over visual novelty**.

---

# 4. SCOPE

## 4.1 In scope

- Virtual Desktop capability detection;
- Virtual Desktop discovery/mapping where supported;
- workspace configuration;
- profiles;
- application discovery;
- process/window detection;
- safe application launch;
- window movement;
- desired/actual state comparison;
- dry run;
- execution planning;
- verification;
- cancellation;
- diagnostics;
- structured logs;
- operation history;
- configuration backup/restore;
- import/export;
- setup/bootstrap;
- Desktop shortcuts;
- optional startup integration;
- accessibility;
- light/dark/system appearance;
- packaging documentation;
- unit/mock/integration tests.

## 4.2 Explicitly out of scope for Version 1

Do not add:

- system cleaning;
- debloating;
- RAM cleaners;
- registry cleaners;
- process killing;
- application uninstallers;
- browser cleanup;
- antivirus controls;
- firewall modification;
- remote management;
- cloud synchronization;
- telemetry;
- cryptocurrency;
- automatic online updater;
- arbitrary script execution;
- remote commands;
- generic task automation;
- hidden persistence mechanisms.

---

# 5. UX PRINCIPLES — NEW HIGH-PRIORITY REQUIREMENTS

The application must be designed around the following principles.

## 5.1 Progressive disclosure

Show simple information first.

Example:

```text
Development
4 applications
3 running
1 missing
Ready
```

Allow the user to open deeper details when needed:

```text
View Details
→
Executable path
PID
HWND
Desktop GUID
matching confidence
provider information
```

Do not expose all technical metadata in every card.

## 5.2 One clear primary action per context

Examples:

Dashboard:

```text
Launch Workspace
```

Workspace editor:

```text
Save Changes
```

Execution:

```text
Run
```

Diagnostics:

```text
Run Health Check
```

Do not present ten equally prominent buttons.

## 5.3 Safe destructive/disruptive actions

Every action capable of changing Windows state must communicate:

- what will happen;
- what will not happen;
- whether it is reversible;
- whether confirmation is required;
- what happens if it fails.

## 5.4 Never use color alone

A warning must not be represented only by yellow.

Use:

```text
⚠ Warning
```

A success must include text:

```text
✓ Verified
```

An error must include text:

```text
✕ Error
```

Provide accessible labels/tooltips where icons are used.

---

# 6. INFORMATION ARCHITECTURE

Use a clear primary navigation model.

Recommended:

```text
Dashboard
Workspaces
Applications
Virtual Desktops
Execution
History
Logs
Diagnostics
Settings
About
```

Do not make every page equally prominent.

## 6.1 Global header

The header should show:

- application name;
- active profile;
- current Windows desktop;
- overall health/status;
- refresh action;
- settings access.

## 6.2 Global execution area

When an operation is running, the UI should expose a persistent operation status area containing:

```text
Operation: Sync Workspace
Profile: Development
Status: Running
Progress: Working...
[Stop]
```

The user must never have to guess whether the application is still working.

---

# 7. DASHBOARD — IMPROVED

The dashboard should answer four questions immediately:

1. What workspace/profile am I using?
2. What is the current Windows desktop?
3. Is the workspace healthy?
4. What can I do next?

Recommended structure:

```text
┌──────────────────────────────────────────────────────────┐
│ Virtual Desktop Workspace Manager                        │
│ Profile: Development                 Current: Desktop 2  │
├──────────────────────────────────────────────────────────┤
│ Workspace Status                                         │
│ ✓ Ready                                                  │
│                                                          │
│ 4 Desktops     7 Apps     5 Running     1 Warning       │
├──────────────────────────────────────────────────────────┤
│ Quick Actions                                            │
│ [Launch Workspace] [Sync] [Dry Run] [Refresh]            │
├──────────────────────────────────────────────────────────┤
│ Workspace Overview                                       │
│                                                          │
│ Browser        ✓ 1 app                                   │
│ Development    ✓ 3 apps                                  │
│ Database       ⚠ 1 app missing                           │
│ API            ✓ 2 apps                                  │
├──────────────────────────────────────────────────────────┤
│ Recent Activity                                          │
│ Last sync • 2 minutes ago • Completed with 1 warning     │
└──────────────────────────────────────────────────────────┘
```

The dashboard must remain useful even when:

- no workspace exists;
- no desktops are detected;
- no applications are configured;
- the provider is unavailable;
- configuration is invalid.

---

# 8. EMPTY STATES

Every major screen needs a deliberate empty state.

## 8.1 No workspace

```text
No workspace configured yet.

Create a workspace to organize applications across
Windows Virtual Desktops.

[Create Workspace]
[Import Workspace]
```

## 8.2 No applications

```text
No applications assigned.

Add an application by browsing for an executable,
selecting a running application, or using discovery.

[Add Application]
```

## 8.3 No desktops

```text
No Virtual Desktop mapping is available.

[Refresh]
[Run Diagnostics]
[Configure Mapping]
```

## 8.4 No history

```text
No workspace operations have been recorded yet.
```

Do not display fake sample activity in production mode.

---

# 9. LOADING STATES

Never freeze the UI without explanation.

Use meaningful loading states:

```text
Detecting Virtual Desktops…
Scanning running applications…
Resolving executable…
Building execution plan…
Verifying window placement…
```

For operations with unknown duration:

```text
Working…
```

Do not invent percentages.

If real progress can be measured, show it.

---

# 10. ERROR UX

Errors must answer:

1. What happened?
2. Why did it happen?
3. What did the manager avoid doing?
4. What can the user do next?

Bad:

```text
COM error 0x80004005
```

Better:

```text
Could not move the selected window.

The window was detected, but Windows did not confirm
the requested Virtual Desktop assignment.

No process was terminated and no files were modified.

[Retry]
[View Details]
[Run Diagnostics]
```

Technical error information remains available in Logs/Details.

---

# 11. SUCCESS UX

Do not merely show:

```text
Success
```

Show verified outcome:

```text
Workspace synchronized

✓ 6 applications verified
✓ 5 windows assigned
⚠ 1 application unavailable

[View Details]
```

A requested-but-unverified operation must say:

```text
Completed — verification unavailable
```

not:

```text
Verified
```

---

# 12. CONFIRMATION UX

Use confirmations selectively.

Do not ask for confirmation for harmless actions such as:

- opening Settings;
- refreshing detection;
- viewing logs;
- switching tabs;
- saving ordinary configuration changes.

Confirmation is appropriate for:

- executing a workspace;
- importing a workspace containing launch definitions;
- restoring configuration;
- changing startup automation;
- moving a running window immediately because of a configuration change;
- actions with significant Windows-state impact.

Confirmation dialogs must state the scope.

Example:

```text
Run Development Workspace?

This may:
• create missing Virtual Desktops if supported;
• launch configured applications;
• move matched application windows.

This will not:
• kill applications;
• uninstall software;
• delete files;
• delete user-created desktops.

[Cancel] [Review Plan]
```

---

# 13. EXECUTION PLAN UX — IMPROVED

Before real execution, show a reviewable plan.

Group actions:

```text
DESKTOPS
+ Create Desktop

APPLICATIONS
✓ Reuse Brave
→ Move Brave → Browser
→ Launch Postman
→ Move Postman → API

WARNINGS
⚠ SSMS executable could not be resolved
```

Each planned action should expose details on demand.

Provide:

```text
[Back]
[Cancel]
[Run]
```

Do not make the Run button available while blocking validation errors exist.

---

# 14. LIVE EXECUTION UX

While running, show a chronological task list:

```text
✓ Configuration validated
✓ Virtual Desktop mapping refreshed
✓ Brave detected
✓ Brave window verified
→ Launching Postman…
○ Waiting for Postman window
○ Moving Postman
○ Verifying
```

Allow the user to expand an item for technical details.

Provide:

- Stop;
- Pause if implemented;
- View Logs;
- operation ID.

Do not allow conflicting workspace operations during execution.

---

# 15. WORKSPACE EDITOR — IMPROVED

The workspace editor should make the relationship between desktops and applications obvious.

Preferred model:

```text
WORKSPACE: Development

┌───────────────────────────────────────────┐
│ Browser                                   │
│ Windows Desktop: 1                        │
│                                           │
│  • Brave                                  │
│                                           │
│ [+ Add Application] [Edit]                │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ Development                               │
│ Windows Desktop: 2                        │
│                                           │
│  • Google Antigravity                     │
│  • VS Code                                │
│  • Git Bash                               │
│                                           │
│ [+ Add Application] [Edit]                │
└───────────────────────────────────────────┘
```

Support:

- add desktop;
- rename workspace label;
- map desktop;
- reorder display order;
- add multiple applications;
- drag-and-drop assignment;
- edit application;
- disable application;
- remove configuration;
- duplicate a workspace profile;
- import/export.

---

# 16. APPLICATION DETAILS DRAWER

Use a side panel/drawer or dedicated editor for detailed application configuration.

Show simple information first:

```text
Brave Browser
✓ Detected
Desktop: Browser
Launch mode: Reuse existing
Windows: 2
```

Advanced sections:

```text
Executable
Arguments
Working Directory
Discovery
Matching
Window Policy
Timeouts
Retries
Environment
Diagnostics
```

Use collapsible sections to avoid overwhelming the user.

---

# 17. APPLICATION DISCOVERY UX

The Add Application workflow should guide the user.

Recommended dialog:

```text
Add Application

How would you like to add it?

[Browse for EXE]
[Choose Running Application]
[Discover Installed Applications]
[Use Template]
```

After discovery:

```text
Brave Browser

Detected:
✓ Executable
✓ Installation
✓ Running process
✓ 2 windows

Choose installation:
○ C:\...
○ C:\...

[Add Application]
```

If ambiguous:

```text
Multiple installations found.

Please choose the installation to manage.
```

Never silently select a questionable executable.

---

# 18. DESKTOP MAPPING UX

Provide a dedicated mapping screen.

```text
Workspace Desktop       Windows Desktop
------------------------------------------------
Browser                 Desktop 1 ✓
Development             Desktop 2 ✓
Database                Desktop 4 ✓
API                     Desktop 5 ⚠
```

For each mapping show:

- identity confidence;
- current existence;
- current desktop indicator;
- stale/unknown state;
- last verified time.

When identity cannot be safely determined:

```text
Mapping requires review.

Windows reported a different desktop identity.
The manager will not guess.

[Review]
```

---

# 19. ACCESSIBILITY — EXPANDED

The product must support:

- keyboard-only operation;
- logical tab order;
- visible keyboard focus;
- accessible names for controls;
- accessible descriptions for complex controls;
- screen-reader-friendly status text where supported by the UI framework;
- scalable text/layout where practical;
- sufficient contrast;
- non-color status communication;
- tooltips for unfamiliar icons;
- keyboard shortcuts for frequent operations;
- dialogs that do not trap focus incorrectly.

Recommended keyboard shortcuts:

```text
Ctrl+S       Save
Ctrl+R       Refresh
Ctrl+F       Search
Ctrl+L       View Logs
Ctrl+,       Settings
F5            Refresh
Esc           Close/cancel current dialog
```

Only implement shortcuts that do not conflict with native Windows behavior.

---

# 20. RESPONSIVE DESKTOP LAYOUT

Although this is a Windows desktop application, support:

- window resizing;
- smaller laptop resolutions;
- 100%/125%/150% Windows scaling;
- long application names;
- long executable paths;
- large numbers of applications;
- large numbers of workspace desktops.

Do not rely on fixed pixel widths for critical controls.

When space becomes limited:

- collapse secondary information;
- use scrollable regions;
- preserve primary actions;
- avoid clipped text;
- avoid overlapping controls.

---

# 21. SEARCH, FILTERING, AND SORTING

Where lists become non-trivial, provide:

- search;
- filtering;
- sorting;
- clear filter;
- result count.

Applications should be searchable by:

- name;
- executable;
- desktop;
- status.

Logs should be searchable by:

- operation ID;
- level;
- component;
- time;
- text.

History should be filterable by:

- profile;
- operation;
- result;
- date range.

---

# 22. NOTIFICATION SYSTEM

Use a consistent notification/toast system for non-blocking events.

Examples:

```text
Saved
Workspace configuration saved.

Warning
Postman was not detected.

Completed
Workspace synchronized with 1 warning.
```

Do not use notifications for critical errors that require user action.

Provide a persistent error/warning area for unresolved issues.

---

# 23. UNSAVED-CHANGE PROTECTION

If the user has unsaved changes and attempts to:

- close the window;
- switch workspace;
- switch profile;
- reload from disk;
- import another configuration;
- restore a backup;

show:

```text
You have unsaved changes.

[Save Changes]
[Discard Changes]
[Cancel]
```

Never silently discard user configuration edits.

---

# 24. CONFIGURATION DIFF / REVIEW

For important configuration operations, provide a review screen.

Example:

```text
Configuration Changes

+ Add Postman
~ Move Brave: Desktop 1 → Desktop 4
~ Launch mode: Reuse → Ask
- Remove Old Test App
```

This is especially useful for:

- imports;
- restores;
- migrations;
- bulk edits.

---

# 25. PROFILE UX

Profile switching must be visibly separated from execution.

Example:

```text
Active Profile
Development

[Switch Profile]
```

After switching:

```text
Profile changed

Development → Work

No applications were launched.
No windows were moved.

[View Work Profile]
[Launch Work Workspace]
```

Never make profile switching implicitly execute a workspace.

---

# 26. HEALTH INDICATOR

Provide a simple overall health state:

```text
✓ Healthy
⚠ Needs Attention
✕ Blocked
```

Calculate it from real conditions such as:

- provider availability;
- configuration validity;
- unresolved mappings;
- missing required applications;
- writable configuration;
- logging health.

Do not use arbitrary scores unless they provide real value.

---

# 27. DIAGNOSTICS UX

The Diagnostics page should be organized into categories:

```text
System
Virtual Desktops
Provider
Configuration
Applications
Windows
Permissions
Storage
Dependencies
Recent Errors
```

Each category should show:

```text
✓ Passed
⚠ Warning
✕ Failed
— Not Tested
```

Provide:

```text
[Run Health Check]
[Generate Diagnostic Report]
[Copy Summary]
[Open Logs]
```

Health Check remains diagnostic-only.

---

# 28. LOG VIEWER UX

Provide:

- live tailing while an operation runs;
- search;
- level filters;
- operation filter;
- date/time display;
- copy selected;
- export;
- open log directory;
- clear visible filter;
- safe log retention.

Do not render massive logs in a way that freezes the GUI.

Use virtualization/pagination where appropriate.

---

# 29. OPERATION HISTORY UX

History should provide a compact table:

```text
Time       Profile       Operation      Result       Duration
10:42      Development   Sync           Warning      8.4s
09:15      Work          Launch         Success      6.1s
Yesterday  Development   Dry Run        Complete     0.8s
```

Selecting a row opens details.

Allow:

- view report;
- open logs;
- copy operation ID;
- rerun as Dry Run;
- inspect warnings.

Do not provide a one-click destructive "rerun" without applying the normal execution safety rules.

---

# 30. SETTINGS INFORMATION ARCHITECTURE

Organize Settings into:

```text
General
Appearance
Execution
Safety
Startup
Tray
Logging
Diagnostics
Advanced
About
```

Do not place unrelated settings in one giant form.

Every non-obvious setting should have a short explanation.

Advanced settings should clearly identify when changing them may affect execution behavior.

---

# 31. SETTINGS GUARDRAILS

For settings such as:

- timeouts;
- retries;
- polling;
- automation;
- startup;
- confirmation;

validate reasonable bounds.

Do not allow:

```text
negative timeout
negative retry count
zero/invalid polling interval
unbounded retry
```

unless the semantics explicitly require it.

Prefer bounded values with documented maximums.

---

# 32. FIRST-RUN EXPERIENCE — IMPROVED

The first-run wizard must distinguish **configuration** from **execution**.

Recommended flow:

```text
1. Welcome
2. System compatibility
3. Virtual Desktop capabilities
4. Detect current desktops
5. Create/select workspace profile
6. Map workspace desktops
7. Discover applications
8. Assign applications
9. Configure launch behavior
10. Review configuration
11. Save
12. Finish
```

At the end:

```text
Your workspace is configured.

Nothing has been launched.
Nothing has been moved.
No Virtual Desktop changes were performed.

[Open Workspace]
[Close]
```

Do not put a "Launch now" action immediately beside Finish unless it is clearly separated as an explicit next action.

---

# 33. GUIDED SETUP / CONFIGURATION CHECKLIST

Provide a persistent checklist where useful:

```text
Workspace Setup

✓ Profile created
✓ Desktop mappings configured
✓ Applications added
⚠ Postman path needs review
✓ Save completed
```

This should disappear or become optional once configuration is healthy.

---

# 34. SAFE QUICK ACTIONS

The dashboard may provide:

- Refresh;
- Dry Run;
- Launch Workspace;
- Sync;
- Open Logs;
- Health Check.

Do not put risky system-management actions into the quick-action area.

---

# 35. SYSTEM TRAY UX

If a tray implementation is included:

- tray icon must communicate state;
- tooltip should show profile and status;
- context menu must remain concise;
- Exit must actually stop the manager;
- tray actions must use the same authorization model as the GUI.

Recommended:

```text
Open Manager
Launch Workspace
Sync Workspace
Pause Automation
Health Check
View Logs
Settings
Exit
```

When the manager is only monitoring/idle:

```text
Virtual Desktop Workspace Manager
Development • Ready
```

When running:

```text
Development • Running
```

When warning:

```text
Development • Warning
```

---

# 36. NOTIFICATION AND TRAY SAFETY

Do not allow a background tray process to become an invisible automation engine.

If automation is disabled:

```text
No background workspace execution.
```

If startup automation is enabled, clearly show it in Settings and Diagnostics.

---

# 37. STATE MODEL — EXPANDED

Define explicit application states:

```text
UNINITIALIZED
SETUP_REQUIRED
READY
CONFIGURATION_DIRTY
VALIDATION_FAILED
DRY_RUN
PLANNING
AWAITING_CONFIRMATION
RUNNING
PAUSED
CANCELLING
CANCELLED
COMPLETED
COMPLETED_WITH_WARNINGS
FAILED
RECOVERY_REQUIRED
UNAVAILABLE
```

State transitions must be explicit and testable.

Do not allow UI state to imply execution state incorrectly.

---

# 38. OPERATION STATE MACHINE

Use:

```text
Idle
 ↓
Validate
 ↓
Discover
 ↓
Plan
 ↓
Await Approval
 ↓
Execute
 ↓
Verify
 ↓
Report
```

Failure branches:

```text
Validation Failed
Discovery Warning
Capability Blocked
Cancelled
Partial Failure
Unexpected Failure
Recovery Required
```

The UI must reflect these states accurately.

---

# 39. OPERATION SAFETY CONTRACT

Every real workspace operation must follow:

```text
1. Load configuration
2. Validate configuration
3. Detect capabilities
4. Discover current state
5. Resolve mappings
6. Build plan
7. Present/record plan
8. Obtain required authorization
9. Revalidate state
10. Execute one bounded action at a time
11. Revalidate before disruptive actions
12. Verify outcome
13. Continue or safely skip
14. Produce final report
15. Persist operation history
```

Never jump directly from a UI button to an arbitrary Windows API call.

---

# 40. ACTION CLASSIFICATION

Classify actions as:

### Read-only

- detect desktops;
- inspect windows;
- inspect processes;
- validate configuration;
- diagnostics;
- dry-run planning.

### Configuration-only

- add application;
- rename workspace label;
- change mapping;
- change settings;
- import configuration.

### Windows-state-changing

- create desktop;
- switch desktop;
- launch application;
- move window;
- startup registration.

This classification should be used in:

- confirmation UX;
- logs;
- permissions;
- tests;
- audit history.

---

# 41. AUTHORIZATION BOUNDARY

The application must distinguish:

```text
User requested configuration change
```

from:

```text
User authorized Windows-state execution
```

Examples:

- Saving `Brave → Desktop 4` does not move Brave immediately.
- Opening Configure does not launch applications.
- Switching profile does not launch applications.
- Importing a profile does not execute it.
- Dry Run does not execute.
- Health Check does not execute.
- Run Workspace explicitly authorizes execution.
- A direct "Move Now" action explicitly authorizes that move only.

---

# 42. MANUAL ACTION VS AUTOMATION

Every feature that can change Windows state should be understandable as either:

```text
Manual action
```

or:

```text
Workspace automation
```

Do not allow hidden automation to piggyback on harmless UI actions.

---

# 43. WINDOW-MATCHING TEST UI

When editing a matching rule, provide a **Test Match** function.

It must be diagnostic-only.

Example:

```text
Test Match

Rule:
Executable path = brave.exe
Title contains = GitHub

Matches:
✓ Brave
PID 1234
HWND 0x000...
Desktop: 2
Confidence: 90%

[Close]
```

Test Match must not move or launch anything.

---

# 44. APPLICATION DISCOVERY CACHE

If discovery caching is used:

- cache only application metadata;
- use bounded retention;
- invalidate when paths change;
- never treat cache as authoritative;
- never overwrite a user-selected executable because cached discovery differs.

---

# 45. STALE STATE UX

If cached or persisted state is stale:

```text
Workspace state may be outdated.

Windows reports that the mapped desktop no longer exists.

[Refresh]
[Review Mapping]
```

Do not silently repair ambiguous identity.

---

# 46. RECOVERY CENTER

Provide a simple recovery area under Diagnostics or Settings:

```text
Recovery

Configuration
✓ Current configuration valid
✓ Latest backup available

Previous Operation
⚠ Operation interrupted

[Review Operation]
[Run Dry Run]
[Restore Configuration]
```

Never automatically resume a workspace after a crash.

---

# 47. BACKUP UX

Show:

```text
Configuration Backups

Today
• 10:42 — Before import
• 09:15 — Before migration

Yesterday
• 16:30 — Manual backup
```

Actions:

```text
Create Backup
Restore
Export
Delete Old Backup
```

Restoration must be validated and confirmed.

Never delete the only valid backup.

---

# 48. IMPORT UX

Use:

```text
Select file
↓
Parse
↓
Validate
↓
Show changes
↓
Confirm
↓
Backup current configuration
↓
Apply atomically
↓
Verify
```

The preview must clearly distinguish:

```text
Added
Changed
Removed
Unresolved
Potentially unsafe
```

Imported configuration must never execute automatically.

---

# 49. EXPORT UX

Export should support:

- active profile;
- selected profile;
- full configuration.

Before exporting, offer:

```text
Include executable paths
Include advanced matching rules
Include environment settings
```

If exported data could contain sensitive information, warn the user.

---

# 50. PRIVACY-PRESERVING DIAGNOSTICS

Diagnostic reports should have two modes:

### Standard

Safe technical report with redaction.

### Detailed

More technical information, still excluding secrets.

Never include:

- passwords;
- tokens;
- browser cookies;
- authentication headers;
- private keys;
- arbitrary secret environment variables.

---

# 51. LOG REDACTION

Implement a centralized redaction layer rather than asking each logger call to remember what is sensitive.

Redact likely secret forms such as:

```text
token
password
apikey
api_key
authorization
secret
credential
```

Do not rely only on exact names.

Allow the redaction system to be extended.

---

# 52. PROCESS LAUNCH AUDIT

Before launching an application, log a safe summary:

```text
Launch requested
Application: Postman
Executable: <redacted/full path according to privacy policy>
Mode: Launch if missing
Reason: No compatible window detected
```

Do not log sensitive arguments.

---

# 53. EXECUTION CONCURRENCY MODEL

The application may use worker threads/tasks internally, but **workspace operations are serialized**.

A single operation may perform independent discovery tasks concurrently if that improves performance and is safe.

However:

- only one workspace executor owns Windows-state-changing operations;
- cancellation must propagate;
- worker failures must be collected;
- UI updates must be marshalled safely;
- workers must terminate cleanly.

---

# 54. RESOURCE LIFECYCLE

All Windows resources must have explicit ownership/lifecycle rules.

Cover:

- process handles;
- window handles;
- COM objects;
- threads;
- timers;
- event subscriptions;
- file handles;
- log handlers;
- temporary files.

Ensure cleanup on:

- success;
- failure;
- cancellation;
- application close;
- unexpected exceptions where possible.

---

# 55. MEMORY AND PERFORMANCE BUDGET

Aim for lightweight idle behavior.

The application should:

- avoid continuous full process enumeration;
- avoid continuous filesystem scanning;
- avoid unnecessary desktop polling;
- avoid duplicate timers;
- avoid unbounded in-memory logs;
- avoid retaining every historical window/process object;
- release resources promptly.

Where practical, use event-driven mechanisms.

If polling is necessary, centralize it and make it configurable.

---

# 56. LARGE WORKSPACE SUPPORT

The application must remain usable with:

- 10+ desktops;
- 50+ applications;
- many windows;
- long executable paths;
- long workspace names;
- long application names.

Use:

- virtualization/pagination;
- search;
- grouping;
- collapsible sections;
- lazy loading where appropriate.

Do not assume a four-desktop/four-application maximum.

---

# 57. INTERNATIONALIZATION READINESS

Version 1 may ship in English, but UI architecture should avoid hard-coding text into business logic.

Keep user-facing strings centralized where practical.

Do not assume:

- text always fits a fixed width;
- dates use one format;
- decimal separators are always identical.

Use Windows/user locale-aware formatting where appropriate.

---

# 58. DATE/TIME HANDLING

Store machine-readable timestamps consistently.

Display user-friendly local times.

Operation IDs should remain sortable.

Do not mix ambiguous date formats such as:

```text
01/02/2026
```

without context.

Prefer:

```text
2026-02-01
```

for logs/data and localized friendly formatting in the UI.

---

# 59. ERROR CODES AND SUPPORTABILITY

Every major failure should have a stable internal error category/code.

Example:

```text
VDM-001 Provider unavailable
VDM-002 Desktop identity mismatch
WIN-001 Window no longer exists
APP-001 Executable not found
CFG-001 Invalid configuration
SETUP-001 Dependency failure
```

User-facing messages should remain understandable.

Logs should contain the technical code.

---

# 60. SUPPORT BUNDLE

Provide a one-action way to prepare a support bundle containing:

- diagnostic report;
- relevant logs;
- configuration schema version;
- application/provider versions;
- sanitized operation history.

Do not include secrets or raw private application data.

Prefer an exportable archive such as ZIP if safe and supported.

---

# 61. DOCUMENTATION IMPROVEMENTS

In addition to the existing documentation requirements, create:

```text
docs/user-guide.md
docs/ui-ux-specification.md
docs/operation-state-machine.md
docs/error-catalog.md
docs/recovery-guide.md
docs/support-bundle.md
docs/test-strategy.md
docs/release-checklist.md
docs/compatibility-matrix.md
```

Keep documentation synchronized with implementation.

---

# 62. COMPATIBILITY MATRIX

Document support by Windows version/build where known:

```text
Capability                 Win10       Win11
------------------------------------------------
Enumerate desktops         Supported   Supported/conditional
Current desktop            ...
Window desktop detection   ...
Window movement            ...
Desktop creation           ...
Desktop switching          ...
```

Do not claim support until technically verified.

Mark:

```text
Supported
Conditional
Unsupported
Unknown
```

---

# 63. FEATURE CAPABILITY MATRIX

The UI should derive available actions from detected capabilities.

Example:

```text
Create Desktop
✓ Available

Move Window
✓ Available

Switch Desktop
⚠ Requires provider capability

Delete Desktop
✕ Not implemented
```

Disabled controls must explain why they are unavailable.

Do not simply gray out a control without explanation.

---

# 64. FEATURE FLAGS

If optional/experimental features exist:

- keep them disabled by default;
- label them clearly;
- do not expose unstable features as normal production behavior;
- document them;
- ensure they cannot bypass safety controls.

---

# 65. ADVANCED MODE

A clearly labeled Advanced/Developer view may expose:

- provider details;
- GUIDs;
- HWNDs;
- PIDs;
- raw capability data;
- API errors;
- execution plan internals.

Do not require Advanced Mode for normal use.

---

# 66. CONFIGURATION SCHEMA DESIGN

Prefer a normalized, versioned model with stable IDs.

Conceptually:

```text
Application
 ├─ id
 ├─ name
 ├─ executable
 ├─ arguments
 ├─ workingDirectory
 ├─ enabled
 ├─ desktopId
 ├─ launchPolicy
 ├─ matchingPolicy
 └─ executionPolicy

Workspace
 ├─ id
 ├─ name
 ├─ desktops[]
 └─ applications[]

Desktop
 ├─ id
 ├─ name
 ├─ windowsDesktopId
 ├─ displayOrder
 └─ mappingStatus
```

Avoid duplicating the same authoritative value in multiple places unless migration/compatibility requires it.

---

# 67. CONFIGURATION VALIDATION LAYERS

Use:

```text
Syntax validation
→ Schema validation
→ Semantic validation
→ Capability validation
→ Execution readiness validation
```

Examples:

A valid path can still be invalid because:

- it points to a directory;
- it is inaccessible;
- it is not an executable;
- its desktop mapping is unresolved.

Do not stop at JSON parsing.

---

# 68. EXECUTION READINESS

Before Run Workspace, display:

```text
Ready to run
```

only if all blocking conditions are resolved.

Warnings may be allowed when policy permits.

Example:

```text
✓ Configuration valid
✓ Provider available
✓ Desktop mappings valid
⚠ Postman unavailable
```

Then:

```text
Run with warnings
```

must be explicit.

---

# 69. DRY-RUN GUARANTEE

Dry Run must be architecturally incapable of invoking Windows-state-changing operations.

Prefer a plan/executor design where Dry Run uses a non-mutating executor rather than merely setting scattered boolean flags.

This is stronger and easier to test.

---

# 70. SAFE EXECUTOR DESIGN

The execution engine should receive an approved execution plan.

It should not invent new actions during execution.

If execution discovers that the world changed:

```text
Revalidate
→ Replan or safely skip
```

Do not silently expand scope.

---

# 71. PLAN IMMUTABILITY

Once a user approves a plan:

- keep a snapshot;
- record operation ID;
- execute only approved scope;
- if material state changes, require re-planning where necessary.

Do not let background discovery silently add new applications to an approved run.

---

# 72. OPERATION SCOPE

Every operation should identify:

```text
Profile
Workspace
Target desktops
Target applications
Operation type
Authorization source
```

This prevents accidental cross-profile execution.

---

# 73. CROSS-PROFILE SAFETY

Never combine applications from two profiles unless the user explicitly creates a combined workspace.

Running:

```text
Development
```

must not accidentally execute:

```text
Work
```

or:

```text
Personal
```

configuration.

---

# 74. APPLICATION OWNERSHIP

The workspace manager does not own installed applications.

It owns only:

- workspace configuration;
- application references;
- its own logs;
- its own backups;
- its own shortcuts.

Removing a reference must never imply removal of the application itself.

---

# 75. WINDOWS DESKTOP OWNERSHIP

The manager does not own the user's Virtual Desktops.

It may reference/manage only the desktops explicitly mapped into the active workspace.

Extra desktops remain outside its scope.

---

# 76. USER-INITIATED WINDOW MOVES

If the user manually moves a managed window:

- do not immediately move it back;
- record the divergence when practical;
- allow the next explicit Sync to reconcile it;
- if aggressive automation is enabled, clearly document that behavior.

---

# 77. AUTOMATION MODES

Provide explicit modes:

```text
Manual
```

No automatic reconciliation.

```text
Assisted
```

Show suggested corrections; require approval.

```text
Automatic
```

Allow configured automation subject to safety rules.

Default:

```text
Manual
```

Do not make Automatic the default.

---

# 78. AUTOMATION SAFETY

Even Automatic mode must never:

- kill processes;
- uninstall applications;
- delete files;
- delete desktops automatically;
- execute arbitrary commands;
- bypass configuration validation;
- bypass capability checks.

---

# 79. STARTUP AUTOMATION SAFETY

Keep separate:

```text
Start Manager with Windows
```

and:

```text
Run Workspace automatically at login
```

Both default OFF.

When enabling workspace-at-login, show a stronger warning:

```text
This will allow the manager to change your desktop/application
state automatically after Windows login.

You can disable it later in Settings.
```

---

# 80. SETUP/INSTALLATION UX

When the user explicitly runs setup, show:

```text
Virtual Desktop Workspace Manager Setup

System
Windows: ...
Python: ...
Architecture: ...

Environment
✓ Project environment
✓ Dependencies

Configuration
✓ Existing configuration preserved

Shortcuts
✓ Configure
✓ Run Workspace

No workspace was launched.
```

Provide a final clear state:

```text
Setup completed successfully.

The application is ready.
Nothing was launched.
```

---

# 81. SETUP MUST NOT BE A HIDDEN RUNTIME

Do not make `setup.py` import and initialize the workspace executor merely to verify it.

Setup may verify imports and static contracts, but must not trigger runtime workspace behavior.

---

# 82. RELEASE/BUILD SEPARATION

Keep these concepts separate:

```text
Development
Testing
Setup
Packaging
Runtime
Workspace Execution
```

A build step must not automatically become a runtime step.

---

# 83. PACKAGING QUALITY

If packaging is implemented:

- use reproducible build configuration;
- document build prerequisites;
- preserve version information;
- include icons/resources;
- ensure paths are correct;
- ensure logs/config remain user-level;
- ensure the packaged application behaves identically to source mode.

Do not use packaging to hide unsafe behavior.

---

# 84. RELEASE CHECKLIST

Before declaring a release candidate:

```text
[ ] Requirements traceability complete
[ ] Static security review complete
[ ] Mock tests complete
[ ] Configuration migration tested
[ ] Setup tested in isolation
[ ] Packaging reviewed
[ ] Shortcut targets reviewed
[ ] Shortcut ownership reviewed
[ ] UI keyboard navigation reviewed
[ ] Empty/loading/error states reviewed
[ ] Logs redacted
[ ] Diagnostics redacted
[ ] No unexpected network behavior
[ ] No startup persistence unless explicitly configured
[ ] No real workspace manipulated during development
```

---

# 85. TEST STRATEGY — EXPANDED

Use test layers:

```text
Unit
 ↓
Contract
 ↓
Mock integration
 ↓
Configuration
 ↓
Static security
 ↓
Packaging/shortcut validation
 ↓
Manual real-Windows validation — only after explicit authorization
```

Do not skip directly to real Windows testing.

---

# 86. CONTRACT TESTS FOR PROVIDERS

Every Windows-specific provider should have a contract test suite.

Examples:

```text
enumerate_desktops()
get_current_desktop()
get_window_desktop()
move_window()
create_desktop()
switch_desktop()
```

Mocks must conform to the same contract.

This prevents business logic from becoming dependent on one specific implementation.

---

# 87. FAILURE INJECTION TESTS

Simulate:

- provider unavailable;
- desktop disappears;
- window disappears;
- PID changes;
- process exits;
- executable missing;
- launch timeout;
- ambiguous window;
- configuration corruption;
- backup failure;
- disk write failure;
- cancellation during wait;
- cancellation before launch;
- partial operation failure;
- unexpected exception.

The product must fail safely.

---

# 88. FUZZ / ROBUSTNESS TESTING

Where practical, test configuration parsing with:

- missing fields;
- unknown fields;
- invalid types;
- invalid paths;
- extreme string lengths;
- malformed regex;
- negative values;
- huge values;
- duplicate IDs;
- circular/invalid references;
- invalid Unicode.

Do not allow malformed configuration to crash the manager.

---

# 89. UI TESTING

Test:

- startup;
- navigation;
- first-run wizard;
- add application;
- edit application;
- reassign application;
- multiple applications per desktop;
- save;
- unsaved changes;
- import/export;
- dry run;
- execution plan;
- cancellation;
- error dialogs;
- accessibility navigation;
- resizing;
- long names;
- empty states;
- loading states.

Prefer UI tests with mocked providers.

---

# 90. SECURITY ACCEPTANCE TESTS

Verify:

```text
No arbitrary shell execution
No encoded PowerShell
No dynamic download-and-execute
No silent elevation
No hidden startup persistence
No unsafe config execution
No secret logging
No destructive cleanup
No process killing
No desktop deletion
```

---

# 91. PERFORMANCE ACCEPTANCE TESTS

Measure where practical:

- startup time;
- idle CPU;
- idle memory;
- discovery duration;
- planning duration;
- execution responsiveness;
- log viewer performance.

Avoid inventing strict numbers unless measured.

Report observed values honestly.

---

# 92. FAILURE COMMUNICATION

Every failure report should include:

```text
Status
What happened
Scope affected
What was not changed
Suggested next action
Technical details
Operation ID
```

This is especially important for Windows API failures.

---

# 93. USER TRUST REQUIREMENT

The product must always make it possible for the user to answer:

> "What is this application about to change?"

and:

> "What did it actually change?"

This should be supported by:

- execution plan;
- operation history;
- logs;
- verification;
- diagnostics;
- explicit authorization;
- clear final report.

---

# 94. FINAL PRODUCT SUCCESS CRITERIA

The product is successful only if all of the following are true:

### Functionality

- [ ] Multiple applications can belong to one workspace desktop.
- [ ] Applications can be added without source-code changes.
- [ ] Applications can be reassigned.
- [ ] Applications can be removed from configuration without uninstalling them.
- [ ] Profiles work independently.
- [ ] Desired vs actual state is modeled.
- [ ] Dry Run is genuinely non-mutating.
- [ ] Launch and Sync are distinct.
- [ ] Duplicate launches are prevented.
- [ ] Window matching is conservative.
- [ ] Desktop identity is handled safely.
- [ ] Operations are verified where possible.

### Safety

- [ ] No automatic desktop deletion.
- [ ] No process termination.
- [ ] No file deletion.
- [ ] No application uninstallation.
- [ ] No hidden shell execution.
- [ ] No silent elevation.
- [ ] No hidden startup persistence.
- [ ] No telemetry.
- [ ] No runtime network requirement.
- [ ] No real workspace manipulation during Antigravity development.

### UX

- [ ] Clear navigation.
- [ ] Clear visual hierarchy.
- [ ] Responsive resizing.
- [ ] Keyboard navigation.
- [ ] Accessible focus states.
- [ ] Empty states.
- [ ] Loading states.
- [ ] Error states.
- [ ] Success states.
- [ ] Unsaved-change protection.
- [ ] Search/filtering where needed.
- [ ] Consistent terminology.
- [ ] No fake controls.
- [ ] No fake success.

### Persistence

- [ ] GUI changes persist.
- [ ] Run Workspace uses the same saved configuration.
- [ ] Configuration is versioned.
- [ ] Writes are atomic.
- [ ] Backups exist.
- [ ] Import/export is validated.
- [ ] Migration is safe.

### Setup

- [ ] Root `setup.py` exists.
- [ ] Setup is separate from runtime.
- [ ] Setup is idempotent.
- [ ] Existing configuration is preserved.
- [ ] Dependencies are controlled.
- [ ] Configure shortcut exists.
- [ ] Run Workspace shortcut exists.
- [ ] Shortcut ownership is tracked.
- [ ] Re-running setup does not duplicate shortcuts.
- [ ] Unrelated shortcuts are preserved.
- [ ] Setup does not execute the workspace.

### Engineering

- [ ] Windows APIs are isolated behind providers.
- [ ] Mock providers exist.
- [ ] Business logic is testable without Windows.
- [ ] Cancellation is cooperative.
- [ ] Only one workspace executor runs at once.
- [ ] Crash recovery is explicit.
- [ ] Logs are structured.
- [ ] Diagnostic reports are redacted.
- [ ] Resource cleanup is implemented.
- [ ] Documentation matches implementation.

---

# 95. REQUIRED DELIVERABLES — EXPANDED

The finished project must contain, as applicable:

## Source

- complete production-oriented source;
- clean architecture;
- provider abstractions;
- UI;
- configuration system;
- workspace engine;
- planner;
- executor;
- verifier;
- discovery services;
- diagnostics;
- logging;
- setup/bootstrap;
- packaging support.

## Documentation

At minimum:

```text
README.md
CHANGELOG.md
docs/requirements-analysis.md
docs/technology-decision.md
docs/architecture.md
docs/configuration-schema.md
docs/windows-api-compatibility.md
docs/safety-review.md
docs/security-review.md
docs/setup-security-review.md
docs/ui-ux-specification.md
docs/operation-state-machine.md
docs/error-catalog.md
docs/recovery-guide.md
docs/support-bundle.md
docs/test-strategy.md
docs/compatibility-matrix.md
docs/release-checklist.md
docs/final-review.md
docs/requirements-traceability.md
docs/troubleshooting.md
```

## Tests

Include:

- unit tests;
- provider contract tests;
- mock integration tests;
- configuration tests;
- migration tests;
- setup tests;
- shortcut tests;
- security tests;
- failure-injection tests;
- UI tests where the selected framework supports them.

## Assets

Include:

- application icon;
- Configure icon variant if practical;
- Run Workspace icon variant if practical;
- any required local UI resources.

---

# 96. FINAL ANTIGRAVITY WORKFLOW

Follow this sequence exactly.

## Phase 1 — Analyze

Read the entire specification.

Identify:

- functional requirements;
- safety requirements;
- UX requirements;
- Windows API dependencies;
- compatibility risks;
- setup requirements;
- testing requirements.

Create:

```text
docs/requirements-analysis.md
```

Do not run the application.

## Phase 2 — Technology decision

Create:

```text
docs/technology-decision.md
```

Compare realistic Windows technologies.

Choose based on reliability and maintainability.

## Phase 3 — Architecture

Create:

```text
docs/architecture.md
docs/operation-state-machine.md
```

## Phase 4 — UX specification

Create:

```text
docs/ui-ux-specification.md
```

Define:

- navigation;
- page hierarchy;
- component states;
- dialogs;
- empty states;
- loading states;
- error states;
- accessibility;
- keyboard behavior;
- responsive behavior.

## Phase 5 — Data model

Create:

```text
docs/configuration-schema.md
```

## Phase 6 — Safety review

Create:

```text
docs/safety-review.md
docs/security-review.md
docs/setup-security-review.md
```

## Phase 7 — Implementation

Build the complete application.

Do not stop at the UI.

Do not create fake controls.

Do not create disconnected screens.

## Phase 8 — Static validation

Inspect the entire source tree.

Search for:

```text
TODO
FIXME
pass
NotImplemented
stub
fake
placeholder
coming soon
shell=True
EncodedCommand
Invoke-Expression
Start-Process
subprocess
os.system
```

Review every potentially dangerous occurrence manually.

## Phase 9 — Safe tests

Use mocks/fakes.

Do not manipulate the real Windows Virtual Desktop environment.

Do not execute `setup.py`.

Do not create real Desktop shortcuts.

Do not launch the generated application.

## Phase 10 — Final review

Create:

```text
docs/final-review.md
docs/requirements-traceability.md
```

For every requirement mark:

```text
PASS
PARTIAL
NOT IMPLEMENTED
UNSUPPORTED
```

Do not mark PASS merely because a screen or button exists.

## Phase 11 — Stop

After implementation and safe validation:

**STOP.**

Do not:

- launch the application;
- execute setup;
- create real shortcuts;
- launch configured applications;
- manipulate Virtual Desktops.

Report the result and wait for explicit authorization.

---

# 97. FINAL RESPONSE REQUIRED FROM ANTIGRAVITY

When the work is complete, report:

1. technology selected;
2. architecture;
3. project structure;
4. files created;
5. dependencies;
6. API/provider strategy;
7. Windows compatibility;
8. implemented features;
9. UX improvements;
10. accessibility features;
11. persistence model;
12. setup behavior;
13. shortcut behavior;
14. tests created;
15. tests actually executed;
16. static validation performed;
17. security review results;
18. known limitations;
19. unsupported Windows features;
20. packaging instructions;
21. configuration location;
22. log location;
23. diagnostics instructions;
24. remaining issues;
25. whether `setup.py` was executed;
26. whether the application was launched;
27. whether real Desktop shortcuts were created;
28. whether real Virtual Desktops were manipulated.

Clearly separate:

```text
STATIC VALIDATION
MOCK TESTING
PACKAGING VALIDATION
REAL WINDOWS TESTING
```

If real Windows testing was not authorized, explicitly say:

```text
Real Windows runtime validation was NOT performed.
```

Never imply otherwise.

---

# 98. ABSOLUTE FINAL RULES

These rules override convenience.

1. **DO NOT RUN THE GENERATED APPLICATION during development.**
2. **DO NOT RUN `setup.py` during development.**
3. **DO NOT CREATE REAL DESKTOP SHORTCUTS during development.**
4. **DO NOT MANIPULATE REAL VIRTUAL DESKTOPS during development.**
5. **DO NOT LAUNCH CONFIGURED APPLICATIONS during development.**
6. **DO NOT DELETE VIRTUAL DESKTOPS automatically.**
7. **DO NOT KILL PROCESSES.**
8. **DO NOT UNINSTALL APPLICATIONS.**
9. **DO NOT DELETE USER FILES.**
10. **DO NOT MODIFY DEVELOPMENT DATA.**
11. **DO NOT SILENTLY ELEVATE.**
12. **DO NOT CREATE HIDDEN STARTUP PERSISTENCE.**
13. **DO NOT DISABLE WINDOWS SECURITY.**
14. **DO NOT USE UNSAFE ARBITRARY SHELL COMMANDS.**
15. **DO NOT EXECUTE CONFIGURATION AS CODE.**
16. **DO NOT CLAIM SUCCESS WITHOUT VERIFICATION.**
17. **DO NOT TREAT A PROCESS AS A WINDOW.**
18. **DO NOT TRUST STALE HWNDs OR PIDs.**
19. **DO NOT ASSUME DESKTOP POSITION IS PERMANENT IDENTITY.**
20. **DO NOT SILENTLY EXECUTE AFTER OPENING THE GUI.**
21. **DO NOT SILENTLY EXECUTE AFTER SAVING CONFIGURATION.**
22. **DO NOT SILENTLY EXECUTE AFTER IMPORTING A PROFILE.**
23. **DO NOT SILENTLY EXECUTE AFTER SWITCHING PROFILES.**
24. **DO NOT LET ONE OPERATION RUN CONCURRENTLY WITH ANOTHER.**
25. **DO NOT ADD TELEMETRY.**
26. **DO NOT ADD AN AUTOMATIC UPDATER IN VERSION 1.**
27. **DO NOT ADD UNRELATED SYSTEM-CLEANING FEATURES.**
28. **DO NOT USE FAKE DATA IN PRODUCTION UI.**
29. **DO NOT CREATE BUTTONS THAT DO NOTHING.**
30. **DO NOT HIDE UNSUPPORTED CAPABILITIES.**
31. **DO NOT SACRIFICE SAFETY FOR AUTOMATION.**
32. **DO NOT SACRIFICE RELIABILITY FOR VISUAL EFFECTS.**
33. **DO NOT SACRIFICE ACCESSIBILITY FOR COMPACTNESS.**
34. **DO NOT SACRIFICE MAINTAINABILITY FOR SPEED OF INITIAL IMPLEMENTATION.**
35. **DO NOT CLAIM PRODUCTION-READY STATUS while critical features remain stubbed.**
36. **DO NOT EXECUTE ANY REAL ACTION UNTIL THE USER EXPLICITLY AUTHORIZES IT.**

---

# 99. IMPLEMENTATION START COMMAND

Begin by analyzing the entire specification and producing the required design/architecture documentation.

Then implement the complete product.

Then perform static validation and safe mocked tests.

Then stop.

**DO NOT RUN THE APPLICATION.**

**DO NOT RUN SETUP.**

**DO NOT CREATE THE REAL DESKTOP SHORTCUTS.**

**DO NOT RUN THE WORKSPACE.**

**WAIT FOR EXPLICIT USER AUTHORIZATION.**

---

# ORIGINAL DETAILED REQUIREMENTS — RETAINED BASELINE

The original detailed specification follows below and remains part of the product contract. The sections above add higher-priority product/UX/quality requirements and clarify behavior where necessary.


# RETAINED BASELINE SPECIFICATION

The following original detailed requirements are retained as the implementation baseline.

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

Version 1 must have **no network requirement during normal application runtime**.

Setup may require network access only when `setup.py` explicitly installs declared Python dependencies from the approved package source.

Do not add:

* telemetry
* analytics
* remote logging
* cloud synchronization
* remote commands
* update downloads

unless explicitly requested later.

The running application must not contact the network merely to:

* open the GUI
* load configuration
* inspect local processes/windows
* manage supported Virtual Desktop operations
* write logs
* run diagnostics

If dependencies are already available locally, setup should be able to proceed without unnecessary network access.

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

Provide a development/source mode and optional packaged mode.

The project MUST include the root-level `setup.py` setup/bootstrap entry point defined in Sections 83B–83L.

Installation/setup and workspace execution are separate operations.

If Python is used, consider a reputable packaging method such as PyInstaller only after the application works correctly.

Packaging must not hide unsafe behavior.

The packaged application must:

* use the same configuration
* use the same safety rules
* preserve logs
* preserve user configuration
* not automatically launch the workspace
* preserve the `--config`, `--run`, `--dry-run`, `--diagnostics`, `--version`, and `--help` command contract
* remain separate from the `setup.py` setup/bootstrap responsibility

The source-mode setup path must be fully documented and must use `setup.py`.

Do not make `setup.py` a hidden alias for `main.py --run`.

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

# 83B. `setup.py` — SINGLE EXPLICIT SYSTEM SETUP / BOOTSTRAP ENTRY POINT

`setup.py` is the **single supported setup entry point** for installing and configuring the application on a Windows 10/11 PC.

The intended user experience is:

```text
Project folder
    ↓
setup.py
    ↓
Environment + dependencies + configuration + two Desktop shortcuts
    ↓
READY FOR USE
```

After setup completes, the user should not need to manually install Python packages, create application folders, create Desktop shortcuts, or enter command-line arguments.

## Critical Separation

`setup.py` is a **SETUP / INSTALL / REPAIR program only**.

It is NOT the workspace execution entry point.

The architecture must remain:

```text
setup.py
    ↓
SETUP / REPAIR / DIAGNOSTICS ONLY

main.py --config
    ↓
CONFIGURATION GUI ONLY

main.py --run
    ↓
EXPLICIT WORKSPACE EXECUTION
```

If a packaged executable is later produced:

```text
VirtualDesktopWorkspaceManager.exe --config
VirtualDesktopWorkspaceManager.exe --run
```

`setup.py` must never silently call `main.py --run`.

`setup.py` must never launch the workspace merely because installation succeeded.

## Required File

The project root must contain:

```text
setup.py
```

This must be a real, maintainable Python setup/bootstrap program. Do not confuse it with the legacy Python packaging convention of using `setup.py` only for package metadata.

Document the distinction clearly in `README.md`.

## Supported Setup Commands

At minimum:

```text
py setup.py
py setup.py --setup
py setup.py --repair
py setup.py --check
py setup.py --help
py setup.py --version
```

`py setup.py` and `py setup.py --setup` perform normal setup.

`--repair` repairs only application-owned setup artifacts.

`--check` is non-destructive diagnostics.

`--help` and `--version` are non-destructive.

There must be no default mode in which `setup.py` runs the workspace.

Do not add `py setup.py --run` as an alias for workspace execution.

## What `setup.py` Must Do

When explicitly executed by the user, `setup.py` must:

1. Verify Windows 10/11 compatibility.
2. Verify a supported Python version and architecture.
3. Detect the project root from `setup.py`.
4. Create or reuse a project-local `.venv`.
5. Install only declared, controlled dependencies.
6. Verify required imports and dependency versions.
7. Create required application-owned user directories.
8. Create a safe initial configuration if none exists.
9. Preserve valid existing configuration.
10. Back up and safely migrate configuration when schema changes.
11. Create/repair the two Desktop shortcuts.
12. Verify shortcut targets, arguments, working directories, and icons.
13. Record setup state.
14. Write a dedicated setup log.
15. Return a meaningful exit code.
16. Stop after setup.

## Python Prerequisite

A Python script cannot bootstrap Python before Python exists.

Therefore, if Python is missing or incompatible, `setup.py` must stop with a clear message explaining that a supported Python installation is required.

It must NOT:

* silently download Python
* silently install Python
* modify system PATH without explicit authorization
* download and execute an arbitrary installer
* weaken Windows security controls

A future packaged installer may handle the Python prerequisite separately, but that is outside `setup.py`.

## Project and Environment Safety

Derive the project root from the location of `setup.py`.

Do not hard-code the developer's path.

Prefer:

```text
<project-root>\.venv\
```

for the application environment.

Do not pollute global Python unnecessarily.

Reuse a valid `.venv` instead of deleting and recreating it on every setup.

## Dependency Installation

Declare dependencies in one authoritative file, such as:

```text
requirements.txt
requirements.lock
pyproject.toml
```

The chosen source must be documented.

Prefer pinned/reproducible versions for production.

Install only declared dependencies from an approved package source.

Do not install arbitrary packages based on configuration values or user-provided URLs.

If network access is needed for dependency installation, report it clearly. Normal runtime operation should remain offline-capable unless a documented feature genuinely requires network access.

## Configuration Persistence

Store authoritative user configuration in a stable per-user location, for example:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\config\
```

Recommended application-owned structure:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\
    config\
    profiles\
    backups\
    logs\
    diagnostics\
    state\
    cache\
```

The exact schema must be documented.

The GUI and Run Workspace entry point must use the **same authoritative configuration source**.

If no configuration exists, create only a safe minimal/default configuration.

If a valid configuration exists:

**NEVER overwrite it merely because setup was rerun.**

For schema migration:

```text
validate
→ backup
→ migrate
→ validate migrated result
→ commit
```

If migration fails, preserve the original.

Do not silently discard unknown configuration fields.

## Create the Two Desktop Shortcuts

`setup.py` must create exactly two application-owned Desktop shortcuts for the current Windows user:

```text
Virtual Desktop Workspace Manager — Configure
Virtual Desktop Workspace Manager — Run Workspace
```

Obtain the actual Desktop path through a reliable Windows known-folder mechanism or equivalent.

Do not assume:

```text
C:\Users\<username>\Desktop
```

because Desktop can be redirected, localized, or synchronized.

### Shortcut 1 — Configure

Purpose:

```text
Open configuration GUI only
```

It must:

* load saved configuration
* show the active profile
* allow configuration changes
* save valid changes persistently
* use the same configuration source as Run Workspace
* pass an explicit `--config` mode
* use an application-owned icon
* use a deterministic working directory

It must NEVER:

* launch configured applications
* create Virtual Desktops
* move windows
* switch desktops
* execute the workspace
* enable startup automation

### Shortcut 2 — Run Workspace

Purpose:

```text
Explicitly execute the saved active workspace
```

It must:

* use the same persisted configuration
* validate configuration before execution
* use explicit `--run`
* respect confirmation policy
* execute only the active profile
* apply all existing safety, cancellation, timeout, retry, logging, and verification rules
* return meaningful exit status

Double-clicking this shortcut is an explicit user request to execute the workspace. Double-clicking Configure is not.

If configuration is missing or invalid, Run Workspace must stop safely rather than guessing or falling back to hidden defaults.

## Source-Mode Shortcut Targets

A source-mode implementation may use:

Configure:

```text
<project-root>\.venv\Scripts\pythonw.exe
```

Arguments:

```text
"<project-root>\main.py" --config
```

Run Workspace:

```text
<project-root>\.venv\Scripts\python.exe
```

Arguments:

```text
"<project-root>\main.py" --run
```

Use the actual selected architecture if it differs.

## Packaged Shortcut Targets

A packaged implementation may use:

```text
VirtualDesktopWorkspaceManager.exe --config
VirtualDesktopWorkspaceManager.exe --run
```

Source and packaged modes must use the same logical configuration and safety rules.

## Shortcut Icons

Provide application-owned `.ico` assets, for example:

```text
assets\VirtualDesktopWorkspaceManager.ico
```

Distinct Configure/Run icon variants are preferred when practical.

Do not rely on misleading or arbitrary system icons.

## Shortcut Ownership and Repair

`setup.py` must identify application-owned shortcuts using a combination of:

* stable application identifier
* deterministic shortcut name
* validated target
* validated arguments
* application-owned icon and/or metadata

Repair only shortcuts confidently identified as application-owned.

Never delete or modify unrelated Desktop shortcuts.

If duplicates exist, detect them and handle them conservatively.

## Idempotency

Repeated setup must converge to:

```text
one valid Configure shortcut
one valid Run Workspace shortcut
```

It must never create:

```text
Configure (1)
Configure (2)
Run Workspace (1)
```

or equivalent duplicates.

## Setup State

Maintain setup state separately from workspace configuration, for example:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\state\setup.json
```

It may contain:

* setup version
* application version
* Python version
* environment path
* dependency status
* shortcut status
* last setup timestamp
* migration status

It must NOT be the authoritative source for workspace mappings.

## Setup Logging

Write:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\logs\setup.log
```

Include:

* timestamp
* setup/application version
* Windows version
* Python version
* architecture
* setup mode
* steps
* created/reused/repaired items
* warnings
* errors
* final status
* exit code

Never log passwords, tokens, API keys, or secrets.

## Setup Plan

Before material system changes, show a concise setup plan:

```text
Virtual Desktop Workspace Manager Setup

Windows:        <detected version>
Python:         <detected version>
Environment:    <path>
Dependencies:   <status>
Configuration:  <status>
Desktop:        <path>

Planned actions:
[ ] Create/reuse virtual environment
[ ] Install declared dependencies
[ ] Create/validate configuration
[ ] Create/repair Configure shortcut
[ ] Create/repair Run Workspace shortcut

This setup does NOT launch the workspace.
```

If the setup is interactive, require clear confirmation before material changes.

`--check` must remain non-destructive.

## Setup Must Never Perform Runtime Actions

`setup.py` must never:

* launch the GUI automatically
* launch the workspace
* launch configured applications
* create/delete Virtual Desktops
* switch the current Virtual Desktop
* move application windows
* terminate application processes
* uninstall applications
* delete user files
* modify development data
* create startup entries
* create scheduled tasks
* create services
* disable UAC
* disable Defender
* disable SmartScreen
* modify firewall rules
* weaken security policies
* modify unrelated registry settings
* modify unrelated shortcuts

Successful setup means:

```text
READY FOR USER
```

not:

```text
WORKSPACE STARTED
```

## Exit Codes

Define and document meaningful exit codes, for example:

```text
0 = success
1 = general setup failure
2 = unsupported OS
3 = missing/incompatible Python
4 = dependency failure
5 = configuration failure
6 = shortcut failure
7 = permission failure
8 = user cancellation
9 = incomplete setup / repair required
```

Do not return `0` when required setup failed.

## Repair Mode

`--repair` may repair:

* missing application directories
* missing/broken declared dependencies
* application-owned shortcut targets
* application-owned icons
* setup state

It must preserve valid user configuration and backups.

It must not become a general Windows repair utility.

## Check Mode

`--check` must report without modifying the system:

```text
OS
Python
Architecture
Virtual environment
Dependencies
Configuration
Schema
Shortcut status
Icon status
Required files
Permissions
Setup state
```

It must not install packages, create shortcuts, modify configuration, launch applications, or manipulate Virtual Desktops.

## Partial Failure and Recovery

Setup must tolerate interruption and partial failure.

Examples:

* dependencies installed but shortcuts failed
* first shortcut created but second failed
* configuration migration failed
* virtual environment creation succeeded but dependency installation failed

Record completed steps and leave the system in a recoverable state.

Do not delete unrelated data as rollback.

The next `setup.py` or `--repair` invocation must be able to continue safely.

## Path and File Safety

Validate all application-owned paths.

Protect against:

* path traversal
* malformed relative paths
* unexpected reparse points/symlinks where relevant
* accidental system-directory targeting
* accidental user-data targeting
* malformed configuration paths

Configuration values must never become arbitrary shell commands.

## Single Setup Authority

`setup.py` is the one user-facing setup authority.

Do not create competing user-facing setup scripts such as:

```text
install.py
bootstrap.py
setup_windows.py
setup_final.py
```

Helper modules are allowed only when invoked by `setup.py` and documented as internal implementation details.

## Safe Re-runs

The user should be able to rerun:

```text
py setup.py
```

after a reboot, application update, shortcut deletion, or configuration change without losing valid workspace configuration.

Setup must be idempotent and configuration-preserving.

## Startup Automation

Desktop shortcuts are required.

Do not automatically create:

* Startup-folder entries
* Registry Run entries
* scheduled tasks
* services

Startup automation must remain a separate explicitly enabled feature.

## Setup Acceptance Tests

Create mocked/unit tests for at least:

```text
SETUP-001 Windows 10 accepted
SETUP-002 Windows 11 accepted
SETUP-003 Unsupported OS blocked
SETUP-004 Supported Python detected
SETUP-005 Missing Python reported safely
SETUP-006 Compatible .venv reused
SETUP-007 Missing .venv created
SETUP-008 Only declared dependencies installed
SETUP-009 Dependency failure returns nonzero
SETUP-010 Required imports verified
SETUP-011 Application directories created
SETUP-012 Initial configuration created safely
SETUP-013 Existing configuration preserved
SETUP-014 Migration creates backup
SETUP-015 Invalid configuration blocks unsafe migration
SETUP-016 Configure shortcut created
SETUP-017 Run shortcut created
SETUP-018 Shortcut targets correct
SETUP-019 Shortcut arguments correct
SETUP-020 Shortcut icons correct
SETUP-021 Repeated setup creates no duplicates
SETUP-022 Broken owned shortcut repaired
SETUP-023 Unrelated shortcut preserved
SETUP-024 --check is non-destructive
SETUP-025 --help is non-destructive
SETUP-026 --version is non-destructive
SETUP-027 setup never launches configured applications
SETUP-028 setup never manipulates Virtual Desktops
SETUP-029 setup never moves windows
SETUP-030 setup never enables startup automation
SETUP-031 setup failure returns nonzero
SETUP-032 partial setup can be resumed
SETUP-033 setup state recorded
SETUP-034 setup log written without secrets
SETUP-035 valid configuration is never overwritten
```

All Windows-specific operations must be mockable.

Do not run these tests against the user's real Desktop or real Virtual Desktop during Antigravity development.

## Setup Security Review

Create:

```text
docs/setup-security-review.md
```

For each risk document:

```text
Risk
Impact
Mitigation
Test
Residual Risk
```

Cover:

* dependency supply-chain risk
* package source trust
* arbitrary code execution
* path injection
* shortcut hijacking
* malformed configuration
* migration safety
* privilege escalation
* global Python pollution
* accidental app launch
* accidental Virtual Desktop manipulation
* partial/interrupted setup
* duplicate shortcuts
* unrelated shortcut protection
* secret leakage
* network access
* symlink/reparse-point risks
* permissions
* repair behavior

---

# 83C. TWO SHORTCUTS — SOURCE MODE AND PACKAGED MODE

The two Desktop shortcuts must work in both supported deployment models.

## Development/source mode

If the user has not packaged the application, shortcuts may target the project's approved Python runtime and application entry point, for example:

```text
<project>\.venv\Scripts\pythonw.exe <project>\main.py --config
```

and:

```text
<project>\.venv\Scripts\python.exe <project>\main.py --run
```

The exact implementation may differ.

The shortcut target must use explicit executable + argument separation and must not construct an arbitrary shell command.

## Packaged mode

If the application is packaged:

```text
VirtualDesktopWorkspaceManager.exe --config
VirtualDesktopWorkspaceManager.exe --run
```

must be supported.

The shortcuts must target the packaged executable rather than a development interpreter.

## Shortcut working directory

The shortcut must use a safe, deterministic working directory.

Do not depend on the user's current directory.

Do not use Desktop, Downloads, or another arbitrary user folder as an implicit working directory.

## Shortcut icon

Both shortcuts must use an application-owned icon.

Prefer:

```text
assets\VirtualDesktopWorkspaceManager.ico
```

or the equivalent packaged resource.

Use distinct visual variants for:

```text
Configure
Run Workspace
```

if practical, while retaining common application branding.

The icon must not be downloaded dynamically.

---

# 83D. SHORTCUT OWNERSHIP METADATA

The application must be able to distinguish its own shortcuts from unrelated Desktop shortcuts.

Use one or more of:

* deterministic shortcut names;
* explicit application-owned metadata;
* a stable application identifier;
* target/argument validation;
* installer ownership records.

Do NOT rely only on "this shortcut looks similar".

When repairing shortcuts:

```text
Inspect
→ identify owned shortcut
→ validate target
→ repair only owned shortcut
→ verify
```

Never replace or delete an unrelated shortcut with a similar name.

If two shortcuts with the same expected application-owned name exist:

* inspect their targets;
* identify the valid owned shortcut;
* report duplicates;
* remove/repair only those proven to belong to this application;
* never delete an ambiguous unrelated shortcut automatically.

---

# 83E. SETUP / APPLICATION / WORKSPACE STATE MACHINE

Document and enforce these states:

```text
NOT SET UP
    ↓
SETUP REQUIRED
    ↓
SET UP
    ↓
CONFIGURED
    ↓
READY TO RUN
    ↓
RUNNING
    ↓
COMPLETED / WARNING / FAILED / CANCELLED
```

Important:

```text
SET UP ≠ RUNNING
CONFIGURED ≠ RUNNING
GUI OPEN ≠ RUNNING
```

Opening the Configure shortcut must never transition the application into workspace execution.

Only an explicit Run Workspace operation may enter the execution state.

---

# 83F. FIRST SETUP MUST NOT EXECUTE A DEFAULT WORKSPACE

If no configuration exists, `setup.py` may create a safe initial configuration template.

For example:

```text
Development
    Desktop definitions: unassigned
    Applications: empty or disabled
```

If the project provides example application templates for Brave, Antigravity, SSMS, Postman, VS Code, Docker, or other applications:

* templates may be displayed;
* templates may assist configuration;
* paths may be discovered;
* no application may be launched;
* no desktop may be created;
* no window may be moved.

Do not make the default configuration silently executable.

---

# 83G. SETUP LOGGING

`setup.py` must create a setup log separate from normal workspace-operation logs.

Example:

```text
%APPDATA%\VirtualDesktopWorkspaceManager\logs\setup.log
```

Record:

* timestamp
* setup version
* Python version
* Windows version
* setup mode
* completed steps
* skipped steps
* warnings
* errors
* exit status

Do not record:

* passwords
* access tokens
* secrets
* browser profile data
* full sensitive command lines

---

# 83H. SETUP ACCEPTANCE TESTS

At minimum implement mock/unit tests for:

1. Windows version detection.
2. Architecture detection.
3. Python compatibility detection.
4. Existing `.venv` detection.
5. Missing `.venv` creation planning.
6. Dependency validation.
7. Existing configuration preservation.
8. Initial configuration creation.
9. Shortcut creation logic.
10. Shortcut idempotency.
11. Shortcut repair.
12. Unrelated shortcut protection.
13. Invalid setup-state handling.
14. Setup failure exit codes.
15. `--check` performs no modifications.
16. `setup.py` never calls the workspace execution engine.
17. `setup.py` never launches configured applications.
18. `setup.py` never performs real Virtual Desktop operations.

Where real Windows APIs are needed, use mocks/fakes for development validation.

Do not use the developer's real Desktop as a test fixture.

---

# 83I. SETUP SECURITY REVIEW

Create:

```text
docs/setup-security-review.md
```

Review at minimum:

| Risk | Required mitigation |
|---|---|
| Arbitrary dependency installation | Install only declared/pinned dependencies |
| Arbitrary command execution | Structured subprocess/API calls |
| Shortcut hijacking | Validate target and ownership |
| Path injection | Validate and normalize paths |
| Malicious configuration | Never execute configuration as code |
| Partial setup | Ordered/idempotent setup with failure reporting |
| Global Python pollution | Prefer project-local `.venv` |
| Accidental application launch | `setup.py` has no workspace execution path |
| Accidental desktop manipulation | No Virtual Desktop execution code in setup |
| Privilege escalation | No automatic elevation |
| Secret leakage | Redacted setup logs |
| Network dependency | Setup-only package retrieval; runtime remains offline |
| Duplicate setup artifacts | Idempotent checks |
| Unrelated shortcut deletion | Ownership verification |

---

# 83J. MANUAL SETUP FLOW

Document the expected user flow clearly:

```text
1. Open the project folder.
2. Run:
       py setup.py
3. Review setup result.
4. Setup creates/repairs the application environment and owned shortcuts.
5. Double-click:
       Virtual Desktop Workspace Manager — Configure
6. Configure and save the workspace.
7. Close the GUI if desired.
8. When ready, double-click:
       Virtual Desktop Workspace Manager — Run Workspace
```

At no point should setup itself execute the workspace.

---

# 83K. UPDATE / RE-RUN SETUP SAFETY

If the user runs `setup.py` again after an application update:

* preserve user configuration;
* preserve profiles;
* preserve logs;
* preserve backups;
* preserve user-selected executable paths;
* preserve desktop mappings unless migration requires review;
* update only application-owned setup artifacts;
* repair shortcuts when necessary;
* migrate configuration schema when required;
* never automatically execute the workspace.

If a schema migration could change behavior:

```text
Configuration migration available.

Your current configuration will be backed up before migration.

[Cancel] [Review] [Migrate]
```

Never silently discard unknown configuration fields.

---

# 83L. CLEAR SEPARATION OF SETUP AND RUNTIME COMMANDS

The final command contract must be:

```text
SETUP BOOTSTRAP
----------------
py setup.py
py setup.py --setup
py setup.py --repair
py setup.py --check
py setup.py --help
py setup.py --version

APPLICATION
-----------
VirtualDesktopWorkspaceManager.exe --config
VirtualDesktopWorkspaceManager.exe --run
VirtualDesktopWorkspaceManager.exe --dry-run
VirtualDesktopWorkspaceManager.exe --diagnostics
VirtualDesktopWorkspaceManager.exe --version
VirtualDesktopWorkspaceManager.exe --help
```

The source-mode equivalent may use:

```text
.venv\Scripts\python.exe main.py --config
.venv\Scripts\python.exe main.py --run
```

Do not confuse `setup.py` with `main.py`.

The filename `setup.py` refers to setup/bootstrap, not workspace execution.

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
* [ ] Root-level `setup.py` exists
* [ ] `setup.py` is setup/bootstrap only
* [ ] `setup.py` never executes the workspace
* [ ] `setup.py` never launches configured applications
* [ ] `setup.py` never manipulates real Virtual Desktops
* [ ] `setup.py` setup is idempotent
* [ ] `setup.py --check` is non-destructive
* [ ] `setup.py --repair` repairs only application-owned setup artifacts
* [ ] Project-local virtual environment is supported where appropriate
* [ ] Dependencies are declared and pinned
* [ ] Setup state is separate from workspace configuration
* [ ] Setup logging exists
* [ ] Setup security review exists
* [ ] Source-mode shortcuts are supported
* [ ] Packaged-mode shortcuts are supported
* [ ] Setup failure returns a non-zero exit code
* [ ] Existing user configuration is preserved during setup/update
* [ ] Re-running setup does not duplicate shortcuts
* [ ] Setup-time network use is limited to declared dependency installation
* [ ] Runtime remains offline-first


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

# 148B. SETUP.PY ACCEPTANCE CHECKLIST

Before declaring the project complete:

* [ ] Root-level `setup.py` exists.
* [ ] `setup.py` is the single supported setup authority.
* [ ] `py setup.py` performs complete setup.
* [ ] `--setup`, `--repair`, `--check`, `--help`, and `--version` are supported.
* [ ] `setup.py` never runs the workspace.
* [ ] `setup.py` never launches configured applications.
* [ ] `setup.py` never manipulates real Virtual Desktops.
* [ ] `setup.py` never enables startup automation.
* [ ] `setup.py` never silently elevates.
* [ ] Windows 10/11 compatibility is checked.
* [ ] Python compatibility is checked.
* [ ] Project-local `.venv` is used.
* [ ] Dependencies are declared and reproducible.
* [ ] Dependencies are verified after installation.
* [ ] Configuration persists outside transient source state.
* [ ] Existing valid configuration is preserved.
* [ ] Schema migration is backed up and validated.
* [ ] Setup is idempotent.
* [ ] Partial setup can be safely resumed.
* [ ] Setup state and logs are written.
* [ ] Configure shortcut is created.
* [ ] Run Workspace shortcut is created.
* [ ] Both shortcuts use explicit command-line modes.
* [ ] Both shortcuts use deterministic working directories.
* [ ] Both shortcuts use application-owned icons.
* [ ] Re-running setup does not duplicate shortcuts.
* [ ] Repair affects only application-owned shortcuts.
* [ ] Unrelated Desktop shortcuts are preserved.
* [ ] `--check` is non-destructive.
* [ ] Setup failures return non-zero exit codes.
* [ ] Missing Python is reported rather than silently installed.
* [ ] Runtime does not require setup-time network access.
* [ ] Setup security review is complete.
* [ ] Setup tests are mocked and do not modify the real workspace.
* [ ] Antigravity has not executed `setup.py` during development.
* [ ] Antigravity has not created real Desktop shortcuts during development.
* [ ] Antigravity has not launched the application during development.

---

# 149. REQUIRED DELIVERABLES

Provide:

## Application

Complete production-oriented source code.

## Setup / Bootstrap

Provide a complete root-level `setup.py` that performs the full Windows 10/11 setup workflow, including environment creation/reuse, declared dependency installation, configuration initialization/preservation, setup logging/state, and creation/repair of both required Desktop shortcuts.

`setup.py` must stop after setup and must never execute the workspace.


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

## Setup / Bootstrap

The project must include:

* `setup.py`
* documented setup modes
* idempotent environment setup
* dependency verification
* configuration-directory initialization
* setup-state handling
* setup logging
* shortcut creation/repair
* setup acceptance tests
* `docs/setup-security-review.md`

`setup.py` must be setup/bootstrap only and must never execute the workspace.

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
16. `setup.py` behavior and supported setup commands
17. Whether `setup.py` was executed or only statically reviewed
18. Whether real Desktop shortcuts were created during validation
19. Dependency installation status
20. Manual run instructions
17. Configuration location
18. Log location
19. Diagnostic instructions
20. Remaining issues, if any
21. `setup.py` setup behavior and supported setup commands
22. Whether setup was executed or only statically reviewed
23. Whether shortcuts were created during validation
24. Setup dependency installation status
25. Setup/security review status

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
36. **NEVER execute `setup.py` during development merely to prove setup works.**
37. **NEVER treat `setup.py` as the workspace execution entry point.**
38. **NEVER let `setup.py` launch configured applications or manipulate Virtual Desktops.**
39. **NEVER create the real Desktop shortcuts during Google Antigravity development unless I explicitly authorize running the setup process.**
40. **NEVER let setup overwrite valid user configuration without backup and validation.**
41. **NEVER let setup remove unrelated Desktop shortcuts.**
42. **NEVER require global Python package installation when a project-local environment is sufficient.**

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
16. `setup.py` is a setup/bootstrap entry point, not a workspace execution entry point.
17. `py setup.py` must not launch the GUI after setup unless explicitly designed as a separate, opt-in command; default behavior is setup completion and exit.
18. `setup.py --check` must be non-destructive.
19. `setup.py --repair` may modify only application-owned setup artifacts and must not execute workspace actions.
20. Setup must preserve user configuration, profiles, logs, and backups.
21. Setup must use the same application-owned shortcut identity rules defined in this specification.
22. The runtime application must load the same persisted configuration regardless of whether it is started from the Configure shortcut, Run shortcut, packaged executable, or source-mode entry point.

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
Create the installer/packaging logic and the root-level `setup.py` setup/bootstrap logic for these shortcuts, but do not execute `setup.py` or create/click the real shortcuts on my Desktop during development.

`setup.py` must be complete enough to set up the source-mode application on a user's Windows 10/11 system when the user explicitly runs it.

`setup.py` must:
* detect and validate Windows/Python compatibility;
* create/use the project-local environment where appropriate;
* install only declared dependencies;
* initialize user-level application directories;
* validate/preserve existing configuration;
* create or repair the two application-owned Desktop shortcuts;
* verify setup;
* produce a setup report and exit;
* never launch the application;
* never launch the workspace;
* never manipulate real Virtual Desktops;
* never launch configured applications.

Do not execute `setup.py` during Google Antigravity development merely because the prompt asks for it to be created.

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
Do not execute `setup.py` as part of development.
Do not create the real Desktop shortcuts during development.
Do not perform real setup changes on my Windows installation during development.
Do not modify my Windows workspace.

Do not perform real workspace execution.

Every functional UI control must connect to real application logic.

Every unsupported feature must be clearly identified.

Every important Windows API limitation must be documented.

Every safety-sensitive action must require the appropriate explicit user authorization.

When implementation, static validation, and safe mocked tests are complete, stop.

Do not execute setup unless I explicitly authorize setup.
Do not execute the application unless I explicitly authorize the application.
Do not execute the workspace unless I explicitly authorize the workspace.
Report the project status.

Then wait.

**DO NOT RUN THE APPLICATION.**

**DO NOT RUN THE WORKSPACE.**

**WAIT FOR MY EXPLICIT INSTRUCTION BEFORE EXECUTING ANY REAL WORKSPACE OPERATION.**



---

# 100. REVISION NOTES FOR THIS VERSION

This revision intentionally strengthens the original specification rather than removing its detailed Windows engineering requirements.

Major improvements include:

- explicit objective, audience, scope, tone, deliverables, and success criteria;
- product-level UX principles;
- stronger visual hierarchy;
- improved Dashboard information architecture;
- deliberate empty/loading/error/success states;
- unsaved-change protection;
- configuration diff/review;
- application discovery wizard;
- application detail drawer;
- desktop mapping UX;
- keyboard/accessibility requirements;
- responsive desktop behavior;
- search/filter/sort requirements;
- notification/toast behavior;
- operation history;
- recovery center;
- support bundle generation;
- capability matrices;
- explicit authorization boundaries;
- manual/assisted/automatic automation modes;
- state machines;
- action classification;
- plan immutability;
- operation scope;
- provider contract testing;
- failure injection;
- fuzz/robustness testing;
- UI testing;
- performance testing;
- internationalization readiness;
- clearer setup/runtime separation;
- release-readiness criteria;
- stronger user-trust requirements.

The original detailed sections below remain mandatory unless superseded by an explicit higher-priority safety or clarification rule above.

---

# 101. REQUIREMENT COMPLETENESS RULE

Do not optimize for merely producing a large amount of code.

The goal is a **coherent product** in which:

```text
UI
↓
Domain Model
↓
State Discovery
↓
Planning
↓
Authorization
↓
Execution
↓
Verification
↓
Reporting
↓
Persistence
```

forms one consistent system.

A feature is incomplete if:

- its UI exists but its logic does not;
- its logic exists but it cannot be configured;
- it can execute but cannot be tested safely;
- it changes state without verification;
- it is not represented in diagnostics/logging;
- it is not represented in documentation;
- it violates the safety boundary.

---

# 102. REQUIREMENT QUALITY GATE

Before implementing any feature, classify it as:

```text
READ-ONLY
CONFIGURATION
WINDOWS-STATE-CHANGING
SETUP
DIAGNOSTIC
```

Then determine:

- authorization requirement;
- rollback/recovery behavior;
- verification method;
- logging requirement;
- mock/test strategy;
- UI feedback;
- error behavior.

Do not implement state-changing behavior directly inside UI callbacks without going through the application/domain layer.

---

# 103. PRODUCT COMPLETION DEFINITION

"Complete" means:

```text
Implemented
+
Integrated
+
Persisted
+
Validated
+
Tested safely
+
Documented
+
Accessible
+
Recoverable
+
Traceable
```

A visual control alone does not constitute implementation.

A function that works only on the developer's machine does not constitute production readiness.

A feature that cannot be safely mocked does not meet the architecture requirement.

---

# 104. UX COMPLETION DEFINITION

The UI is complete only when each major workflow has:

```text
Entry
→ Guidance
→ Action
→ Progress
→ Result
→ Recovery/Next Step
```

This applies to:

- first run;
- adding applications;
- editing workspaces;
- mapping desktops;
- importing;
- restoring;
- dry run;
- launch;
- sync;
- diagnostics;
- setup;
- error recovery.

---

# 105. FINAL USER-TRUST TEST

Before completion, ask:

### Can the user tell what will happen?

If not, improve the plan/confirmation UI.

### Can the user tell what happened?

If not, improve reporting/history/logs.

### Can the user stop future actions?

If not, improve cancellation.

### Can the user recover configuration?

If not, improve backups/recovery.

### Can the user understand why something failed?

If not, improve error UX.

### Can the user use the product without knowing Windows internals?

If not, improve progressive disclosure.

### Can the user verify that a successful action really succeeded?

If not, improve verification.

### Can the user safely configure the product without accidentally executing it?

If not, fix the authorization boundary.

---

# 106. FINAL ANTIGRAVITY STOP CONDITION

Once the project reaches the state below:

```text
Source complete
Documentation complete
Tests created
Static validation complete
Mock validation complete
Security review complete
Traceability complete
```

STOP.

Do not continue into:

```text
setup.py execution
real installation
GUI launch
workspace execution
Desktop shortcut creation
Virtual Desktop manipulation
application launch
```

unless the user explicitly authorizes the relevant action.

**The correct final state during this development phase is:**

```text
READY FOR USER AUTHORIZATION
```

not:

```text
RUNNING
```
