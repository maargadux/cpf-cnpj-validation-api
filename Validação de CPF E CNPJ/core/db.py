import sqlite3
from pathlib import Path

DB_PATH = Path("database.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            plan TEXT NOT NULL DEFAULT 'free',
            daily_limit INTEGER NOT NULL DEFAULT 100
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_daily (
            key TEXT NOT NULL,
            day TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (key, day),
            FOREIGN KEY (key) REFERENCES api_keys(key)
        )
        """)
