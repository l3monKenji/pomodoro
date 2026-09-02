"""Allow ``python -m pomodoro`` to open the GUI window."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
