# Pomodoro

A native, modern-looking Pomodoro timer for macOS. Run it from the
terminal with a single command, or bundle it into a double-clickable
`Pomodoro.app` (see [below](#building-a-double-clickable-macos-app)) — either
way it opens its own desktop window, built with
[PySide6](https://doc.qt.io/qtforpython/), where you configure your
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

## Building a double-clickable macOS app

If you'd rather launch Pomodoro from the Dock / Launchpad than from a
terminal, bundle it into a standalone `Pomodoro.app` with
[PyInstaller](https://pyinstaller.org/):

```bash
./packaging/build.sh
```

That script installs the build dependency (`pip install -e ".[package]"`),
renders the app icon, runs PyInstaller against
[`packaging/Pomodoro.spec`](packaging/Pomodoro.spec), and ad-hoc code-signs
the result (required to run on Apple Silicon). When it finishes:

```bash
cp -R dist/Pomodoro.app /Applications/
open /Applications/Pomodoro.app
```

The bundle is self-contained — it ships its own Python and Qt, so it runs
on any Mac (macOS 11+) without a Python install. Pass `--dmg` to also get
a `dist/Pomodoro.dmg` for copying it to another machine:

```bash
./packaging/build.sh --dmg
```

Because the app isn't signed with an Apple Developer ID, the first launch
on another Mac needs a right-click → **Open** (or *System Settings →
Privacy & Security → Open Anyway*) to get past Gatekeeper. On the machine
that built it, it just opens.

The phase-end sounds and all settings/history work exactly as in the
terminal version — see the two sections below.

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

**In the packaged `Pomodoro.app`**, whatever `sounds/` files were present
at build time are bundled inside the app. To swap them afterwards without
rebuilding, drop `focus_end.mp3` / `break_end.mp3` into
`~/Library/Application Support/Pomodoro/sounds/` — that location is
checked first and wins over the bundled copies.

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
├── cli.py         # `pomodoro` entry point
└── __main__.py    # `python -m pomodoro`
tests/             # unit tests for the timer state machine
sounds/            # drop-in folder for focus_end.mp3 / break_end.mp3
packaging/         # PyInstaller spec, icon generator, build.sh → Pomodoro.app
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
