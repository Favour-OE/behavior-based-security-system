from datetime import datetime, timedelta
from .hashing import verify_password, generate_token, hash_token
from ..database.models import (
    get_user_by_username,
    increment_failed_attempts,
    reset_failed_attempts,
    lock_account,
    is_account_locked,
    create_session
)
from ..config import config
from ..behavior.capture import capture_behavior_from_login


def check_account_lockout(user: dict) -> tuple[bool, str | None]:
    locked, locked_until = is_account_locked(user['id'])
    if locked:
        return True, f"Account is locked until {locked_until}"
    if user['failed_attempts'] >= config.MAX_FAILED_ATTEMPTS:
        lockout_time = datetime.now() + timedelta(minutes=config.LOCKOUT_DURATION_MINUTES)
        lock_account(user['id'], lockout_time.isoformat())
        return True, f"Account locked due to too many failed attempts. Locked until {lockout_time.isoformat()}"
    return False, None


def login(username: str, password: str, typing_time: float = 0.0, ip_address: str = None, user_agent: str = None) -> dict:
    user = get_user_by_username(username)
    if not user:
        return {"success": False, "session_token": None, "user_id": None, "error": "Invalid credentials"}

    if not user['is_active']:
        return {"success": False, "session_token": None, "user_id": None, "error": "Account is deactivated"}

    is_locked, message = check_account_lockout(user)
    if is_locked:
        return {"success": False, "session_token": None, "user_id": None, "error": message}

    if not verify_password(password, user['password_hash']):
        increment_failed_attempts(user['id'])
        remaining = config.MAX_FAILED_ATTEMPTS - user['failed_attempts'] - 1
        return {
            "success": False,
            "session_token": None,
            "user_id": None,
            "error": f"Invalid credentials. {remaining} attempts remaining" if remaining > 0 else "Invalid credentials. Account locked."
        }

    reset_failed_attempts(user['id'])

    session_token = generate_token()
    token_hash = hash_token(session_token)
    expires_at = (datetime.now() + timedelta(hours=config.SESSION_EXPIRY_HOURS)).isoformat()

    session_id = create_session(user['id'], token_hash, expires_at, ip_address, user_agent)

    capture_ctx = capture_behavior_from_login(
        user_id=user['id'],
        typing_time=typing_time,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return {
        "success": True,
        "session_token": session_token,
        "session_id": session_id,
        "user_id": user['id'],
        "capture_context": capture_ctx,
        "error": None
    }
