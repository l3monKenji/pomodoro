"""Optional macOS desktop notifications via osascript."""

from __future__ import annotations

import shutil
import subprocess


def send_notification(title: str, message: str) -> None:
    """Best-effort desktop notification. Silently does nothing if unavailable."""
    osascript = shutil.which("osascript")
    if not osascript:
        return
    script = f'display notification "{_escape(message)}" with title "{_escape(title)}"'
    try:
        subprocess.Popen([osascript, "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')
