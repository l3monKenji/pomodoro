"""Entry point PyInstaller freezes into ``Pomodoro.app``.

Kept as a tiny standalone launcher so the spec file has a single, obvious
script to analyse. All real logic lives in the ``pomodoro`` package.
"""

from __future__ import annotations

from pomodoro.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
