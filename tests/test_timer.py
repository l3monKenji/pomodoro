"""Unit tests for the GUI-independent timer state machine."""

from __future__ import annotations

import unittest

from pomodoro.core.timer import Phase, PhaseEvent, RunState, TimerConfig, TimerEngine


def make_engine(**overrides) -> tuple[TimerEngine, list[PhaseEvent], list[None]]:
    config = TimerConfig(
        focus_minutes=1,
        break_minutes=1,
        long_break_minutes=2,
        rounds=4,
        long_break_enabled=True,
        long_break_interval=2,
    )
    for key, value in overrides.items():
        setattr(config, key, value)

    phase_events: list[PhaseEvent] = []
    session_completions: list[None] = []
    engine = TimerEngine(
        config,
        on_phase_complete=phase_events.append,
        on_session_complete=lambda: session_completions.append(None),
    )
    return engine, phase_events, session_completions


class TimerEngineTests(unittest.TestCase):
    def test_idle_engine_does_not_tick(self) -> None:
        engine, events, _ = make_engine()
        engine.tick(30)
        self.assertEqual(engine.state, RunState.IDLE)
        self.assertEqual(engine.remaining_seconds, 60)
        self.assertEqual(events, [])

    def test_focus_round_completes_and_moves_to_break(self) -> None:
        engine, events, _ = make_engine()
        engine.start()
        engine.tick(60)

        self.assertEqual(engine.phase, Phase.SHORT_BREAK)
        self.assertEqual(engine.round_number, 1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], PhaseEvent(Phase.FOCUS, 1))

    def test_long_break_inserted_at_configured_interval(self) -> None:
        engine, events, _ = make_engine(long_break_interval=2)
        engine.start()
        # Focus 1 -> short break
        engine.tick(60)
        self.assertEqual(engine.phase, Phase.SHORT_BREAK)
        # short break -> Focus 2
        engine.tick(60)
        self.assertEqual(engine.phase, Phase.FOCUS)
        self.assertEqual(engine.round_number, 2)
        # Focus 2 -> long break (round 2 % interval 2 == 0)
        engine.tick(60)
        self.assertEqual(engine.phase, Phase.LONG_BREAK)

    def test_session_always_ends_on_focus_never_on_break(self) -> None:
        engine, events, completions = make_engine(rounds=2, long_break_enabled=False)
        engine.start()
        engine.tick(60)  # focus 1 -> break
        engine.tick(60)  # break -> focus 2
        self.assertEqual(engine.phase, Phase.FOCUS)
        self.assertEqual(engine.round_number, 2)

        engine.tick(60)  # focus 2 -> session finished
        self.assertEqual(engine.state, RunState.FINISHED)
        self.assertEqual(len(completions), 1)
        focus_events = [e for e in events if e.phase is Phase.FOCUS]
        self.assertEqual(len(focus_events), 2)

    def test_pause_freezes_remaining_time(self) -> None:
        engine, _, _ = make_engine()
        engine.start()
        engine.tick(10)
        engine.pause()
        remaining_before = engine.remaining_seconds
        engine.tick(10)
        self.assertEqual(engine.remaining_seconds, remaining_before)
        self.assertEqual(engine.state, RunState.PAUSED)

    def test_resume_continues_from_paused_remaining_time(self) -> None:
        engine, _, _ = make_engine()
        engine.start()
        engine.tick(10)
        engine.pause()
        engine.resume()
        engine.tick(10)
        self.assertEqual(engine.remaining_seconds, 40)

    def test_stop_resets_to_fresh_idle_focus_round_one(self) -> None:
        engine, _, _ = make_engine()
        engine.start()
        engine.tick(60)  # into break
        engine.tick(30)
        engine.stop()

        self.assertEqual(engine.state, RunState.IDLE)
        self.assertEqual(engine.phase, Phase.FOCUS)
        self.assertEqual(engine.round_number, 1)
        self.assertEqual(engine.remaining_seconds, 60)

    def test_progress_reflects_elapsed_fraction(self) -> None:
        engine, _, _ = make_engine()
        engine.start()
        engine.tick(30)
        self.assertAlmostEqual(engine.progress, 0.5)

    def test_overshoot_across_multiple_phase_boundaries_in_one_tick(self) -> None:
        engine, events, _ = make_engine(rounds=3, long_break_enabled=False)
        engine.start()
        # A single large tick spans focus1 -> break -> focus2 in one call.
        engine.tick(150)
        self.assertEqual(engine.phase, Phase.FOCUS)
        self.assertEqual(engine.round_number, 2)
        self.assertEqual(engine.remaining_seconds, 30)
        self.assertEqual(len(events), 2)


if __name__ == "__main__":
    unittest.main()
