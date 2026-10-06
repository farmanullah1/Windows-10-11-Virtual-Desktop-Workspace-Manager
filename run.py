"""
Virtual Desktop Workspace Manager — Bootstrap Forwarder (Section 83B).

As mandated by Section 83B, 'setup.py' is the single supported setup entry point.
This module is maintained as a transparent wrapper forwarding to setup.py.
"""

import sys
from setup import main, SetupRunner, parse_args, SETUP_VERSION

if __name__ == "__main__":
    main()
