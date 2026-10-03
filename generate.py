"""Backward-compatible entrypoint."""
import sys
from app.cli import main

if __name__ == "__main__":
    sys.argv = ["generate"] + sys.argv[1:]
    main()
