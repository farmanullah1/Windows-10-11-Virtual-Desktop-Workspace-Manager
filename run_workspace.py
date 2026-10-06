"""
Virtual Desktop Workspace Manager — Run Workspace Entry Point.

Dedicated executable entry point to explicitly execute the active workspace profile.
Double-clicking or invoking this entry point constitutes an explicit user action to run
the workspace according to persisted configuration and safety rules.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from app.main import main as app_main


def main():
    if "--run" not in sys.argv:
        sys.argv.append("--run")
    app_main()


if __name__ == "__main__":
    main()

