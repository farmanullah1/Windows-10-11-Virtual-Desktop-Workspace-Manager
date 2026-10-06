"""
Virtual Desktop Workspace Manager — Configure Entry Point.

Dedicated executable entry point to open the configuration & settings graphical interface.
Strict Safety Guarantee: This entry point NEVER launches workspaces, creates desktops,
or moves windows automatically.
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
    if "--config" not in sys.argv:
        sys.argv.append("--config")
    app_main()


if __name__ == "__main__":
    main()

