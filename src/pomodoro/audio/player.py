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


def _existing(path: str) -> str | None:
    return path if Path(path).is_file() else None


def default_sounds_dir() -> Path:
    """Resolve where to look for ``focus_end.mp3`` / ``break_end.mp3``.

    Order of precedence:
    1. ``POMODORO_SOUNDS_DIR`` env var, for an explicit override.
    2. A ``sounds`` folder under the app's Application Support directory,
       if the user has dropped their own MP3s there - this is the only way
       to customise sounds in the packaged ``.app`` (see README).
    3. When running from a frozen ``.app`` bundle: the ``sounds`` folder
       shipped inside the bundle.
    4. The repository's own ``sounds/`` folder, so a source checkout (e.g.
       ``pip install -e .``) works out of the box with the README instructions.
    5. A ``sounds`` folder under Application Support, created on demand, as a
       last resort for non-editable (wheel) installs.
    """
    override = os.environ.get("POMODORO_SOUNDS_DIR")
    if override:
        return Path(override).expanduser()

    from ..persistence.paths import app_data_dir

    user_sounds = app_data_dir() / "sounds"
    if any((user_sounds / name).is_file() for name in ("focus_end.mp3", "break_end.mp3")):
        return user_sounds

    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        bundled = Path(bundle_dir) / "sounds"
        if bundled.is_dir():
            return bundled

    repo_candidate = Path(__file__).resolve().parents[3] / "sounds"
    if repo_candidate.is_dir():
        return repo_candidate

    user_sounds.mkdir(parents=True, exist_ok=True)
    return user_sounds


class SoundPlayer:
    def __init__(self, sounds_dir: Path) -> None:
        self.sounds_dir = sounds_dir
        # A Finder-launched .app inherits a minimal PATH, so fall back to the
        # well-known absolute location of macOS's bundled afplay.
        self._afplay = shutil.which("afplay") or _existing("/usr/bin/afplay")

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
