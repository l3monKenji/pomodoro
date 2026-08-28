"""Console entry point: ``pomodoro`` opens the GUI window."""

from __future__ import annotations


def main() -> int:
    from .gui.app import run

    return run()


if __name__ == "__main__":
    raise SystemExit(main())
