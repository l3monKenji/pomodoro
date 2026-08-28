"""Shared location for the app's persistent files.

Everything the app writes at runtime (settings, history database) lives
under macOS's standard per-user Application Support directory - never in
the repo/install directory - so it survives reinstalls and stays out of
version control.
"""

from __future__ import annotations

from pathlib import Path

_APP_FOLDER_NAME = "Pomodoro"


def app_data_dir() -> Path:
    directory = Path.home() / "Library" / "Application Support" / _APP_FOLDER_NAME
    directory.mkdir(parents=True, exist_ok=True)
    return directory
