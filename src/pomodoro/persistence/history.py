"""SQLite-backed persistence for completed focus rounds and their stats."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from .paths import app_data_dir

_DB_FILENAME = "pomodoro.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    completed_at TEXT NOT NULL,
    duration_minutes REAL NOT NULL,
    tag TEXT
);
"""


@dataclass(slots=True)
class SessionRecord:
    completed_at: datetime
    duration_minutes: float
    tag: str


@dataclass(slots=True)
class StatsSummary:
    today_minutes: float = 0.0
    today_count: int = 0
    week_minutes: float = 0.0
    week_count: int = 0
    total_minutes: float = 0.0
    total_count: int = 0


class HistoryStore:
    """Append-only log of completed focus rounds, plus derived statistics."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (app_data_dir() / _DB_FILENAME)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def record_focus_round(self, duration_minutes: float, tag: str = "") -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO focus_sessions (completed_at, duration_minutes, tag) VALUES (?, ?, ?)",
                (datetime.now().isoformat(timespec="seconds"), duration_minutes, tag or ""),
            )

    def _rows(self, tag: str | None = None) -> list[SessionRecord]:
        if tag:
            cursor = self._conn.execute(
                "SELECT completed_at, duration_minutes, tag FROM focus_sessions WHERE tag = ? ORDER BY completed_at",
                (tag,),
            )
        else:
            cursor = self._conn.execute(
                "SELECT completed_at, duration_minutes, tag FROM focus_sessions ORDER BY completed_at"
            )
        return [
            SessionRecord(datetime.fromisoformat(completed_at), duration_minutes, tag or "")
            for completed_at, duration_minutes, tag in cursor.fetchall()
        ]

    def distinct_tags(self) -> list[str]:
        cursor = self._conn.execute(
            "SELECT DISTINCT tag FROM focus_sessions WHERE tag IS NOT NULL AND tag != '' ORDER BY tag"
        )
        return [row[0] for row in cursor.fetchall()]

    def summary(self, tag: str | None = None) -> StatsSummary:
        rows = self._rows(tag)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday

        summary = StatsSummary()
        for row in rows:
            summary.total_minutes += row.duration_minutes
            summary.total_count += 1
            row_date = row.completed_at.date()
            if row_date == today:
                summary.today_minutes += row.duration_minutes
                summary.today_count += 1
            if row_date >= week_start:
                summary.week_minutes += row.duration_minutes
                summary.week_count += 1
        return summary

    def daily_totals(self, days: int = 7, tag: str | None = None) -> list[tuple[date, float]]:
        """Total focus minutes per day for the last ``days`` days (oldest first)."""
        rows = self._rows(tag)
        today = date.today()
        buckets: dict[date, float] = {today - timedelta(days=offset): 0.0 for offset in range(days - 1, -1, -1)}
        cutoff = today - timedelta(days=days - 1)
        for row in rows:
            row_date = row.completed_at.date()
            if row_date >= cutoff:
                buckets[row_date] = buckets.get(row_date, 0.0) + row.duration_minutes
        return sorted(buckets.items())

    def reset(self) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM focus_sessions")
