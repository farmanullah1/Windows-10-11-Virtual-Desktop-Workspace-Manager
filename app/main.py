"""
Application entry point and CLI runner for Virtual Desktop Workspace Manager.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

# Ensure root package directory is in sys.path and remove app/ to avoid shadowing stdlib logging
script_dir = str(Path(__file__).resolve().parent)
while script_dir in sys.path:
    sys.path.remove(script_dir)

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.manager import WorkspaceManager
from app.configuration.config_store import ConfigStore
from app.configuration.validator import ConfigValidator
from app.logging.logger import setup_logging, get_logger
from app.services.shortcut_service import ShortcutService
from app.services.single_instance import SingleInstanceGuard
from app.ui.app_window import MainWindow


def parse_args():
    parser = argparse.ArgumentParser(description="Windows Virtual Desktop Workspace Manager")
    parser.add_argument("--config", action="store_true", help="Open configuration & management GUI (default)")
    parser.add_argument("--run", action="store_true", help="Execute the active workspace profile (Run Workspace entry point)")
    parser.add_argument("--minimized", action="store_true", help="Start application minimized to tray/taskbar")
    parser.add_argument("--autolaunch", action="store_true", help="Execute active workspace if autolaunch is permitted")
    parser.add_argument("--dry-run", action="store_true", help="Run workspace dry run preview in console and exit")
    parser.add_argument("--sync", action="store_true", help="Run workspace synchronization non-interactively and exit")
    parser.add_argument("--profile", type=str, default=None, help="Target profile ID or name to activate")
    parser.add_argument("--create-shortcuts", action="store_true", help="Create owned desktop shortcuts (Configure and Run Workspace)")
    parser.add_argument("--remove-shortcuts", action="store_true", help="Remove owned desktop shortcuts cleanly")
    parser.add_argument("--health-check", action="store_true", help="Run 8-point system diagnostic health check and exit")
    parser.add_argument("--no-prompt", action="store_true", help="Skip launch confirmation prompt when running with --run")
    parser.add_argument("--headless", action="store_true", help="Execute in headless mode without GUI popups")
    return parser.parse_args()


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    args = parse_args()

    # Load configuration
    store = ConfigStore()
    config = store.load()

    # Initialize Logger
    setup_logging(
        log_dir=config.logging.log_dir or None,
        log_level=config.logging.log_level,
        retention_days=config.logging.log_retention_days,
    )
    logger = get_logger()
    logger.info("Virtual Desktop Workspace Manager initialized.")

    manager = WorkspaceManager(config_store=store)

    # Health check diagnostics (Section 113)
    if args.health_check:
        from app.services.diagnostics_service import DiagnosticsService
        diag = DiagnosticsService(
            config=manager.config,
            desktop_provider=manager.desktop_provider,
            process_provider=manager.process_provider,
            window_provider=manager.window_provider,
        )
        print(diag.format_health_check_summary())
        sys.exit(0)

    # 1. Shortcut management commands
    if args.create_shortcuts:
        svc = ShortcutService()
        res = svc.create_desktop_shortcuts()
        print(f"Created desktop shortcuts: Configure={res['config']}, Run={res['run']}")
        sys.exit(0)

    if args.remove_shortcuts:
        svc = ShortcutService()
        res = svc.remove_desktop_shortcuts()
        print(f"Removed desktop shortcuts: Configure={res['config']}, Run={res['run']}")
        sys.exit(0)

    # 2. Activate specific profile if requested via CLI
    if args.profile:
        for p in manager.config.profiles:
            if p.id == args.profile or p.name.lower() == args.profile.lower():
                manager.config.general.active_profile_id = p.id
                manager.save_config()
                break

    # 3. Non-interactive CLI Dry Run
    if args.dry_run:
        result = manager.dry_run()
        print(result.format_preview())
        sys.exit(0)

    # 4. Non-interactive CLI Sync
    if args.sync:
        report = manager.sync_workspace()
        print(report.summary_text())
        sys.exit(0 if report.success else 1)

    # 5. Dedicated "Run Workspace" entry point (--run)
    if args.run:
        # Validate configuration before execution (Section 148A Test 5)
        try:
            ConfigValidator.validate(manager.config)
        except Exception as val_err:
            logger.error("Configuration validation failed before workspace execution: %s", val_err)
            print(f"Error: Invalid configuration - {val_err}")
            sys.exit(1)

        active_prof = manager.config.get_active_profile()
        logger.info("Executing Run Workspace entry point for profile: %s", active_prof.name)

        # Check confirmation policy if confirm_before_execution is enabled and not headless
        should_confirm = getattr(config.general, "confirm_before_execution", True)
        if should_confirm and not args.no_prompt and not args.headless:
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                confirmed = messagebox.askyesno(
                    "Run Workspace Confirmation",
                    f"Launch Workspace profile '{active_prof.name}'?\n\n"
                    f"This will launch missing applications and assign windows to their configured virtual desktops.",
                    parent=root
                )
                root.destroy()
                if not confirmed:
                    logger.info("Workspace execution cancelled by user.")
                    print("Execution cancelled by user.")
                    sys.exit(0)
            except Exception as ex:
                logger.warning("GUI confirmation dialog unavailable (%s), proceeding with CLI run.", ex)

        report = manager.launch_workspace()
        print(report.summary_text())
        sys.exit(0 if report.success else 1)

    # 6. Auto-launch handling: Only if BOTH CLI flag and user setting allow it
    if args.autolaunch and config.general.auto_launch_workspace:
        logger.info("Executing workspace autolaunch as configured in startup settings.")
        manager.launch_workspace()

    # 7. Default / --config: Launch Configuration GUI with Single-Instance enforcement
    guard = SingleInstanceGuard()
    if not guard.acquire():
        logger.warning("Virtual Desktop Workspace Manager is already running.")
        print("Virtual Desktop Workspace Manager is already running.")
        sys.exit(0)

    try:
        app = MainWindow(manager, start_minimized=args.minimized)
        app.mainloop()
    finally:
        guard.release()


if __name__ == "__main__":
    main()


