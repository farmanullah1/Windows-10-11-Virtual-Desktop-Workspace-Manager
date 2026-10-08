"""
Tests for TriggerEngine event-driven automation.
"""

import time
from datetime import datetime
from app.models.workspace import (
    WorkspaceConfig,
    WorkspaceProfile,
    ProfileTrigger,
    TriggerType,
)
from app.providers.base import MonitorInfo
from app.providers.mock_provider import MockWindowProvider
from app.services.trigger_service import TriggerEngine


def test_trigger_engine_display_change():
    """Verifies that changing monitor count fires ON_DISPLAY_CHANGE trigger."""
    fired = []

    def on_fired(prof_id, trig_type):
        fired.append((prof_id, trig_type))

    profile = WorkspaceProfile(
        id="p-dock",
        name="Dock Profile",
        triggers=[
            ProfileTrigger(
                trigger_type=TriggerType.ON_DISPLAY_CHANGE.value,
                enabled=True,
                cooldown_seconds=10
            )
        ]
    )
    config = WorkspaceConfig(profiles=[profile])

    win_provider = MockWindowProvider(initial_monitors=[
        MonitorInfo(index=0, x=0, y=0, width=1920, height=1080, is_primary=True)
    ])

    engine = TriggerEngine(
        get_config_func=lambda: config,
        window_provider=win_provider,
        on_trigger_callback=on_fired
    )

    # Initial check sets baseline
    engine.check_triggers_once()
    assert len(fired) == 0

    # Simulate docking external monitor
    win_provider.monitors.append(MonitorInfo(index=1, x=1920, y=0, width=2560, height=1440))

    events = engine.check_triggers_once()
    assert len(events) == 1
    assert len(fired) == 1
    assert fired[0] == ("p-dock", "on_display_change")

    # Second check without change does NOT fire
    events2 = engine.check_triggers_once()
    assert len(events2) == 0


def test_trigger_engine_schedule_and_cooldown():
    """Verifies scheduled time trigger fires and respects cooldown."""
    fired = []
    now_hm = datetime.now().strftime("%H:%M")

    profile = WorkspaceProfile(
        id="p-work",
        name="Morning Work",
        triggers=[
            ProfileTrigger(
                trigger_type=TriggerType.ON_TIME_SCHEDULE.value,
                enabled=True,
                time_of_day=now_hm,
                cooldown_seconds=300
            )
        ]
    )
    config = WorkspaceConfig(profiles=[profile])
    win_provider = MockWindowProvider()

    engine = TriggerEngine(
        get_config_func=lambda: config,
        window_provider=win_provider,
        on_trigger_callback=lambda p, t: fired.append((p, t))
    )

    events = engine.check_triggers_once()
    assert len(events) == 1
    assert len(fired) == 1

    # Immediate second check should be stopped by cooldown
    events2 = engine.check_triggers_once()
    assert len(events2) == 0
    assert len(fired) == 1


def test_trigger_engine_automation_disabled_guard():
    """Verifies that disabled automation in safety settings suppresses all triggers."""
    fired = []
    profile = WorkspaceProfile(
        id="p-suppressed",
        name="Suppressed Profile",
        triggers=[
            ProfileTrigger(trigger_type=TriggerType.ON_DISPLAY_CHANGE.value, enabled=True)
        ]
    )
    config = WorkspaceConfig(profiles=[profile])
    config.safety.automation_enabled = False  # Disabled

    win_provider = MockWindowProvider(initial_monitors=[MonitorInfo(0, 0, 0, 1920, 1080)])
    engine = TriggerEngine(
        get_config_func=lambda: config,
        window_provider=win_provider,
        on_trigger_callback=lambda p, t: fired.append(p)
    )

    engine.check_triggers_once()
    # Add monitor
    win_provider.monitors.append(MonitorInfo(1, 1920, 0, 1920, 1080))
    events = engine.check_triggers_once()

    assert len(events) == 0
    assert len(fired) == 0


def test_trigger_engine_start_stop_lifecycle():
    """Verifies background worker starts and stops cleanly."""
    config = WorkspaceConfig()
    win_provider = MockWindowProvider()
    engine = TriggerEngine(
        get_config_func=lambda: config,
        window_provider=win_provider,
        poll_interval_seconds=0.1
    )

    assert engine.is_running() is False
    engine.start()
    assert engine.is_running() is True
    time.sleep(0.2)
    engine.stop()
    assert engine.is_running() is False
