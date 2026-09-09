"""Render the app icon (``Pomodoro.icns``) from the shared logo mark at
``assets/logo-mark.svg``. Run standalone; it writes next to this file.

    python packaging/make_icon.py

Needs PySide6 (already a project dependency) and macOS's ``iconutil``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

HERE = Path(__file__).resolve().parent
MARK_SVG = HERE.parent / "assets" / "logo-mark.svg"

# Palette lifted from src/pomodoro/gui/theme.py (dark theme background) and
# from the mark's own stroke colour in assets/logo-mark.svg.
BG_TOP = QColor("#171f2a")
BG_BOTTOM = QColor("#0f1620")


def _render(size: int) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Rounded-rect background with a vertical blue gradient (macOS "squircle"
    # look is approximated with a generous corner radius).
    margin = size * 0.08
    body = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22
    gradient = QLinearGradient(0, body.top(), 0, body.bottom())
    gradient.setColorAt(0.0, BG_TOP)
    gradient.setColorAt(1.0, BG_BOTTOM)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(body, radius, radius)

    # The logo mark, rendered in its own blue against the dark body.
    renderer = QSvgRenderer(str(MARK_SVG))
    mark_inset = size * 0.16
    mark_rect = QRectF(mark_inset, mark_inset, size - 2 * mark_inset, size - 2 * mark_inset)
    renderer.render(painter, mark_rect)

    painter.end()
    return image


def main() -> int:
    if not shutil.which("iconutil"):
        print("iconutil not found - this script only runs on macOS.", file=sys.stderr)
        return 1
    if not MARK_SVG.is_file():
        print(f"Logo mark not found at {MARK_SVG}", file=sys.stderr)
        return 1

    QGuiApplication(sys.argv)

    iconset = HERE / "Pomodoro.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir()

    # (px, filename) pairs Apple's iconutil expects.
    specs = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    for px, name in specs:
        _render(px).save(str(iconset / name), "PNG")

    icns = HERE / "Pomodoro.icns"
    subprocess.run(
        ["iconutil", "--convert", "icns", str(iconset), "--output", str(icns)],
        check=True,
    )
    shutil.rmtree(iconset)
    print(f"Wrote {icns}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
