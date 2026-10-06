"""
Application entry point and CLI runner for Virtual Desktop Workspace Manager.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

# Ensure root package directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.manager import WorkspaceManager
from app.configuration.config_store import ConfigStore
from app.logging.logger import setup_logging, get_logger
from app.ui.app_window import MainWindow


def parse_args():
    parser = argparse.ArgumentParser(description="Windows Virtual Desktop Workspace Manager")
    parser.add_argument("--minimized", action="store_true", help="Start application minimized to tray/taskbar")
    parser.add_argument("--autolaunch", action="store_true", help="Execute active workspace if autolaunch is permitted")
    parser.add_argument("--dry-run", action="store_true", help="Run workspace dry run preview in console and exit")
    parser.add_argument("--sync", action="store_true", help="Run workspace synchronization non-interactively")
    parser.add_argument("--profile", typestr=str, default=None, help="Target profile ID or name to activate")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load configuration
    store = ConfigStore()
    config = store.load()

    # Initialize Logger
    setup_logging(
        log_dir=config.logging.log_dir or None,
        log_level=config.logging.log_level,
        retention_days=config.logging.log_retention_days
    )
    logger = get_logger()
    logger.info("Virtual Desktop Workspace Manager initialized.")

    manager = WorkspaceManager(config_store=store)

    # Activate specific profile if requested via CLI
    if args.profile:
        for p in manager.config.profiles:
            if p.id == args.profile or p.name.lower() == args.profile.lower():
                manager.config.general.active_profile_id = p.id
                manager.save_config()
                break

    # Non-interactive CLI Dry Run
    if args.dry_run:
        result = manager.dry_run()
        print(result.format_preview())
        sys.exit(0)

    # Non-interactive CLI Sync
    if args.sync:
        report = manager.sync_workspace()
        print(report.summary_text())
        sys.exit(0)

    # Auto-launch handling: Only if BOTH CLI flag and user setting allow it
    if args.autolaunch and config.general.auto_launch_workspace:
        logger.info("Executing workspace autolaunch as configured in startup settings.")
        manager.launch_workspace()

    # Launch GUI
    app = MainWindow(manager, start_minimized=args.minimized)
    app.mainloop()


if __name__ == "__main__":
    main()
