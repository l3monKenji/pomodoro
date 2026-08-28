"""Reusable custom widgets: the phase progress ring and a mini bar chart."""

from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import FONT_FAMILY_MONO


class ProgressRing(QWidget):
    """A circular progress indicator with a big countdown label centered inside."""

    def __init__(self, diameter: int = 300, stroke_width: int = 14, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._diameter = diameter
        self._stroke_width = stroke_width
        self._progress = 0.0
        self._track_color = QColor("#24344a")
        self._ring_color = QColor("#4f8cff")
        self._center_text = "00:00"
        self._sub_text = ""

        self._color_anim = QPropertyAnimation(self, b"ringColor", self)
        self._color_anim.setDuration(450)
        self._color_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.setMinimumSize(diameter, diameter)

    def sizeHint(self):  # noqa: D102 - Qt override
        from PySide6.QtCore import QSize

        return QSize(self._diameter, self._diameter)

    # -- properties exposed for styling / animation -----------------------
    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, value: float) -> None:
        self._progress = min(max(value, 0.0), 1.0)
        self.update()

    progress = Property(float, get_progress, set_progress)

    def get_ring_color(self) -> QColor:
        return self._ring_color

    def set_ring_color(self, color: QColor) -> None:
        self._ring_color = color
        self.update()

    ringColor = Property(QColor, get_ring_color, set_ring_color)

    def set_track_color(self, color: QColor) -> None:
        self._track_color = color
        self.update()

    def animate_to_color(self, color: QColor) -> None:
        self._color_anim.stop()
        self._color_anim.setStartValue(self._ring_color)
        self._color_anim.setEndValue(color)
        self._color_anim.start()

    def set_texts(self, center_text: str, sub_text: str = "") -> None:
        self._center_text = center_text
        self._sub_text = sub_text
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height())
        margin = self._stroke_width / 2 + 2
        rect = QRectF(
            (self.width() - side) / 2 + margin,
            (self.height() - side) / 2 + margin,
            side - margin * 2,
            side - margin * 2,
        )

        # Track
        track_pen = QPen(self._track_color)
        track_pen.setWidth(self._stroke_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Progress arc, starting at 12 o'clock, clockwise
        if self._progress > 0:
            ring_pen = QPen(self._ring_color)
            ring_pen.setWidth(self._stroke_width)
            ring_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(ring_pen)
            span = int(-360 * 16 * self._progress)
            painter.drawArc(rect, 90 * 16, span)

        # Center countdown text
        painter.setPen(QColor("#edf1f6"))
        center_font = QFont(FONT_FAMILY_MONO.split(",")[0].strip('"'))
        center_font.setPixelSize(int(side * 0.19))
        center_font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(center_font)
        text_rect = rect.adjusted(0, -side * 0.06, 0, -side * 0.06)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._center_text)

        if self._sub_text:
            sub_font = QFont()
            sub_font.setPixelSize(int(side * 0.05))
            sub_font.setWeight(QFont.Weight.Medium)
            painter.setFont(sub_font)
            painter.setPen(QColor("#9aa8b8"))
            sub_rect = rect.adjusted(0, side * 0.14, 0, side * 0.14)
            painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, self._sub_text)


class MiniBarChart(QWidget):
    """A small, dependency-free bar chart used for the last-7-days overview."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._values: list[float] = []
        self._labels: list[str] = []
        self._bar_color = QColor("#4f8cff")
        self.setMinimumHeight(140)

    def set_data(self, labels: list[str], values: list[float], color: QColor) -> None:
        self._labels = labels
        self._values = values
        self._bar_color = color
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._values:
            return

        width = self.width()
        height = self.height()
        label_height = 18
        chart_height = height - label_height
        max_value = max(self._values) or 1.0

        n = len(self._values)
        gap = 10
        bar_width = max((width - gap * (n + 1)) / n, 4)

        painter.setPen(QColor("#697687"))
        font = QFont()
        font.setPixelSize(10)
        painter.setFont(font)

        for i, (value, label) in enumerate(zip(self._values, self._labels)):
            x = gap + i * (bar_width + gap)
            bar_h = (value / max_value) * (chart_height - 8) if max_value else 0
            bar_h = max(bar_h, 3 if value > 0 else 0)
            y = chart_height - bar_h

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._bar_color)
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_h), 4, 4)

            painter.setPen(QColor("#697687"))
            painter.drawText(
                QRectF(x - gap / 2, chart_height + 2, bar_width + gap, label_height),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )
