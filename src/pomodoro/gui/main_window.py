"""The application's main window: header, Timer/Statistics tabs."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget

from ..audio import SoundPlayer
from ..persistence import HistoryStore, SettingsStore
from .stats_view import StatsView
from .theme import WINDOW_SIZE, build_stylesheet, themes_by_name
from .timer_view import TimerView


class MainWindow(QMainWindow):
    def __init__(self, sounds_dir: Path) -> None:
        super().__init__()
        self.setWindowTitle("Pomodoro")
        self.setFixedSize(*WINDOW_SIZE)

        self.settings = SettingsStore()
        self.history = HistoryStore()
        self.sound_player = SoundPlayer(sounds_dir)

        self._themes = themes_by_name()
        self.tokens = self._themes.get(self.settings.theme, self._themes["dark"])

        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        root_widget = QWidget()
        root_widget.setObjectName("rootView")
        self.setCentralWidget(root_widget)

        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(24, 18, 24, 0)
        root_layout.setSpacing(0)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("POMODORO")
        title.setObjectName("appTitle")
        subtitle = QLabel("Fokus. Pause. Fortschritt.")
        subtitle.setObjectName("appSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.theme_button = QPushButton("☀️ Hell" if self.tokens.name == "dark" else "🌙 Dunkel")
        self.theme_button.setObjectName("ghostButton")
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.clicked.connect(self._toggle_theme)
        header.addWidget(self.theme_button)

        root_layout.addLayout(header)

        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs)

        self.timer_view = TimerView(self.settings, self.history, self.sound_player, self.tokens)
        self.stats_view = StatsView(self.history, self.tokens)
        self.timer_view.stats_changed.connect(self.stats_view.refresh)

        self.tabs.addTab(self.timer_view, "Timer")
        self.tabs.addTab(self.stats_view, "Statistik")
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int) -> None:
        if self.tabs.widget(index) is self.stats_view:
            self.stats_view.refresh()

    def _toggle_theme(self) -> None:
        new_name = "light" if self.tokens.name == "dark" else "dark"
        self.tokens = self._themes[new_name]
        self.settings.theme = new_name
        self.settings.save()
        self._apply_theme()

    def _apply_theme(self) -> None:
        self.setStyleSheet(build_stylesheet(self.tokens))
        self.theme_button.setText("☀️ Hell" if self.tokens.name == "dark" else "🌙 Dunkel")
        self.timer_view.apply_theme(self.tokens)
        self.stats_view.apply_theme(self.tokens)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        self.settings.save()
        self.history.close()
        super().closeEvent(event)
