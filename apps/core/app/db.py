import logging
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"
DB_PATH = DATA_PATH / "cuenote.db"

logger = logging.getLogger("cuenote.core")


def get_conn() -> sqlite3.Connection:
    DATA_PATH.mkdir(parents=True, exist_ok=True)
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
        conn.commit()
    finally:
        conn.close()
    logger.info("Database ready at %s", DB_PATH)
