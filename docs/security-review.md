# Security and Safety Review

## 1. Security Architecture Principles

The **Windows Virtual Desktop Workspace Manager** operates under a strict principle of least privilege, non-destructive execution, and local-only data boundaries.

---

## 2. Privileges and Elevation

* **Standard User Account Operability**: The manager executes entirely within standard Windows user privileges (Medium Integrity Level).
* **No Automatic Elevation**: The application never invokes `RunAs`, never prompts for UAC elevation automatically, and never executes elevated helper processes.
* **Registry Boundaries**: All registry writes (such as optional Windows login startup registration) are restricted exclusively to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`. No system-wide `HKEY_LOCAL_MACHINE` modifications are performed.

---

## 3. Process Execution Safety

* **No Shell Execution**: All process launches through `ProcessService` use `subprocess.Popen` with argument arrays directly passed to the Windows API `CreateProcessW`. The `shell=True` flag is strictly forbidden across the codebase to prevent command injection.
* **Argument Sanitization**: Arguments configured for applications are safely tokenized via `shlex.split(posix=False)` and validated by `ConfigValidator`. Risky shell characters (e.g., pipes `|`, command chaining `&`, redirection `>`, command substitution `` ` ``, `$`) trigger configuration validation warnings.
* **Process Termination Policy**: The manager **never** terminates or kills processes. Even during an Emergency Stop (`STOP` button), the manager simply halts subsequent launch and window movement phases without issuing `TerminateProcess` or `taskkill`.

---

## 4. Filesystem Boundaries

* **Restricted Application State**: All runtime state, logs, markers, and configurations are stored strictly within the user's roaming application data folder:

  ```text
  %APPDATA%\VirtualDesktopWorkspaceManager\
  ├── workspace.json
  ├── workspace.backup.json
  ├── backups\
  └── logs\
  ```

* **No Unsolicited File Deletion**: The manager never deletes files outside of its own configured log retention cleanup (`workspace_YYYYMMDD.log` older than the user-configured retention limit).
* **Developer Data Immunity**: The manager never touches source code, git repositories, browser profile caches, Docker data volumes, or database files.

---

## 5. Network Access and Privacy

* **Zero Network Requests**: The application is completely offline. No telemetry, analytics, update checks, or remote logging are implemented.
* **Zero Cloud Storage**: All workspace profiles, application definitions, and desktop indices remain exclusively on the local computer.

---

## 6. Logging and Diagnostics Redaction

* **Automatic Masking**: The `DiagnosticsService` scans all text before rendering diagnostic reports or writing debug records, automatically masking:
  * Tokens, authorization headers, passwords, and API keys matching `(token|auth|password|secret|bearer)=...`.
  * Usernames within filesystem paths (replaced with `<USER>`).
* **Memory Buffer Bounds**: The live UI logging panel uses a bounded in-memory ring buffer (maximum 2,000 records) to prevent unbounded memory growth.

---

## 7. Safety Threat Model & Mitigations

| Threat | Impact | Mitigation Strategy |
| --- | --- | --- |
| Command Injection | Arbitrary command execution via configured arguments | Safe tokenized argument passing; `shell=True` prohibited; validation warnings on shell syntax |
| Configuration Corruption | Loss of user workspace settings on sudden crash | Atomic file writes via temporary files and `shutil.move`; automatic backup preservation |
| Runaway Process Spawning | System resource exhaustion from duplicate launches | Process and window pre-detection; reusable instance policies; configurable launch delays |
| Accidental Desktop Destruction | Loss of open work on user virtual desktops | Manager strictly creates or reuses desktops; desktop deletion code is not exposed to automation |
| Accidental App Uninstallation | Loss of software | "Remove" actions explicitly state and enforce that only configuration records are deleted |
