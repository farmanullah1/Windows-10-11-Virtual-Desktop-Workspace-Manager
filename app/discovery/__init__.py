"""
Discovery package exports.
"""

from app.discovery.app_templates import (
    AppTemplate,
    APPLICATION_TEMPLATES,
    get_template_by_id,
)
from app.discovery.shortcut_resolver import (
    ShortcutResolver,
    DiscoveredShortcut,
)
from app.discovery.running_apps import (
    RunningAppDiscoverer,
    RunningAppInfo,
)
from app.discovery.app_detector import AppDetector

__all__ = [
    "AppTemplate",
    "APPLICATION_TEMPLATES",
    "get_template_by_id",
    "ShortcutResolver",
    "DiscoveredShortcut",
    "RunningAppDiscoverer",
    "RunningAppInfo",
    "AppDetector",
]
