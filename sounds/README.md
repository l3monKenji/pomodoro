# Sounds

Drop your own MP3 files in this folder to enable audio signals. The app
looks them up by fixed file name:

| File               | Played when...                          |
|--------------------|------------------------------------------|
| `focus_end.mp3`    | a focus round finishes                    |
| `break_end.mp3`    | a short or long break finishes            |

Notes:

- Files are optional. If a file is missing (or `afplay` isn't available),
  the app falls back silently to a terminal bell instead of crashing, and
  shows a small hint in the window so you know sounds are disabled.
- Any MP3 works — keep them short (1-3s) so they don't overlap the next
  phase's countdown.
- Playback uses macOS's built-in `afplay`, so no extra audio dependency is
  required.
