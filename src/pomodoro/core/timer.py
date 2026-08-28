"""Pure Python Pomodoro state machine.

This module has no dependency on Qt, threads, or wall-clock time: it is
driven entirely by calls to :meth:`TimerEngine.tick`, which makes it
trivial to unit test and reuse from any front end (GUI, CLI, ...).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class Phase(Enum):
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class RunState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass(slots=True)
class TimerConfig:
    """User-configurable durations and round structure."""

    focus_minutes: float = 25.0
    break_minutes: float = 5.0
    long_break_minutes: float = 15.0
    rounds: int = 4
    long_break_enabled: bool = True
    long_break_interval: int = 4

    def phase_duration_seconds(self, phase: Phase) -> float:
        if phase is Phase.FOCUS:
            return max(self.focus_minutes, 0.0) * 60
        if phase is Phase.LONG_BREAK:
            return max(self.long_break_minutes, 0.0) * 60
        return max(self.break_minutes, 0.0) * 60


@dataclass(slots=True)
class PhaseEvent:
    """Emitted whenever a phase finishes naturally (its countdown hit zero)."""

    phase: Phase
    round_number: int


class TimerEngine:
    """A Focus -> Break -> Focus -> ... state machine that always ends on Focus.

    Drive it from any event loop by calling :meth:`tick` with the elapsed
    number of seconds since the previous tick (e.g. from a 1s ``QTimer``).
    """

    def __init__(
        self,
        config: TimerConfig,
        on_phase_complete: Optional[Callable[[PhaseEvent], None]] = None,
        on_session_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self.config = config
        self.on_phase_complete = on_phase_complete
        self.on_session_complete = on_session_complete
        self.state: RunState = RunState.IDLE
        self.phase: Phase = Phase.FOCUS
        self.round_number: int = 1
        self.remaining_seconds: float = config.phase_duration_seconds(Phase.FOCUS)

    @property
    def total_seconds(self) -> float:
        return self.config.phase_duration_seconds(self.phase)

    @property
    def progress(self) -> float:
        """Fraction of the current phase elapsed, in ``[0, 1]``."""
        total = self.total_seconds
        if total <= 0:
            return 1.0
        return min(max(1.0 - (self.remaining_seconds / total), 0.0), 1.0)

    def start(self) -> None:
        if self.state in (RunState.IDLE, RunState.PAUSED):
            self.state = RunState.RUNNING

    def pause(self) -> None:
        if self.state is RunState.RUNNING:
            self.state = RunState.PAUSED

    def resume(self) -> None:
        self.start()

    def toggle_pause(self) -> None:
        if self.state is RunState.RUNNING:
            self.pause()
        elif self.state is RunState.PAUSED:
            self.resume()

    def stop(self) -> None:
        """Abort the current session and reset back to a fresh, idle Focus 1/N."""
        self.state = RunState.IDLE
        self.phase = Phase.FOCUS
        self.round_number = 1
        self.remaining_seconds = self.config.phase_duration_seconds(Phase.FOCUS)

    def apply_config(self, config: TimerConfig) -> None:
        """Replace the config. Only takes effect immediately while idle."""
        self.config = config
        if self.state is RunState.IDLE:
            self.remaining_seconds = config.phase_duration_seconds(self.phase)

    def tick(self, delta_seconds: float) -> None:
        if self.state is not RunState.RUNNING or delta_seconds <= 0:
            return
        self.remaining_seconds -= delta_seconds
        # A while-loop (rather than a single if) guards against a very large
        # delta_seconds skipping over more than one phase boundary at once.
        while self.remaining_seconds <= 0 and self.state is RunState.RUNNING:
            overshoot = -self.remaining_seconds
            self._advance_phase()
            self.remaining_seconds -= overshoot

    def _next_phase_after_focus(self) -> Phase:
        if self.config.long_break_enabled and self.config.long_break_interval > 0:
            if self.round_number % self.config.long_break_interval == 0:
                return Phase.LONG_BREAK
        return Phase.SHORT_BREAK

    def _advance_phase(self) -> None:
        finished_phase = self.phase
        finished_round = self.round_number

        if self.on_phase_complete is not None:
            self.on_phase_complete(PhaseEvent(finished_phase, finished_round))

        if finished_phase is Phase.FOCUS:
            if finished_round >= self.config.rounds:
                self.state = RunState.FINISHED
                self.remaining_seconds = 0.0
                if self.on_session_complete is not None:
                    self.on_session_complete()
                return
            self.phase = self._next_phase_after_focus()
        else:
            self.round_number += 1
            self.phase = Phase.FOCUS

        self.remaining_seconds = self.config.phase_duration_seconds(self.phase)
