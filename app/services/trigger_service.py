"""
Trigger Engine for automated, event-driven workspace execution.
Supports:
- Display topology changes (monitor connected/disconnected)
- Scheduled time-of-day execution
- Startup execution
Guarded by SafetySettings.automation_enabled and configurable cooldowns.
"""

from __future__ import annotations
import time
import threading
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List
from app.models.workspace import WorkspaceConfig, TriggerType, ProfileTrigger
from app.providers.base import IWindowProvider
from app.logging.logger import get_logger


class TriggerEngine:
    """Monitors session and hardware events to automatically trigger workspace profiles."""

    def __init__(
        self,
        get_config_func: Callable[[], WorkspaceConfig],
        window_provider: IWindowProvider,
        on_trigger_callback: Optional[Callable[[str, str], None]] = None,
        poll_interval_seconds: float = 5.0
    ):
        self.get_config_func = get_config_func
        self.window_provider = window_provider
        self.on_trigger_callback = on_trigger_callback
        self.poll_interval = poll_interval_seconds
        self.logger = get_logger()

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_monitor_count: Optional[int] = None
        self._last_checked_minute: Optional[str] = None

    def start(self) -> None:
        """Starts the background monitoring thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            try:
                monitors = self.window_provider.get_monitors()
                self._last_monitor_count = len(monitors)
            except Exception:
                self._last_monitor_count = 1

            self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="VDWM-TriggerEngine")
            self._thread.start()
            self.logger.info("TriggerEngine started in background.")

    def stop(self) -> None:
        """Stops the background monitoring thread."""
        with self._lock:
            if not self._running:
                return
            self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.logger.info("TriggerEngine stopped.")

    def is_running(self) -> bool:
        return self._running

    def _worker_loop(self) -> None:
        while self._running:
            try:
                self.check_triggers_once()
            except Exception as ex:
                self.logger.error(f"Error in TriggerEngine worker loop: {ex}")

            # Sleep in small increments for responsive shutdown
            slept = 0.0
            while self._running and slept < self.poll_interval:
                time.sleep(0.5)
                slept += 0.5

    def check_triggers_once(self) -> List[Dict[str, Any]]:
        """Evaluates triggers once and fires any matching actions. Returns list of triggered events."""
        config = self.get_config_func()
        if not config.safety.automation_enabled:
            return []

        now_ts = time.time()
        now_hm = datetime.now().strftime("%H:%M")
        triggered_events: List[Dict[str, Any]] = []

        # 1. Display Topology Check
        display_changed = False
        try:
            current_monitors = self.window_provider.get_monitors()
            curr_count = len(current_monitors)
            if self._last_monitor_count is not None and curr_count != self._last_monitor_count:
                display_changed = True
                self.logger.info(f"Display topology change detected: {self._last_monitor_count} -> {curr_count} monitors.")
            self._last_monitor_count = curr_count
        except Exception as ex:
            self.logger.debug(f"Failed to query monitors in trigger check: {ex}")

        # 2. Evaluate profiles
        for profile in config.profiles:
            for trigger in profile.triggers:
                if not trigger.enabled:
                    continue

                # Check cooldown
                if trigger.last_triggered and (now_ts - trigger.last_triggered < trigger.cooldown_seconds):
                    continue

                fired = False

                # Display Change trigger
                if trigger.trigger_type == TriggerType.ON_DISPLAY_CHANGE.value and display_changed:
                    fired = True

                # Time Schedule trigger
                elif trigger.trigger_type == TriggerType.ON_TIME_SCHEDULE.value and trigger.time_of_day:
                    if trigger.time_of_day == now_hm and self._last_checked_minute != now_hm:
                        fired = True

                if fired:
                    trigger.last_triggered = now_ts
                    event_info = {
                        "profile_id": profile.id,
                        "profile_name": profile.name,
                        "trigger_type": trigger.trigger_type,
                        "timestamp": now_ts
                    }
                    triggered_events.append(event_info)
                    self.logger.info(f"Trigger fired for Profile '{profile.name}' ({trigger.trigger_type})")

                    if self.on_trigger_callback:
                        try:
                            self.on_trigger_callback(profile.id, trigger.trigger_type)
                        except Exception as cb_ex:
                            self.logger.error(f"Trigger callback failure: {cb_ex}")

        self._last_checked_minute = now_hm
        return triggered_events
