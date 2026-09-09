"""Resolves the bundled logo mark and rasterises it for Qt widgets.

Mirrors the frozen-vs-source lookup in ``audio/player.py``: a packaged
``.app`` ships the SVG under ``sys._MEIPASS``, while a source checkout reads
it straight from the repository's ``assets/`` folder.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


def logo_mark_path() -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        bundled = Path(bundle_dir) / "assets" / "logo-mark.svg"
        if bundled.is_file():
            return bundled

    return Path(__file__).resolve().parents[3] / "assets" / "logo-mark.svg"


def logo_pixmap(size: int) -> QPixmap:
    """Render the logo mark to a transparent square pixmap of ``size`` px."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    renderer = QSvgRenderer(str(logo_mark_path()))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()

    return pixmap
