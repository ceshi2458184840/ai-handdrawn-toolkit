#!/usr/bin/env python3
"""Backward-compatible wrapper for app.cli.generate."""
import sys

if __name__ == "__main__":
    sys.argv = ["ai-handdrawn", "generate"] + sys.argv[1:]
    from app.cli import main
    main()
