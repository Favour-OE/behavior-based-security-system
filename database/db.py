import sqlite3
import os
from contextlib import contextmanager
from config import config

DATABASE_PATH = config.DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                typing_time REAL,
                login_hour INTEGER,
                login_day_of_week INTEGER,
                session_duration REAL,
                command_count INTEGER DEFAULT 0,
                commands_used TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                avg_typing_time REAL,
                std_typing_time REAL,
                avg_session_duration REAL,
                avg_command_count REAL,
                typical_login_hours TEXT,
                common_commands TEXT,
                known_ips TEXT,
                session_count INTEGER NOT NULL DEFAULT 0,
                profile_status TEXT NOT NULL DEFAULT 'bootstrapping',
                last_updated TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                behavior_log_id INTEGER REFERENCES behavior_logs(id),
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                anomaly_signals TEXT,
                decision TEXT NOT NULL,
                secondary_auth INTEGER DEFAULT 0,
                secondary_passed INTEGER,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
