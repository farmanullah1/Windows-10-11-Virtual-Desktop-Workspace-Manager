"""
Fuzz and robustness testing suite per Section 88 of Master Prompt.
Validates that malformed, unexpected, or extreme inputs never crash the system:
- Missing fields
- Unknown fields
- Invalid types
- Extreme string lengths (up to 50,000 chars)
- Malformed regex patterns
- Negative and out-of-range numeric values
- Duplicate IDs (profile, app, desktop)
- Unreferenced desktop numbers
- Diverse Unicode (Arabic, Japanese, Cyrillic, Emojis)
"""

import json
import pytest
from pathlib import Path
from app.models.workspace import (
    WorkspaceConfig,
    WorkspaceProfile,
    AppConfig,
    DesktopConfig,
    GeneralSettings,
    ExecutionSettings,
    LoggingSettings,
    SafetySettings,
    WindowPolicy,
)
from app.configuration.validator import ConfigValidator, ConfigValidationError
from app.configuration.migration import ConfigMigration
from app.core.execution_plan import WorkspaceExecutionPlan
from app.providers.mock_provider import (
    MockVirtualDesktopProvider,
    MockWindowProvider,
    MockProcessProvider,
    MockApplicationLauncher,
)
from app.providers.base import WindowInfo
from app.discovery.app_detector import AppDetector


class TestFuzzConfigurationParsing:
    """Tests robustness against unexpected, missing, and fuzzed JSON structures."""

    def test_missing_fields_defaults_safely(self):
        """Empty dictionary or partial dict must parse without crashing."""
        raw = {}
        migrated = ConfigMigration.migrate(raw)
        cfg = WorkspaceConfig.from_dict(migrated)

        assert isinstance(cfg, WorkspaceConfig)
        assert cfg.schema_version == 1
        assert isinstance(cfg.general, GeneralSettings)
        assert isinstance(cfg.execution, ExecutionSettings)
        assert isinstance(cfg.logging, LoggingSettings)
        assert isinstance(cfg.safety, SafetySettings)

    def test_unknown_fields_ignored_without_crash(self):
        """Extra keys injected by future versions or user edits must not cause exceptions."""
        raw = {
            "schema_version": 1,
            "future_experimental_flag": True,
            "alien_data": {"nested_key": [1, 2, 3]},
            "profiles": [
                {
                    "id": "p1",
                    "name": "Standard",
                    "extra_profile_param": 999,
                    "desktops": [{"number": 1, "name": "Main", "extra_prop": "val"}],
                    "apps": [
                        {
                            "id": "app1",
                            "name": "Editor",
                            "unknown_option": "safe_to_ignore",
                            "desktop": 1
                        }
                    ]
                }
            ]
        }
        migrated = ConfigMigration.migrate(raw)
        cfg = WorkspaceConfig.from_dict(migrated)

        assert cfg.profiles[0].id == "p1"
        assert cfg.profiles[0].apps[0].id == "app1"

    def test_extreme_string_lengths(self):
        """Tests handling of giant string payloads (up to 50,000 characters)."""
        huge_name = "A" * 10000
        huge_args = " --flag=" + ("B" * 40000)
        huge_path = "C:\\" + ("folder\\" * 100) + "app.exe"

        app = AppConfig(
            id="app_huge",
            name=huge_name,
            arguments=huge_args,
            executable=huge_path,
            desktop=1
        )
        profile = WorkspaceProfile(id="p_huge", name="Huge Profile", desktops=[DesktopConfig(1, "D1")], apps=[app])
        cfg = WorkspaceConfig(profiles=[profile])

        # Must serialize and deserialize cleanly
        as_dict = cfg.to_dict()
        json_str = json.dumps(as_dict)
        reloaded = WorkspaceConfig.from_dict(json.loads(json_str))

        assert len(reloaded.profiles[0].apps[0].name) == 10000
        assert len(reloaded.profiles[0].apps[0].arguments) == len(huge_args)

    def test_malformed_regex_in_window_matching(self):
        """Malformed regex in window matching pattern must fail gracefully without crash."""
        window_provider = MockWindowProvider([
            WindowInfo(hwnd=1001, title="Editor Window", pid=10, executable="app.exe", is_visible=True, is_minimized=False, is_maximized=False)
        ])
        proc_provider = MockProcessProvider()
        launcher = MockApplicationLauncher(window_provider=window_provider, process_provider=proc_provider)
        detector = AppDetector(proc_provider)

        bad_regex_app = AppConfig(
            id="bad_rx",
            name="Bad Regex App",
            desktop=1,
            window_policy=WindowPolicy.TITLE_REGEX.value,
            title_pattern="[unclosed-regex-bracket(",  # Fatal regex syntax error
        )
        profile = WorkspaceProfile(id="p_rx", name="Regex Profile", desktops=[DesktopConfig(1, "D1")], apps=[bad_regex_app])

        plan = WorkspaceExecutionPlan(
            profile=profile,
            desktop_provider=MockVirtualDesktopProvider(),
            window_provider=window_provider,
            process_provider=proc_provider,
            launcher=launcher,
            app_detector=detector
        )

        candidates = window_provider.get_all_top_level_windows()
        # Must catch re.error internally and fall back to candidates safely
        filtered = plan._filter_windows_by_policy(bad_regex_app, candidates)
        assert len(filtered) == 1

    def test_negative_and_out_of_range_values_validation(self):
        """Validator must report distinct errors for negative and out-of-range parameters."""
        app = AppConfig(
            id="app_invalid_nums",
            name="Invalid Num App",
            desktop=-1,  # invalid desktop
            launch_delay_ms=-50,  # negative delay
            window_timeout_ms=500000,  # exceeds 120,000 ms max
        )
        profile = WorkspaceProfile(id="p1", name="Profile 1", desktops=[DesktopConfig(-1, "Bad Desktop")], apps=[app])
        cfg = WorkspaceConfig(profiles=[profile])

        errors, warnings = ConfigValidator.validate_config(cfg)
        assert len(errors) >= 3
        assert any("target desktop must be >= 1" in e for e in errors)
        assert any("launch delay must be between" in e for e in errors)
        assert any("window timeout must be between" in e for e in errors)

    def test_duplicate_identifiers_detection(self):
        """Validator must reject duplicates in app IDs, profile IDs, and desktop numbers."""
        profile1 = WorkspaceProfile(
            id="p_duplicate",
            name="Profile Duplicate",
            desktops=[
                DesktopConfig(1, "Desktop 1"),
                DesktopConfig(1, "Duplicate Desktop 1")  # duplicate desktop number
            ],
            apps=[
                AppConfig(id="dup_app_id", name="App 1", desktop=1),
                AppConfig(id="dup_app_id", name="App 2", desktop=1),  # duplicate app id
            ]
        )
        profile2 = WorkspaceProfile(
            id="p_duplicate",  # duplicate profile id
            name="Profile Duplicate 2",
            desktops=[DesktopConfig(1, "Desktop 1")],
            apps=[]
        )
        cfg = WorkspaceConfig(profiles=[profile1, profile2])

        errors, warnings = ConfigValidator.validate_config(cfg)
        assert any("Duplicate application ID" in e for e in errors)
        assert any("Duplicate profile ID" in e for e in errors)
        assert any("Duplicate desktop number" in e for e in errors)

        with pytest.raises(ConfigValidationError):
            ConfigValidator.validate(cfg)

    def test_unreferenced_desktop_warning(self):
        """Apps mapped to non-existent desktops generate a validation warning without crashing."""
        profile = WorkspaceProfile(
            id="p_unref",
            name="Unreferenced Profile",
            desktops=[DesktopConfig(1, "Desktop 1")],
            apps=[
                AppConfig(id="a1", name="App 1", desktop=99)  # desktop 99 not in desktops
            ]
        )
        cfg = WorkspaceConfig(profiles=[profile])

        errors, warnings = ConfigValidator.validate_config(cfg)
        assert len(errors) == 0  # not fatal
        assert any("is assigned to Desktop 99, which is not defined" in w for w in warnings)

    def test_internationalization_unicode_robustness(self):
        """Ensures non-ASCII character sets and emojis persist and serialize properly."""
        intl_names = [
            "ワークスペース 🚀",  # Japanese + Emoji
            "Рабочий стол",        # Russian / Cyrillic
            "مساحة العمل",          # Arabic RTL
            "Espace de Travail",   # French accents
        ]

        apps = [
            AppConfig(id=f"app_{i}", name=name, desktop=1)
            for i, name in enumerate(intl_names)
        ]
        profile = WorkspaceProfile(id="p_intl", name="Multi-language 🌍", desktops=[DesktopConfig(1, "سطح المكتب 1")], apps=apps)
        cfg = WorkspaceConfig(profiles=[profile])

        # Test full JSON roundtrip
        json_output = json.dumps(cfg.to_dict(), ensure_ascii=False)
        reloaded_dict = json.loads(json_output)
        reloaded_cfg = WorkspaceConfig.from_dict(reloaded_dict)

        assert reloaded_cfg.profiles[0].name == "Multi-language 🌍"
        assert reloaded_cfg.profiles[0].apps[0].name == "ワークスペース 🚀"
        assert reloaded_cfg.profiles[0].apps[2].name == "مساحة العمل"
        assert reloaded_cfg.profiles[0].desktops[0].name == "سطح المكتب 1"
