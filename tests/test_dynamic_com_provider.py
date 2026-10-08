"""
Tests for WindowsDynamicComProvider vtable resolution and build detection.
"""

import pytest
from app.providers.base import IVirtualDesktopProvider
from app.providers.windows_dynamic_com_provider import WindowsDynamicComProvider


def test_provider_implements_interface():
    provider = WindowsDynamicComProvider()
    assert isinstance(provider, IVirtualDesktopProvider)


def test_build_profile_vtable_resolution():
    """Verifies that different Windows OS build numbers resolve to expected vtable profiles."""
    win10 = WindowsDynamicComProvider(simulated_build=19045)
    assert win10.build_profile_name == "win10"
    assert win10.get_vtable_offsets()["CreateDesktop"] == 10

    win11_21 = WindowsDynamicComProvider(simulated_build=22000)
    assert win11_21.build_profile_name == "win11_21h2"
    assert win11_21.get_vtable_offsets()["CreateDesktop"] == 11

    win11_22 = WindowsDynamicComProvider(simulated_build=22621)
    assert win11_22.build_profile_name == "win11_22h2"
    assert win11_22.get_vtable_offsets()["CreateDesktop"] == 12

    win11_24 = WindowsDynamicComProvider(simulated_build=26100)
    assert win11_24.build_profile_name == "win11_24h2"
    assert win11_24.get_vtable_offsets()["CreateDesktop"] == 13


def test_dynamic_provider_availability_and_fallback():
    """Verifies is_available queries cascade providers safely."""
    provider = WindowsDynamicComProvider(simulated_build=19045)
    # Should evaluate without raising unhandled exceptions
    avail = provider.is_available()
    assert isinstance(avail, bool)
