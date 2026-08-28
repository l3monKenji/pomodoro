"""The Statistics tab: totals, a 7-day overview chart, and tag filtering."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..persistence import HistoryStore
from .theme import ThemeTokens
from .widgets import MiniBarChart

_WEEKDAY_ABBR = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def _card() -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    return frame


def _format_minutes(minutes: float) -> str:
    total = round(minutes)
    hours, mins = divmod(total, 60)
    if hours:
        return f"{hours}h {mins:02d}m"
    return f"{mins} min"


class _StatTile(QFrame):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        self.value_label = QLabel("0 min")
        self.value_label.setObjectName("statValue")
        layout.addWidget(self.value_label)

        caption = QLabel(label)
        caption.setObjectName("statLabel")
        layout.addWidget(caption)

        self.count_label = QLabel("0 Runden")
        self.count_label.setObjectName("hintLabel")
        layout.addWidget(self.count_label)

    def set_values(self, minutes: float, count: int) -> None:
        self.value_label.setText(_format_minutes(minutes))
        self.count_label.setText(f"{count} Runde{'n' if count != 1 else ''}")


class StatsView(QWidget):
    def __init__(self, history: HistoryStore, tokens: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.history = history
        self.tokens = tokens
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)
        self.today_tile = _StatTile("HEUTE")
        self.week_tile = _StatTile("DIESE WOCHE")
        self.total_tile = _StatTile("GESAMT")
        tiles_row.addWidget(self.today_tile)
        tiles_row.addWidget(self.week_tile)
        tiles_row.addWidget(self.total_tile)
        root.addLayout(tiles_row)

        chart_card = _card()
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(24, 20, 24, 20)
        chart_layout.setSpacing(12)

        header_row = QHBoxLayout()
        chart_title = QLabel("LETZTE 7 TAGE")
        chart_title.setObjectName("cardTitle")
        header_row.addWidget(chart_title)
        header_row.addStretch()

        header_row.addWidget(QLabel("Filter:"))
        self.tag_filter = QComboBox()
        self.tag_filter.addItem("Alle Projekte", userData=None)
        self.tag_filter.currentIndexChanged.connect(self.refresh)
        header_row.addWidget(self.tag_filter)
        chart_layout.addLayout(header_row)

        self.chart = MiniBarChart()
        chart_layout.addWidget(self.chart)

        root.addWidget(chart_card)
        root.addStretch()

        footer_row = QHBoxLayout()
        footer_row.addStretch()
        self.reset_button = QPushButton("Historie zurücksetzen")
        self.reset_button.setObjectName("dangerButton")
        self.reset_button.clicked.connect(self._on_reset_clicked)
        footer_row.addWidget(self.reset_button)
        root.addLayout(footer_row)

    def _current_tag_filter(self) -> str | None:
        return self.tag_filter.currentData()

    def refresh(self) -> None:
        selected = self._current_tag_filter()

        self.tag_filter.blockSignals(True)
        self.tag_filter.clear()
        self.tag_filter.addItem("Alle Projekte", userData=None)
        for tag in self.history.distinct_tags():
            self.tag_filter.addItem(tag, userData=tag)
        index = self.tag_filter.findData(selected)
        self.tag_filter.setCurrentIndex(index if index >= 0 else 0)
        self.tag_filter.blockSignals(False)

        tag = self._current_tag_filter()
        summary = self.history.summary(tag)
        self.today_tile.set_values(summary.today_minutes, summary.today_count)
        self.week_tile.set_values(summary.week_minutes, summary.week_count)
        self.total_tile.set_values(summary.total_minutes, summary.total_count)

        daily = self.history.daily_totals(days=7, tag=tag)
        labels = [_WEEKDAY_ABBR[d.weekday()] for d, _ in daily]
        values = [minutes for _, minutes in daily]
        self.chart.set_data(labels, values, QColor(self.tokens.focus))

    def _on_reset_clicked(self) -> None:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Historie zurücksetzen")
        box.setText("Möchtest du wirklich die komplette Statistik-Historie löschen?")
        box.setInformativeText("Dieser Vorgang kann nicht rückgängig gemacht werden.")
        box.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes)
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if box.exec() == QMessageBox.StandardButton.Yes:
            self.history.reset()
            self.refresh()

    def apply_theme(self, tokens: ThemeTokens) -> None:
        self.tokens = tokens
        self.refresh()
