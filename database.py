import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("bot.db")


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                company TEXT,
                phone TEXT,
                telegram TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()


def save_user(user):
    with connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user.id,
                getattr(user, "username", None),
                getattr(user, "first_name", None),
                getattr(user, "last_name", None),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


def save_lead(user_id, name, company, phone, telegram):
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO leads (user_id, name, company, phone, telegram, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, company, phone, telegram, datetime.utcnow().isoformat()),
        )
        conn.commit()


def get_stats():
    with connect() as conn:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    return users, leads
