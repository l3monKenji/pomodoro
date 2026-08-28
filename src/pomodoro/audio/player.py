"""MP3 playback for phase-end signals, with a safe silent/beep fallback.

Uses macOS's built-in ``afplay`` so the app doesn't need an extra audio
dependency. Missing sound files (or a missing ``afplay``) never crash the
app - callers can check the return value to surface a hint in the UI.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def default_sounds_dir() -> Path:
    """Resolve where to look for ``focus_end.mp3`` / ``break_end.mp3``.

    Order of precedence:
    1. ``POMODORO_SOUNDS_DIR`` env var, for an explicit override.
    2. The repository's own ``sounds/`` folder, so a source checkout (e.g.
       ``pip install -e .``) works out of the box with the README instructions.
    3. A ``sounds`` folder under the app's Application Support directory,
       created on demand, for non-editable (wheel) installs.
    """
    override = os.environ.get("POMODORO_SOUNDS_DIR")
    if override:
        return Path(override).expanduser()

    repo_candidate = Path(__file__).resolve().parents[3] / "sounds"
    if repo_candidate.is_dir():
        return repo_candidate

    from ..persistence.paths import app_data_dir

    fallback = app_data_dir() / "sounds"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


class SoundPlayer:
    def __init__(self, sounds_dir: Path) -> None:
        self.sounds_dir = sounds_dir
        self._afplay = shutil.which("afplay")

    def play(self, filename: str) -> bool:
        """Play ``filename`` from the sounds directory.

        Returns True if a real sound file was played, False if the app
        fell back to a silent no-op / terminal beep.
        """
        path = self.sounds_dir / filename
        if self._afplay and path.is_file():
            try:
                subprocess.Popen(
                    [self._afplay, str(path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except OSError:
                pass
        self._fallback_beep()
        return False

    @staticmethod
    def _fallback_beep() -> None:
        try:
            sys.stdout.write("\a")
            sys.stdout.flush()
        except OSError:
            pass
