"""
Unit tests for SingleInstanceGuard (Section 37).
Verifies single-instance enforcement, duplicate launch prevention, and clean cleanup.
Guaranteed non-destructive using temporary directory.
"""

import tempfile
from pathlib import Path
import pytest

from app.services.single_instance import SingleInstanceGuard


@pytest.fixture
def temp_app_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def test_single_instance_acquire_and_release(temp_app_dir):
    guard1 = SingleInstanceGuard(app_data_dir=temp_app_dir)

    # First instance acquires lock successfully
    assert guard1.acquire() is True
    assert guard1._is_primary is True

    # Clean release
    guard1.release()
    assert guard1._is_primary is False
    assert not (temp_app_dir / "instance.lock").exists()


def test_single_instance_duplicate_prevention(temp_app_dir):
    guard1 = SingleInstanceGuard(app_data_dir=temp_app_dir)
    guard2 = SingleInstanceGuard(app_data_dir=temp_app_dir)

    # First instance acquires lock
    assert guard1.acquire() is True

    # Second instance attempting to acquire in the same process/file environment
    # Note: On Windows named mutex, mutex was created by guard1.
    # guard2 will detect mutex or existing PID in lockfile.
    result2 = guard2.acquire()
    assert result2 is False

    # Once primary releases
    guard1.release()

    # guard2 should now be able to acquire
    result3 = guard2.acquire()
    assert result3 is True
    guard2.release()
