#!/usr/bin/env python3
"""List, audit or selectively install this repository's skills."""
try:
    from .skill_install import main
except ImportError:
    from skill_install import main

if __name__ == '__main__':
    raise SystemExit(main())
