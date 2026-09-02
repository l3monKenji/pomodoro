"""Optional macOS desktop notifications via osascript."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def send_notification(title: str, message: str) -> None:
    """Best-effort desktop notification. Silently does nothing if unavailable."""
    # A Finder-launched .app inherits a minimal PATH; fall back to the
    # well-known absolute location of macOS's bundled osascript.
    osascript = shutil.which("osascript")
    if not osascript and Path("/usr/bin/osascript").is_file():
        osascript = "/usr/bin/osascript"
    if not osascript:
        return
    script = f'display notification "{_escape(message)}" with title "{_escape(title)}"'
    try:
        subprocess.Popen([osascript, "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')
