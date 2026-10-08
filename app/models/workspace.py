"""
Workspace data models and configurations.
"""

from __future__ import annotations
import os
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class WindowPolicy(str, Enum):
    """Policy for selecting which window(s) to move when multiple windows match."""
    MAIN_ONLY = "main"
    ALL_MATCHING = "all"
    TITLE_CONTAINS = "title_contains"
    TITLE_REGEX = "title_regex"
    PROCESS_ONLY = "process"


class LaunchMode(str, Enum):
    """Controls how and whether an application is launched."""
    LAUNCH_IF_MISSING = "launch_if_missing"
    ALWAYS_LAUNCH = "always_launch"
    REUSE_ONLY = "reuse_only"


class WindowSnap(str, Enum):
    """Layout snapping / tiling position for a window."""
    DEFAULT = "default"        # Keep original geometry
    MAXIMIZE = "maximize"      # Full screen on target monitor
    MINIMIZE = "minimize"      # Minimized
    LEFT_HALF = "left_half"    # Left 50%
    RIGHT_HALF = "right_half"  # Right 50%
    TOP_HALF = "top_half"      # Top 50%
    BOTTOM_HALF = "bottom_half"# Bottom 50%
    CENTER = "center"          # Centered with 75% width/height
    CUSTOM = "custom"          # Explicit coordinates [x, y, w, h]


@dataclass
class AppConfig:
    """Configuration for an individual managed application."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    executable: str = ""
    arguments: str = ""
    desktop: int = 1
    enabled: bool = True
    launch_mode: str = LaunchMode.LAUNCH_IF_MISSING.value
    move_existing_window: bool = True
    window_policy: str = WindowPolicy.MAIN_ONLY.value
    title_pattern: str = ""
    launch_delay_ms: int = 1000
    window_timeout_ms: int = 15000
    process_names: List[str] = field(default_factory=list)
    monitor_index: int = 0
    window_snap: str = WindowSnap.DEFAULT.value
    custom_rect: Optional[List[int]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AppConfig:
        clean = dict(data)
        # Backwards compatibility: handle old boolean flag if present
        if "launchIfMissing" in clean and "launch_mode" not in clean:
            clean["launch_mode"] = (
                LaunchMode.LAUNCH_IF_MISSING.value if clean["launchIfMissing"]
                else LaunchMode.REUSE_ONLY.value
            )
            clean.pop("launchIfMissing", None)
        if "moveExistingWindow" in clean and "move_existing_window" not in clean:
            clean["move_existing_window"] = clean.pop("moveExistingWindow")
        if "windowPolicy" in clean and "window_policy" not in clean:
            clean["window_policy"] = clean.pop("windowPolicy")
        if "launchDelayMs" in clean and "launch_delay_ms" not in clean:
            clean["launch_delay_ms"] = clean.pop("launchDelayMs")
        if "windowTimeoutMs" in clean and "window_timeout_ms" not in clean:
            clean["window_timeout_ms"] = clean.pop("windowTimeoutMs")
        if "processNames" in clean and "process_names" not in clean:
            clean["process_names"] = clean.pop("processNames")
        if "titlePattern" in clean and "title_pattern" not in clean:
            clean["title_pattern"] = clean.pop("titlePattern")
        if "monitorIndex" in clean and "monitor_index" not in clean:
            clean["monitor_index"] = clean.pop("monitorIndex")
        if "windowSnap" in clean and "window_snap" not in clean:
            clean["window_snap"] = clean.pop("windowSnap")
        if "customRect" in clean and "custom_rect" not in clean:
            clean["custom_rect"] = clean.pop("customRect")

        allowed_keys = {
            "id", "name", "executable", "arguments", "desktop", "enabled",
            "launch_mode", "move_existing_window", "window_policy",
            "title_pattern", "launch_delay_ms", "window_timeout_ms", "process_names",
            "monitor_index", "window_snap", "custom_rect"
        }
        filtered = {k: v for k, v in clean.items() if k in allowed_keys}
        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def expanded_executable(self) -> str:
        """Expands Windows environment variables like %ProgramFiles% safely."""
        if not self.executable:
            return ""
        return os.path.expandvars(self.executable)


@dataclass
class DesktopConfig:
    """Configuration for an individual virtual desktop."""
    number: int = 1
    name: str = "Desktop 1"
    desktop_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DesktopConfig:
        return cls(
            number=data.get("number", 1),
            name=data.get("name", f"Desktop {data.get('number', 1)}"),
            desktop_id=data.get("desktop_id") or data.get("desktopId")
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkspaceProfile:
    """A profile encapsulating desktop setups and application configurations."""
    id: str = "default"
    name: str = "Default Workspace"
    description: str = ""
    desktops: List[DesktopConfig] = field(default_factory=list)
    apps: List[AppConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceProfile:
        desktops = [DesktopConfig.from_dict(d) for d in data.get("desktops", [])]
        apps = [AppConfig.from_dict(a) for a in data.get("apps", [])]
        return cls(
            id=data.get("id", "default"),
            name=data.get("name", "Default Workspace"),
            description=data.get("description", ""),
            desktops=desktops,
            apps=apps
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "desktops": [d.to_dict() for d in self.desktops],
            "apps": [a.to_dict() for a in self.apps]
        }

    def get_apps_for_desktop(self, desktop_number: int) -> List[AppConfig]:
        """Returns all configured applications assigned to a given desktop."""
        return [app for app in self.apps if app.desktop == desktop_number]

    def get_max_desktop_number(self) -> int:
        """Determines the maximum desktop number required by desktops and app assignments."""
        max_dt = max([d.number for d in self.desktops], default=1)
        max_app = max([a.desktop for a in self.apps if a.enabled], default=1)
        return max(max_dt, max_app, 1)


@dataclass
class GeneralSettings:
    """General manager settings."""
    start_with_windows: bool = False
    auto_launch_workspace: bool = False
    confirm_before_execution: bool = True
    minimize_to_tray: bool = False
    start_minimized: bool = False
    theme: str = "System"
    active_profile_id: str = "default"
    first_run_completed: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GeneralSettings:
        allowed = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**allowed)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionSettings:
    """Execution timing and polling settings."""
    window_timeout_ms: int = 15000
    polling_interval_ms: int = 250
    launch_delay_ms: int = 1000
    retry_count: int = 3

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutionSettings:
        allowed = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**allowed)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LoggingSettings:
    """Logging settings."""
    log_level: str = "INFO"
    log_retention_days: int = 14
    log_dir: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LoggingSettings:
        allowed = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**allowed)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SafetySettings:
    """Strict safety guards ensuring no damage to user files or desktops."""
    automation_enabled: bool = True
    require_confirmation: bool = True
    dry_run_default: bool = False
    never_kill_processes: bool = True
    never_delete_desktops: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SafetySettings:
        allowed = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**allowed)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkspaceConfig:
    """Root configuration structure for the workspace manager."""
    schema_version: int = 1
    profiles: List[WorkspaceProfile] = field(default_factory=list)
    general: GeneralSettings = field(default_factory=GeneralSettings)
    execution: ExecutionSettings = field(default_factory=ExecutionSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    safety: SafetySettings = field(default_factory=SafetySettings)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkspaceConfig:
        profiles_raw = data.get("profiles", [])
        profiles = [WorkspaceProfile.from_dict(p) for p in profiles_raw]
        if not profiles:
            profiles = [cls.create_default_profile()]

        return cls(
            schema_version=data.get("schema_version", data.get("schemaVersion", 1)),
            profiles=profiles,
            general=GeneralSettings.from_dict(data.get("general", {})),
            execution=ExecutionSettings.from_dict(data.get("execution", {})),
            logging=LoggingSettings.from_dict(data.get("logging", {})),
            safety=SafetySettings.from_dict(data.get("safety", {}))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "profiles": [p.to_dict() for p in self.profiles],
            "general": self.general.to_dict(),
            "execution": self.execution.to_dict(),
            "logging": self.logging.to_dict(),
            "safety": self.safety.to_dict()
        }

    def get_active_profile(self) -> WorkspaceProfile:
        """Returns the currently active workspace profile."""
        for p in self.profiles:
            if p.id == self.general.active_profile_id:
                return p
        if self.profiles:
            return self.profiles[0]
        default = self.create_default_profile()
        self.profiles.append(default)
        return default

    @classmethod
    def create_default_profile(cls) -> WorkspaceProfile:
        """
        Builds the default 4-desktop workspace as required by Section 6:
        Desktop 1: Browser (Brave Browser)
        Desktop 2: Development (Google Antigravity)
        Desktop 3: Database (SQL Server Management Studio)
        Desktop 4: API Development (Postman)
        """
        desktops = [
            DesktopConfig(number=1, name="Browser"),
            DesktopConfig(number=2, name="Development"),
            DesktopConfig(number=3, name="Database"),
            DesktopConfig(number=4, name="API Development")
        ]
        apps = [
            AppConfig(
                id="brave",
                name="Brave Browser",
                executable="%ProgramFiles%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                desktop=1,
                enabled=True,
                process_names=["brave.exe"]
            ),
            AppConfig(
                id="antigravity",
                name="Google Antigravity",
                executable="%LocalAppData%\\Programs\\Google Antigravity\\Google Antigravity.exe",
                desktop=2,
                enabled=True,
                process_names=["Google Antigravity.exe", "antigravity.exe", "agy.exe"]
            ),
            AppConfig(
                id="ssms",
                name="SQL Server Management Studio",
                executable="%ProgramFiles(x86)%\\Microsoft SQL Server Management Studio 20\\Common7\\IDE\\Ssms.exe",
                desktop=3,
                enabled=True,
                process_names=["Ssms.exe"]
            ),
            AppConfig(
                id="postman",
                name="Postman",
                executable="%LocalAppData%\\Postman\\Postman.exe",
                desktop=4,
                enabled=True,
                process_names=["Postman.exe"]
            )
        ]
        return WorkspaceProfile(
            id="default",
            name="Default Workspace",
            description="Default 4-desktop developer workspace",
            desktops=desktops,
            apps=apps
        )
