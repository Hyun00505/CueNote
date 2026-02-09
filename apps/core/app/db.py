import logging
import sqlite3
from pathlib import Path

from .config import DATA_DIR

DB_PATH = DATA_DIR / "cuenote.db"

logger = logging.getLogger("cuenote.core")


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                note_path TEXT,
                line_no INTEGER,
                text TEXT,
                checked INTEGER,
                updated_at TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                path TEXT PRIMARY KEY,
                content_hash TEXT,
                updated_at TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                color TEXT DEFAULT '#c9a76c',
                completed INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(date);
            """
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Database ready at %s", DB_PATH)
