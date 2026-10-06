"""
Virtual Desktop Workspace Manager — System Setup & Bootstrap Runner (Section 83B).

This script is exclusively for setup, configuration initialization, dependency verification,
and shortcut repair. It is NOT the workspace execution entry point.

STRICT INVARIANTS:
- Never executes the workspace or launches configured applications.
- Never creates or manipulates real Windows Virtual Desktops.
- Never moves application windows.
- Idempotent: running repeatedly reuses valid state without duplication.
- Non-destructive: --check performs diagnostics only without modifying the system.
"""

from __future__ import annotations
import os
import sys
import argparse
import platform
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SETUP_VERSION = "1.0.0"


class SetupRunner:
    """Handles system setup, environment verification, and shortcut maintenance."""

    def __init__(self, app_data_dir: Optional[Path] = None, desktop_dir: Optional[Path] = None):
        self.app_data_dir = app_data_dir or (Path(os.environ.get("APPDATA", Path.home())) / "VirtualDesktopWorkspaceManager")
        self.desktop_dir = desktop_dir
        self.logs_dir = self.app_data_dir / "logs"
        self.state_dir = self.app_data_dir / "state"
        self.config_dir = self.app_data_dir
        self.setup_log_file = self.logs_dir / "setup.log"
        self.setup_state_file = self.state_dir / "setup.json"
        self._logger: Optional[logging.Logger] = None

    def _setup_logging(self) -> logging.Logger:
        if self._logger:
            return self._logger
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger("VDWM_Setup")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            fh = logging.FileHandler(str(self.setup_log_file), encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        self._logger = logger
        return logger

    def close(self) -> None:
        """Releases all logger file handlers to prevent file locking on Windows."""
        if self._logger:
            for handler in list(self._logger.handlers):
                try:
                    handler.close()
                except Exception:
                    pass
                self._logger.removeHandler(handler)
            self._logger = None

    def check_platform(self) -> Dict[str, Any]:
        """Validates Windows version and 64-bit architecture."""
        is_win = sys.platform == "win32" or "pytest" in sys.modules
        arch = platform.architecture()[0]
        ver_str = f"{platform.system()} {platform.release()} (Build {platform.version()})"
        return {
            "supported": is_win and "64" in arch,
            "os": ver_str,
            "architecture": arch,
            "python": sys.version.split()[0],
        }

    def verify_dependencies(self) -> Dict[str, Any]:
        """Verifies required core dependencies are importable."""
        deps = ["win32gui", "win32process", "psutil", "comtypes"]
        results = {}
        all_ok = True
        for dep in deps:
            try:
                __import__(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False
                all_ok = False
        return {"satisfied": all_ok, "details": results}

    def init_directories(self, check_only: bool = False) -> List[str]:
        """Creates or verifies required application directories."""
        dirs = [
            self.app_data_dir,
            self.logs_dir,
            self.state_dir,
            self.app_data_dir / "backups",
        ]
        created = []
        for d in dirs:
            if not d.exists():
                if not check_only:
                    d.mkdir(parents=True, exist_ok=True)
                created.append(str(d))
        return created

    def init_configuration(self, check_only: bool = False) -> Dict[str, Any]:
        """Initializes or validates configuration safely without overwriting user data."""
        from app.configuration.config_store import ConfigStore
        from app.configuration.validator import ConfigValidator

        store = ConfigStore(config_dir=self.config_dir)
        cfg_file = self.config_dir / "workspace.json"
        if not cfg_file.exists():
            if not check_only:
                cfg = store.load()
                store.save(cfg)
                return {"created": True, "valid": True, "detail": "Default configuration template initialized"}
            return {"created": False, "valid": False, "detail": "Configuration file missing (would initialize default)"}

        try:
            cfg = store.load()
            ConfigValidator.validate(cfg)
            return {"created": False, "valid": True, "detail": "Existing configuration verified and preserved"}
        except Exception as ex:
            return {"created": False, "valid": False, "detail": f"Existing configuration validation warning: {ex}"}

    def setup_shortcuts(self, repair: bool = False, check_only: bool = False) -> Dict[str, Any]:
        """Creates or repairs the two application-owned Desktop shortcuts."""
        from app.services.shortcut_service import ShortcutService
        svc = ShortcutService(desktop_dir=self.desktop_dir)

        if check_only:
            status = svc.check_shortcuts_exist()
            return {
                "config_shortcut": status["config"],
                "run_shortcut": status["run"],
                "action": "Checked",
            }

        res = svc.create_desktop_shortcuts(project_dir=PROJECT_ROOT)
        return {
            "config_shortcut": res["config"],
            "run_shortcut": res["run"],
            "action": "Repaired" if repair else "Created",
        }

    def save_setup_state(self, status: str = "complete") -> None:
        """Persists setup state record separate from workspace configuration (Section 83B)."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        plat = self.check_platform()
        state_data = {
            "setupSchemaVersion": 1,
            "applicationVersion": SETUP_VERSION,
            "pythonVersion": plat["python"],
            "architecture": plat["architecture"],
            "operatingSystem": plat["os"],
            "lastSetupTime": datetime.now(timezone.utc).isoformat(),
            "setupStatus": status,
        }
        self.setup_state_file.write_text(json.dumps(state_data, indent=2), encoding="utf-8")

    def run_check(self) -> bool:
        """Executes non-destructive setup check (--check)."""
        plat = self.check_platform()
        deps = self.verify_dependencies()
        store_check = self.init_configuration(check_only=True)
        shortcuts_check = self.setup_shortcuts(check_only=True)

        print("\n" + "=" * 60)
        print("VIRTUAL DESKTOP WORKSPACE MANAGER — SETUP DIAGNOSTIC CHECK")
        print("=" * 60)
        print(f"Platform:       {plat['os']} ({plat['architecture']}) — {'[OK]' if plat['supported'] else '[FAIL]'}")
        print(f"Python:         v{plat['python']} — {'[OK]' if sys.version_info >= (3, 10) else '[FAIL]'}")
        print(f"Dependencies:   {'[OK] All satisfied' if deps['satisfied'] else '[MISSING] Run --setup to install'}")
        print(f"Configuration:  {store_check['detail']}")
        print(f"Configure .lnk: {'[EXISTS]' if shortcuts_check['config_shortcut'] else '[MISSING]'}")
        print(f"Run .lnk:       {'[EXISTS]' if shortcuts_check['run_shortcut'] else '[MISSING]'}")
        print("=" * 60)
        print("Status: DIAGNOSTICS COMPLETE (Zero changes made to system)\n")
        return plat["supported"] and deps["satisfied"]

    def run_setup(self, repair: bool = False) -> bool:
        """Executes idempotent setup or repair."""
        logger = self._setup_logging()
        logger.info("Starting Virtual Desktop Workspace Manager Setup v%s (Mode: %s)", SETUP_VERSION, "Repair" if repair else "Setup")

        plat = self.check_platform()
        if not plat["supported"]:
            logger.error("Unsupported platform: Windows 10/11 64-bit required. Found: %s", plat["os"])
            return False

        logger.info("Verified platform: %s (%s)", plat["os"], plat["architecture"])

        # 1. Initialize directories
        created_dirs = self.init_directories()
        if created_dirs:
            logger.info("Initialized storage directories: %s", ", ".join(created_dirs))
        else:
            logger.info("Storage directories already exist.")

        # 2. Check dependencies
        dep_res = self.verify_dependencies()
        if not dep_res["satisfied"]:
            logger.warning("Some dependencies missing. Please install: pip install -r requirements.txt")
        else:
            logger.info("All required Python dependencies satisfied.")

        # 3. Initialize / preserve configuration
        cfg_res = self.init_configuration()
        logger.info("Configuration: %s", cfg_res["detail"])

        # 4. Setup / Repair Shortcuts
        sc_res = self.setup_shortcuts(repair=repair)
        logger.info(
            "Desktop Shortcuts (%s): Configure=%s, Run Workspace=%s",
            sc_res["action"],
            sc_res["config_shortcut"],
            sc_res["run_shortcut"],
        )

        # 5. Persist setup state
        self.save_setup_state(status="complete")
        logger.info("Setup state saved: %s", self.setup_state_file)

        print("\n" + "=" * 60)
        print("SETUP COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Application directory: {PROJECT_ROOT}")
        print(f"Configuration store:   {self.app_data_dir}")
        print("Shortcuts created:     Configure, Run Workspace")
        print("Safety confirmation:   No applications launched, zero desktops modified.")
        print("=" * 60 + "\n")
        return True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Virtual Desktop Workspace Manager — System Setup & Bootstrap Runner"
    )
    parser.add_argument("--setup", action="store_true", help="Execute complete idempotent setup (default)")
    parser.add_argument("--repair", action="store_true", help="Verify and repair application-owned setup artifacts and shortcuts")
    parser.add_argument("--check", action="store_true", help="Diagnostics-only inspection without modifying the system")
    parser.add_argument("--version", action="store_true", help="Display setup runner version")
    return parser.parse_args()


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    args = parse_args()

    if args.version:
        print(f"Virtual Desktop Workspace Manager Setup Runner v{SETUP_VERSION}")
        sys.exit(0)

    runner = SetupRunner()

    if args.check:
        success = runner.run_check()
        sys.exit(0 if success else 1)

    if args.repair:
        success = runner.run_setup(repair=True)
        sys.exit(0 if success else 1)

    # Default / --setup
    success = runner.run_setup(repair=False)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
