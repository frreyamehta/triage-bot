import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path("data/triage.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at    TEXT NOT NULL DEFAULT (datetime('now')),
    sender         TEXT NOT NULL,
    channel        TEXT NOT NULL,
    raw_text       TEXT NOT NULL,
    clean_text     TEXT,
    category       TEXT,
    urgency        TEXT,
    summary        TEXT,
    extracted_json TEXT,
    status         TEXT NOT NULL DEFAULT 'received'
);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(_connect()) as conn:
        conn.executescript(SCHEMA)


def insert_message(sender: str, channel: str, raw_text: str) -> int:
    with closing(_connect()) as conn:
        cur = conn.execute(
            "INSERT INTO messages (sender, channel, raw_text) VALUES (?, ?, ?)",
            (sender, channel, raw_text),
        )
        conn.commit()
        return cur.lastrowid


def list_messages(limit: int = 50) -> list[dict]:
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_message(message_id: int) -> dict | None:
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ?", (message_id,)
        ).fetchone()
        return dict(row) if row else None