"""Resolves the bundled logo mark and scales it for Qt widgets.

Mirrors the frozen-vs-source lookup in ``audio/player.py``: a packaged
``.app`` ships the PNG under ``sys._MEIPASS``, while a source checkout reads
it straight from the repository's ``assets/`` folder.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


def logo_mark_path() -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        bundled = Path(bundle_dir) / "assets" / "logo-mark.png"
        if bundled.is_file():
            return bundled

    return Path(__file__).resolve().parents[3] / "assets" / "logo-mark.png"


def logo_pixmap(size: int) -> QPixmap:
    """Load the logo mark, scaled to a ``size`` x ``size`` square pixmap."""
    source = QPixmap(str(logo_mark_path()))
    return source.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
