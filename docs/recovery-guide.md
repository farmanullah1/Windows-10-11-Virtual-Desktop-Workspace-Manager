# Recovery & Troubleshooting Guide

## 1. Overview

The **Virtual Desktop Workspace Manager** is designed with self-healing, non-destructive recovery mechanisms. It never automatically executes destructive repairs or modifies unmanaged state.

---

## 2. Interrupted Operation Recovery (Section 46)

If the computer loses power, restarts, or crashes during a workspace operation:

1. **Automatic Detection:** On subsequent launch, the manager checks for `operation_in_progress.marker` in the configuration directory.
2. **Crash Recovery Dialog:** The user is presented with a non-intrusive prompt:
   ```text
   Notice: A previous workspace operation ('Launch') started at 2026-10-08 10:42:15 may not have completed cleanly.

   Would you like to run 'Sync Workspace' now to reconcile your state?
   ```
3. **Reconciliation:** Clicking **Yes** initiates `Sync Workspace`, which scans currently open windows and safely moves them to their intended desktop without relaunching applications.
4. **Clean Exit:** The crash marker is automatically unlinked.

---

## 3. Configuration Backup & Restore (Section 47)

### 3.1 Automated Backups
Every save operation creates:
1. `workspace.backup.json`: A shadow copy of the last working configuration.
2. `backups/workspace_YYYYMMDD_HHMMSS.backup.json`: A timestamped historical snapshot (retaining the 5 most recent snapshots).

### 3.2 Manual Restoration
If `workspace.json` becomes corrupt or invalid:
1. Open File Explorer to `%APPDATA%\VirtualDesktopWorkspaceManager`.
2. Locate the `backups` directory.
3. Choose the desired timestamped backup file.
4. Copy and rename it to `workspace.json`.
5. Restart the manager.

---

## 4. Emergency STOP Recovery

When the user clicks **■ STOP** during an active execution:
1. The active execution plan halts immediately after completing its current in-flight atomic step.
2. No processes are terminated.
3. Windows that have already been moved remain on their assigned desktop.
4. Applications that were already launched continue running normally.
5. To resume or finish arranging your workspace, click **⟳ Sync Workspace**.

---

## 5. Resolving Virtual Desktop Mismatches

If Windows updates or user actions change the number of Virtual Desktops:
1. Navigate to the **Virtual Desktops** tab.
2. Inspect the **Status** column for `⚠ Not Created Yet` indicators.
3. Click **+ Create Missing Desktop** or run **⟳ Sync Workspace** to re-align desktop numbers with configured targets.
