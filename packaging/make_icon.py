"""Render the app icon (``Pomodoro.icns``) from the same blue/ring motif
the app itself uses. Run standalone; it writes next to this file.

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
from PySide6.QtGui import (  # noqa: E402
    QBrush,
    QColor,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPen,
)

HERE = Path(__file__).resolve().parent

# Palette lifted from src/pomodoro/gui/theme.py (dark theme "focus" blue).
BG_TOP = QColor("#4f8cff")
BG_BOTTOM = QColor("#2f5fd0")
TRACK = QColor(255, 255, 255, 60)
RING = QColor("#eaf1ff")


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

    # Progress ring: full faint track + a 70% arc from 12 o'clock, clockwise.
    stroke = size * 0.075
    inset = size * 0.28
    ring_rect = QRectF(inset, inset, size - 2 * inset, size - 2 * inset)

    track_pen = QPen(TRACK)
    track_pen.setWidthF(stroke)
    track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(track_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawArc(ring_rect, 0, 360 * 16)

    ring_pen = QPen(RING)
    ring_pen.setWidthF(stroke)
    ring_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(ring_pen)
    painter.drawArc(ring_rect, 90 * 16, int(-0.7 * 360 * 16))

    painter.end()
    return image


def main() -> int:
    if not shutil.which("iconutil"):
        print("iconutil not found - this script only runs on macOS.", file=sys.stderr)
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
