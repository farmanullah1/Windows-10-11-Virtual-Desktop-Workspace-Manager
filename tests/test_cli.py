"""
Unit tests for CLI parsing and command-line execution modes.
All tests run with isolated configurations and mock providers.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from app.main import parse_args
from app.models.workspace import WorkspaceConfig
from app.configuration.config_store import ConfigStore


def test_parse_args_defaults():
    with patch.object(sys, "argv", ["main.py"]):
        args = parse_args()
        assert not args.run
        assert not args.config
        assert not args.dry_run
        assert not args.sync
        assert not args.minimized
        assert not args.create_shortcuts


def test_parse_args_run_mode():
    with patch.object(sys, "argv", ["main.py", "--run", "--no-prompt", "--headless"]):
        args = parse_args()
        assert args.run
        assert args.no_prompt
        assert args.headless


def test_parse_args_shortcut_flags():
    with patch.object(sys, "argv", ["main.py", "--create-shortcuts"]):
        args = parse_args()
        assert args.create_shortcuts

    with patch.object(sys, "argv", ["main.py", "--remove-shortcuts"]):
        args = parse_args()
        assert args.remove_shortcuts


def test_parse_args_profile():
    with patch.object(sys, "argv", ["main.py", "--profile", "CustomDev"]):
        args = parse_args()
        assert args.profile == "CustomDev"
