"""The main Timer tab: countdown ring, phase/round status, controls, settings."""

from __future__ import annotations

import math

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..audio import SoundPlayer, send_notification
from ..core.timer import Phase, PhaseEvent, RunState, TimerConfig, TimerEngine
from ..persistence import HistoryStore, SettingsStore
from .theme import ThemeTokens
from .widgets import ProgressRing

_TICK_INTERVAL_MS = 250
_TICK_DELTA_SECONDS = _TICK_INTERVAL_MS / 1000

_PHASE_LABELS = {
    Phase.FOCUS: "FOKUS",
    Phase.SHORT_BREAK: "PAUSE",
    Phase.LONG_BREAK: "LANGE PAUSE",
}

_START_LABELS = {
    RunState.IDLE: "Start",
    RunState.RUNNING: "Pause",
    RunState.PAUSED: "Fortsetzen",
    RunState.FINISHED: "Neue Session",
}


def _card() -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    return frame


class TimerView(QWidget):
    stats_changed = Signal()

    def __init__(
        self,
        settings: SettingsStore,
        history: HistoryStore,
        sound_player: SoundPlayer,
        tokens: ThemeTokens,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.history = history
        self.sound_player = sound_player
        self.tokens = tokens
        self._sound_hint_shown = False
        self._last_phase: Phase | None = None

        self.engine = TimerEngine(
            settings.config,
            on_phase_complete=self._on_phase_complete,
            on_session_complete=self._on_session_complete,
        )

        self._build_ui()
        self._wire_qtimer()
        self._refresh_display(force=True)

    # -- layout -------------------------------------------------------
    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        root.addWidget(self._build_timer_card(), 3)
        root.addWidget(self._build_settings_card(), 2)

    def _build_timer_card(self) -> QFrame:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.phase_label = QLabel(_PHASE_LABELS[Phase.FOCUS])
        self.phase_label.setObjectName("phaseLabel")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._phase_opacity = QGraphicsOpacityEffect(self.phase_label)
        self.phase_label.setGraphicsEffect(self._phase_opacity)
        self._phase_fade_anim = QPropertyAnimation(self._phase_opacity, b"opacity", self)
        self._phase_fade_anim.setDuration(350)
        self._phase_fade_anim.setStartValue(0.0)
        self._phase_fade_anim.setEndValue(1.0)
        self._phase_fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        layout.addWidget(self.phase_label)

        self.round_label = QLabel("Runde 1/4")
        self.round_label.setObjectName("roundLabel")
        self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.round_label)

        layout.addSpacing(12)

        self.ring = ProgressRing(diameter=300, stroke_width=14)
        self.ring.set_ring_color(QColor(self.tokens.focus))
        self.ring.set_track_color(QColor(self.tokens.focus_soft))
        ring_row = QHBoxLayout()
        ring_row.addStretch()
        ring_row.addWidget(self.ring)
        ring_row.addStretch()
        layout.addLayout(ring_row)

        layout.addSpacing(16)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(12)
        controls_row.addStretch()

        self.start_pause_button = QPushButton(_START_LABELS[RunState.IDLE])
        self.start_pause_button.setObjectName("primaryButton")
        self.start_pause_button.setMinimumWidth(150)
        self.start_pause_button.clicked.connect(self._on_start_pause_clicked)
        controls_row.addWidget(self.start_pause_button)

        self.stop_button = QPushButton("Abbrechen")
        self.stop_button.setObjectName("secondaryButton")
        self.stop_button.setMinimumWidth(120)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        controls_row.addWidget(self.stop_button)

        controls_row.addStretch()
        layout.addLayout(controls_row)

        self.hint_label = QLabel("")
        self.hint_label.setObjectName("hintLabel")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        layout.addSpacing(10)
        layout.addWidget(self.hint_label)

        return card

    def _build_settings_card(self) -> QFrame:
        card = _card()
        outer = QVBoxLayout(card)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(14)

        title = QLabel("EINSTELLUNGEN")
        title.setObjectName("cardTitle")
        outer.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        cfg = self.settings.config

        self.focus_spin = QSpinBox()
        self.focus_spin.setRange(1, 180)
        self.focus_spin.setSuffix(" min")
        self.focus_spin.setValue(int(cfg.focus_minutes))
        form.addRow("Fokuszeit", self.focus_spin)

        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setSuffix(" min")
        self.break_spin.setValue(int(cfg.break_minutes))
        form.addRow("Pausenzeit", self.break_spin)

        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 12)
        self.rounds_spin.setValue(cfg.rounds)
        form.addRow("Rundenanzahl", self.rounds_spin)

        self.long_break_checkbox = QCheckBox("Lange Pause aktivieren")
        self.long_break_checkbox.setChecked(cfg.long_break_enabled)
        form.addRow(self.long_break_checkbox)

        self.long_break_interval_spin = QSpinBox()
        self.long_break_interval_spin.setRange(2, 10)
        self.long_break_interval_spin.setSuffix(" Runden")
        self.long_break_interval_spin.setValue(cfg.long_break_interval)
        form.addRow("Lange Pause alle", self.long_break_interval_spin)

        self.long_break_minutes_spin = QSpinBox()
        self.long_break_minutes_spin.setRange(5, 60)
        self.long_break_minutes_spin.setSuffix(" min")
        self.long_break_minutes_spin.setValue(int(cfg.long_break_minutes))
        form.addRow("Lange Pause Dauer", self.long_break_minutes_spin)

        self.tag_input = QLineEdit(self.settings.last_tag)
        self.tag_input.setPlaceholderText("z. B. Kundenprojekt (optional)")
        form.addRow("Projekt/Label", self.tag_input)

        outer.addLayout(form)
        outer.addStretch()

        self._settings_widgets = [
            self.focus_spin,
            self.break_spin,
            self.rounds_spin,
            self.long_break_checkbox,
            self.long_break_interval_spin,
            self.long_break_minutes_spin,
        ]
        for widget in self._settings_widgets:
            if isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._on_settings_changed)
            elif isinstance(widget, QCheckBox):
                widget.toggled.connect(self._on_settings_changed)
        self.long_break_checkbox.toggled.connect(self._update_long_break_enabled_state)
        self.tag_input.editingFinished.connect(self._on_tag_changed)
        self._update_long_break_enabled_state(cfg.long_break_enabled)

        return card

    # -- qtimer wiring --------------------------------------------------
    def _wire_qtimer(self) -> None:
        self._qtimer = QTimer(self)
        self._qtimer.setInterval(_TICK_INTERVAL_MS)
        self._qtimer.timeout.connect(self._on_tick)
        self._qtimer.start()

    def _on_tick(self) -> None:
        self.engine.tick(_TICK_DELTA_SECONDS)
        self._refresh_display()

    # -- engine callbacks (invoked synchronously from the GUI thread) --
    def _on_phase_complete(self, event: PhaseEvent) -> None:
        if event.phase is Phase.FOCUS:
            tag = self.tag_input.text().strip()
            self.history.record_focus_round(self.engine.config.focus_minutes, tag)
            played = self.sound_player.play("focus_end.mp3")
            send_notification(
                "Fokus-Runde beendet",
                f"Runde {event.round_number}/{self.engine.config.rounds} abgeschlossen.",
            )
            self.stats_changed.emit()
        else:
            played = self.sound_player.play("break_end.mp3")
            label = "Lange Pause" if event.phase is Phase.LONG_BREAK else "Pause"
            send_notification(f"{label} beendet", "Zeit für die nächste Fokus-Runde.")

        if not played and not self._sound_hint_shown:
            self._sound_hint_shown = True
            self.hint_label.setText(
                "Keine Sound-Datei gefunden – lege MP3s unter sounds/ ab (siehe sounds/README.md)."
            )

    def _on_session_complete(self) -> None:
        send_notification("Session abgeschlossen", "Alle Runden geschafft — großartige Arbeit!")

    # -- controls ---------------------------------------------------
    def _on_start_pause_clicked(self) -> None:
        state = self.engine.state
        if state is RunState.IDLE:
            self.engine.start()
        elif state is RunState.RUNNING:
            self.engine.pause()
        elif state is RunState.PAUSED:
            self.engine.resume()
        elif state is RunState.FINISHED:
            self.engine.stop()
            self.engine.start()
        self._refresh_display()

    def _on_stop_clicked(self) -> None:
        self.engine.stop()
        self._refresh_display(force=True)

    def _on_settings_changed(self) -> None:
        config = TimerConfig(
            focus_minutes=float(self.focus_spin.value()),
            break_minutes=float(self.break_spin.value()),
            long_break_minutes=float(self.long_break_minutes_spin.value()),
            rounds=self.rounds_spin.value(),
            long_break_enabled=self.long_break_checkbox.isChecked(),
            long_break_interval=self.long_break_interval_spin.value(),
        )
        self.engine.apply_config(config)
        self.settings.config = config
        self.settings.save()
        self._refresh_display(force=True)

    def _on_tag_changed(self) -> None:
        self.settings.last_tag = self.tag_input.text().strip()
        self.settings.save()

    def _update_long_break_enabled_state(self, enabled: bool) -> None:
        self.long_break_interval_spin.setEnabled(enabled)
        self.long_break_minutes_spin.setEnabled(enabled)

    # -- display ------------------------------------------------------
    def _phase_color(self, phase: Phase) -> tuple[QColor, QColor]:
        if phase is Phase.FOCUS:
            return QColor(self.tokens.focus), QColor(self.tokens.focus_soft)
        return QColor(self.tokens.break_), QColor(self.tokens.break_soft)

    def _refresh_display(self, force: bool = False) -> None:
        engine = self.engine
        phase_changed = force or engine.phase != self._last_phase

        remaining = max(0, math.ceil(engine.remaining_seconds - 1e-9))
        minutes, seconds = divmod(remaining, 60)
        self.ring.set_texts(f"{minutes:02d}:{seconds:02d}")
        self.ring.set_progress(engine.progress)

        if engine.state is RunState.FINISHED:
            self.phase_label.setText("SESSION FERTIG")
            self.round_label.setText(f"{engine.config.rounds} Runden abgeschlossen 🎉")
        else:
            self.phase_label.setText(_PHASE_LABELS[engine.phase])
            self.round_label.setText(f"Runde {engine.round_number}/{engine.config.rounds}")

        if phase_changed:
            color, track = self._phase_color(engine.phase)
            self.ring.animate_to_color(color)
            self.ring.set_track_color(track)
            self._phase_fade_anim.stop()
            self._phase_fade_anim.start()
            self._last_phase = engine.phase

        self.start_pause_button.setText(_START_LABELS[engine.state])
        self.stop_button.setEnabled(engine.state is not RunState.IDLE)

        settings_enabled = engine.state in (RunState.IDLE, RunState.FINISHED)
        for widget in self._settings_widgets:
            widget.setEnabled(
                settings_enabled
                if widget is not self.long_break_interval_spin and widget is not self.long_break_minutes_spin
                else settings_enabled and self.long_break_checkbox.isChecked()
            )

    def apply_theme(self, tokens: ThemeTokens) -> None:
        self.tokens = tokens
        color, track = self._phase_color(self.engine.phase)
        self.ring.set_ring_color(color)
        self.ring.set_track_color(track)
