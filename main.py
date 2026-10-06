"""
Virtual Desktop Workspace Manager - Main Entry Point.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from app.main import main

if __name__ == "__main__":
    main()
