"""QApplication bootstrap."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ..audio import default_sounds_dir
from .assets import logo_pixmap
from .main_window import MainWindow


def run(sounds_dir: Path | None = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Pomodoro")
    app.setOrganizationName("L3monKenji")
    app.setWindowIcon(QIcon(logo_pixmap(256)))

    window = MainWindow(sounds_dir or default_sounds_dir())
    window.show()
    return app.exec()
