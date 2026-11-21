from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class SQLiteMemory:
    """Small persistent conversation store and searchable fact memory."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_turns_session_id ON turns(session_id, id)")
            db.execute("""CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                fact TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_facts_session_id ON facts(session_id, id)")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database_path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    @contextmanager
    def _connection(self):
        db = self._connect()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("role must be 'user' or 'assistant'")
        if not content.strip():
            return
        with self._connection() as db:
            db.execute(
                "INSERT INTO turns(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content.strip(), self._now()),
            )

    def remember(self, session_id: str, fact: str) -> str:
        fact = fact.strip()
        if not fact:
            return "Nothing was saved because the memory text was empty."
        with self._connection() as db:
            db.execute(
                "INSERT INTO facts(session_id, fact, created_at) VALUES (?, ?, ?)",
                (session_id, fact, self._now()),
            )
        return "Saved that information to SQLite memory."

    def recent_turns(self, session_id: str, limit: int = 12) -> list[dict[str, str]]:
        limit = max(0, min(int(limit), 100))
        with self._connection() as db:
            rows = db.execute(
                "SELECT role, content FROM turns WHERE session_id=? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def search(self, session_id: str, query: str, limit: int = 8) -> str:
        terms = [term.lower() for term in query.split() if len(term) > 1]
        if not terms:
            return "Give me a search phrase to look up in memory."
        with self._connection() as db:
            rows = db.execute(
                "SELECT 'fact' AS kind, fact AS content, created_at FROM facts WHERE session_id=? "
                "UNION ALL SELECT role AS kind, content, created_at FROM turns WHERE session_id=? "
                "ORDER BY created_at DESC LIMIT 500",
                (session_id, session_id),
            ).fetchall()
        ranked = []
        for row in rows:
            content = row["content"]
            score = sum(term in content.lower() for term in terms)
            if score:
                ranked.append((score, row["created_at"], row["kind"], content))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if not ranked:
            return "No matching information was found in this session's memory."
        return "\n".join(f"[{kind}] {content}" for _, _, kind, content in ranked[:limit])

