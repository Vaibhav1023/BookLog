"""
Database bootstrap.

All schema definitions live here.
Only repositories import get_db() — no other layer touches the DB.
"""

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent.parent / "booklog.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    name          TEXT,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         TEXT    NOT NULL,
    author        TEXT    NOT NULL,
    isbn          TEXT,
    status        TEXT    NOT NULL,
    rating        INTEGER,
    page_count    INTEGER,
    notes         TEXT,
    cover_url     TEXT,
    date_added    TEXT    NOT NULL,
    date_finished TEXT,
    UNIQUE(user_id, isbn)
);

CREATE INDEX IF NOT EXISTS idx_books_user   ON books(user_id);
CREATE INDEX IF NOT EXISTS idx_books_status ON books(user_id, status);
CREATE INDEX IF NOT EXISTS idx_users_email  ON users(email);
"""


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Create tables if they don't exist. Safe to call on every startup."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def get_db(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Return a configured sqlite3 connection.
    Only repositories call this.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn
