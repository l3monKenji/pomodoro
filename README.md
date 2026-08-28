# Pomodoro

A native, modern-looking Pomodoro timer for macOS. Started from the
terminal with a single command, it opens its own desktop window — built
with [PySide6](https://doc.qt.io/qtforpython/) — where you configure your
session, watch a live countdown, and review your focus history.

> pomodoro timer for deepwork and efficency - but mainly for testing DevSecOps stuff ;)

## Why it looks the way it looks

The UI leans on a small, deliberate color idea instead of a generic theme:

- **Blue** is the primary color and the color of the **Focus** phase. Blue
  is associated with calm and analytical thinking, so it's the color you
  spend most of your time looking at.
- **Green** is the secondary/accent color and marks the **Break** phase
  and positive states (completed rounds). Green reads as restorative
  without being attention-grabbing.
- **Neutral dark tones** make up the rest of the interface so the blue and
  green accents stay legible instead of competing with other colors.
- **Red/amber are avoided** almost entirely and reserved for the one
  destructive action in the app (resetting your history).

A light theme is available too (toggle in the top-right corner) using the
same palette logic, for anyone who prefers it.

All colors, spacing, and typography are defined once as design tokens in
[`src/pomodoro/gui/theme.py`](src/pomodoro/gui/theme.py), so the whole
look can be retuned from a single file.

## Features

- Configurable Focus time, Break time, round count, and an optional long
  break every N rounds (classic Pomodoro structure) — the session always
  ends on a Focus round, never a Break.
- A large, animated progress ring with a live `mm:ss` countdown; the ring
  and phase label transition smoothly between the blue Focus color and
  the green Break color.
- Start / Pause / Resume / Cancel controls; the current phase's settings
  are locked while a round is running so you can't accidentally derail an
  in-progress countdown.
- Audio signal at the end of every Focus round and every Break (two
  distinct sounds), plus optional macOS notifications on each phase
  change.
- A Statistics tab with today / this week / all-time totals, a completed
  round count, a 7-day bar chart, optional per-project tag filtering, and
  a (confirmation-gated) history reset.
- Settings and history persist automatically between launches — nothing
  is lost if you quit mid-session (only fully completed Focus rounds are
  recorded, so an aborted round simply isn't counted).

## Installation

Requires Python 3.10+ on macOS.

```bash
git clone <this repo>
cd pomodoro
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `pomodoro` console command (via the entry point defined
in `pyproject.toml`) into your active environment.

## Starting it

```bash
pomodoro
```

This opens the app window. Configure Focus/Break minutes, round count,
and the optional long break in the "Einstellungen" panel, then hit
**Start**. Switch to the **Statistik** tab any time to see your history.

## Adding your own sounds

The app plays an MP3 at the end of each Focus round and each Break. Drop
your own files into [`sounds/`](sounds/) using these exact names:

| File             | Played when...                 |
|-------------------|--------------------------------|
| `focus_end.mp3`  | a Focus round finishes          |
| `break_end.mp3`  | a short or long Break finishes  |

No MP3s are shipped in this repo (see [`sounds/README.md`](sounds/README.md)).
Without them the app doesn't crash — it just falls back to a terminal
beep and shows a small hint in the window. The lookup folder can be
overridden with the `POMODORO_SOUNDS_DIR` environment variable.

## Configuration & data storage

Settings (last-used timer configuration, theme, project tag) and your
focus history are stored automatically under:

```
~/Library/Application Support/Pomodoro/
├── settings.json   # last-used configuration (JSON)
└── pomodoro.db      # completed focus rounds (SQLite)
```

Every focus round you *fully complete* is appended to `pomodoro.db` with
its timestamp, duration, and optional project tag — that's the data the
Statistics tab aggregates into "today / this week / all-time" totals and
the 7-day chart. You can wipe this history from inside the app
(Statistik tab → "Historie zurücksetzen"), which asks for confirmation
first since it can't be undone.

## Project layout

```
src/pomodoro/
├── core/          # timer.py — GUI-independent state machine (Focus/Break/rounds)
├── persistence/   # settings.py (JSON) and history.py (SQLite)
├── audio/         # MP3 playback (afplay) + macOS notifications (osascript)
├── gui/           # PySide6 window: theme tokens, widgets, timer & stats tabs
└── cli.py         # `pomodoro` entry point
tests/             # unit tests for the timer state machine
sounds/            # drop-in folder for focus_end.mp3 / break_end.mp3
```

The timer logic in `core/timer.py` has no Qt dependency and is fully
unit-tested (`tests/test_timer.py`) — the GUI drives it by calling
`TimerEngine.tick()` from a `QTimer`, which keeps the countdown from ever
blocking the window.

## Running the tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
