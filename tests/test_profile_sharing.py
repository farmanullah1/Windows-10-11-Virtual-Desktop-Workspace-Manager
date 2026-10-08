"""
Tests for ProfileSharingService: secure export, path generalization, and encrypted import.
"""

import os
import pytest
from pathlib import Path
from app.models.workspace import (
    WorkspaceProfile,
    DesktopConfig,
    AppConfig,
    WindowSnap,
)
from app.services.profile_sharing import ProfileSharingService


@pytest.fixture
def sample_profile():
    return WorkspaceProfile(
        id="p-team-dev",
        name="Team Full-Stack Dev",
        description="Standard onboarding environment for developers",
        desktops=[
            DesktopConfig(1, "Editor & Code"),
            DesktopConfig(2, "Browser & API"),
        ],
        apps=[
            AppConfig(
                id="app-code",
                name="VS Code",
                executable="C:\\Users\\alice\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
                desktop=1,
                window_snap=WindowSnap.MAXIMIZE.value
            ),
            AppConfig(
                id="app-postman",
                name="Postman",
                executable="C:\\Users\\alice\\AppData\\Local\\Postman\\Postman.exe",
                desktop=2,
                window_snap=WindowSnap.LEFT_HALF.value
            )
        ]
    )


def test_plain_export_and_import(tmp_path, sample_profile):
    """Verifies plain export and import roundtrip without password."""
    service = ProfileSharingService()
    out_file = tmp_path / "dev_profile.vdwm"

    service.export_profile(sample_profile, out_file, passcode=None)
    assert out_file.exists()

    imported = service.import_profile(out_file)
    assert imported.id == "p-team-dev"
    assert imported.name == "Team Full-Stack Dev"
    assert len(imported.apps) == 2
    assert imported.apps[0].window_snap == WindowSnap.MAXIMIZE.value


def test_encrypted_export_and_import_with_passcode(tmp_path, sample_profile):
    """Verifies encrypted export with passcode and successful decryption."""
    service = ProfileSharingService()
    out_file = tmp_path / "secure_profile.vdwm"
    passcode = "StrongTeamPass123!"

    service.export_profile(sample_profile, out_file, passcode=passcode)
    assert out_file.exists()

    # Importing without passcode should fail
    with pytest.raises(ValueError, match="A passcode is required"):
        service.import_profile(out_file, passcode=None)

    # Importing with wrong passcode should fail
    with pytest.raises(ValueError, match="Incorrect passcode"):
        service.import_profile(out_file, passcode="WrongPass!")

    # Importing with correct passcode succeeds
    imported = service.import_profile(out_file, passcode=passcode)
    assert imported.name == "Team Full-Stack Dev"
    assert len(imported.desktops) == 2


def test_path_generalization(sample_profile):
    """Verifies personal user paths are replaced with generic environment variables."""
    service = ProfileSharingService()
    orig_env = os.environ.get("USERPROFILE")
    try:
        os.environ["USERPROFILE"] = "C:\\Users\\alice"
        generalized = service.generalize_paths(sample_profile)
        assert "%USERPROFILE%" in generalized.apps[0].executable
        assert "alice" not in generalized.apps[0].executable
    finally:
        if orig_env:
            os.environ["USERPROFILE"] = orig_env
        else:
            os.environ.pop("USERPROFILE", None)
