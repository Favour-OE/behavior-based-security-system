import json
import sqlite3
from .db import get_db, get_connection
from ..config import get_config


def create_user(username: str, password_hash: str, email: str = None) -> int | None:
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None


def get_user_by_username(username: str) -> dict | None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_user(user_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0


def increment_failed_attempts(user_id: int) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_attempts = failed_attempts + 1, updated_at = datetime('now') WHERE id = ?",
            (user_id,)
        )


def reset_failed_attempts(user_id: int) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = NULL, updated_at = datetime('now') WHERE id = ?",
            (user_id,)
        )


def lock_account(user_id: int, until_datetime: str) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET locked_until = ?, updated_at = datetime('now') WHERE id = ?",
            (until_datetime, user_id)
        )


def is_account_locked(user_id: int) -> tuple[bool, str | None]:
    user = get_user_by_id(user_id)
    if not user:
        return False, None
    locked_until = user.get("locked_until")
    if not locked_until:
        return False, None
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE id = ? AND datetime(locked_until) > datetime('now')",
            (user_id,)
        )
        is_locked = cursor.fetchone() is not None
    return is_locked, locked_until


def create_session(user_id: int, token_hash: str, expires_at: str, ip_address: str = None, user_agent: str = None) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sessions (user_id, token_hash, expires_at, ip_address, user_agent)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, token_hash, expires_at, ip_address, user_agent)
        )
        return cursor.lastrowid


def get_session_by_token_hash(token_hash: str) -> dict | None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM sessions 
               WHERE token_hash = ? AND is_active = 1 AND datetime(expires_at) > datetime('now')""",
            (token_hash,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def deactivate_session(token_hash: str) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET is_active = 0 WHERE token_hash = ?", (token_hash,))


def deactivate_session_by_id(session_id: int) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session_id,))


def create_behavior_log(
    user_id: int,
    typing_time: float = None,
    login_hour: int = None,
    login_day_of_week: int = None,
    session_duration: float = None,
    command_count: int = 0,
    commands_used: list = None,
    ip_address: str = None,
    user_agent: str = None
) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        commands_json = json.dumps(commands_used) if commands_used else None
        cursor.execute(
            """INSERT INTO behavior_logs 
               (user_id, typing_time, login_hour, login_day_of_week, session_duration, 
                command_count, commands_used, ip_address, user_agent)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, typing_time, login_hour, login_day_of_week, session_duration,
             command_count, commands_json, ip_address, user_agent)
        )
        return cursor.lastrowid


def get_behavior_logs_by_user(user_id: int, limit: int = 50) -> list[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM behavior_logs WHERE user_id = ? 
               ORDER BY timestamp DESC LIMIT ?""",
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_behavior_log_by_id(log_id: int) -> dict | None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM behavior_logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_behavior_profile(user_id: int) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO behavior_profiles (user_id, profile_status, session_count)
               VALUES (?, 'bootstrapping', 0)""",
            (user_id,)
        )
        return cursor.lastrowid


def get_profile(user_id: int) -> dict | None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM behavior_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            profile = dict(row)
            profile['typical_login_hours'] = json.loads(profile['typical_login_hours']) if profile['typical_login_hours'] else []
            profile['common_commands'] = json.loads(profile['common_commands']) if profile['common_commands'] else []
            profile['known_ips'] = json.loads(profile['known_ips']) if profile['known_ips'] else []
            return profile
        return None


def update_behavior_profile(
    user_id: int,
    avg_typing_time: float,
    std_typing_time: float,
    avg_session_duration: float,
    avg_command_count: float,
    typical_login_hours: list,
    common_commands: list,
    known_ips: list,
    session_count: int,
    profile_status: str
) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE behavior_profiles SET
               avg_typing_time = ?,
               std_typing_time = ?,
               avg_session_duration = ?,
               avg_command_count = ?,
               typical_login_hours = ?,
               common_commands = ?,
               known_ips = ?,
               session_count = ?,
               profile_status = ?,
               last_updated = datetime('now')
               WHERE user_id = ?""",
            (avg_typing_time, std_typing_time, avg_session_duration, avg_command_count,
             json.dumps(typical_login_hours), json.dumps(common_commands), json.dumps(known_ips),
             session_count, profile_status, user_id)
        )


def get_profile_status(user_id: int) -> str:
    profile = get_profile(user_id)
    return profile['profile_status'] if profile else 'bootstrapping'


def increment_profile_session_count(user_id: int) -> None:
    config = get_config()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT session_count FROM behavior_profiles WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            new_count = row['session_count'] + 1
            if new_count < config.MIN_SESSIONS_BOOTSTRAPPING:
                status = 'bootstrapping'
            elif new_count < config.MIN_SESSIONS_WARMUP:
                status = 'warmup'
            else:
                status = 'active'
            cursor.execute(
                """UPDATE behavior_profiles SET 
                   session_count = ?, profile_status = ?, last_updated = datetime('now')
                   WHERE user_id = ?""",
                (new_count, status, user_id)
            )


def create_risk_log(
    user_id: int,
    behavior_log_id: int | None,
    risk_score: int,
    risk_level: str,
    anomaly_signals: list,
    decision: str,
    secondary_auth: bool = False,
    secondary_passed: bool | None = None
) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO risk_logs 
               (user_id, behavior_log_id, risk_score, risk_level, anomaly_signals, 
                decision, secondary_auth, secondary_passed)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, behavior_log_id, risk_score, risk_level, json.dumps(anomaly_signals),
             decision, int(secondary_auth), int(secondary_passed) if secondary_passed is not None else None)
        )
        return cursor.lastrowid


def get_risk_logs_by_user(user_id: int, limit: int = 50) -> list[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM risk_logs WHERE user_id = ? 
               ORDER BY timestamp DESC LIMIT ?""",
            (user_id, limit)
        )
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log['anomaly_signals'] = json.loads(log['anomaly_signals']) if log['anomaly_signals'] else []
            logs.append(log)
        return logs


def get_recent_high_risk_events(hours: int = 24) -> list[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM risk_logs 
               WHERE risk_level = 'HIGH_RISK' 
               AND timestamp >= datetime('now', '-' || ? || ' hours')
               ORDER BY timestamp DESC""",
            (hours,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_session_by_token(token: str) -> dict | None:
    from ..auth.hashing import hash_token
    token_hash = hash_token(token)
    return get_session_by_token_hash(token_hash)
