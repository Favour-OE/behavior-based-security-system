import re
from auth.hashing import hash_password
from database.models import create_user, create_behavior_profile

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 32
PASSWORD_MIN_LENGTH = 8
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')


def validate_username(username: str) -> tuple[bool, str | None]:
    if not username:
        return False, "Username is required"
    if len(username) < USERNAME_MIN_LENGTH:
        return False, f"Username must be at least {USERNAME_MIN_LENGTH} characters"
    if len(username) > USERNAME_MAX_LENGTH:
        return False, f"Username must be no more than {USERNAME_MAX_LENGTH} characters"
    if not USERNAME_REGEX.match(username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, None


def validate_password(password: str) -> tuple[bool, str | None]:
    if not password:
        return False, "Password is required"
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    return True, None


def signup(username: str, password: str, email: str = None) -> dict:
    valid, error = validate_username(username)
    if not valid:
        return {"success": False, "user_id": None, "error": error}

    valid, error = validate_password(password)
    if not valid:
        return {"success": False, "user_id": None, "error": error}

    password_hash = hash_password(password)

    user_id = create_user(username, password_hash, email)
    if user_id is None:
        return {"success": False, "user_id": None, "error": "Username already exists"}

    create_behavior_profile(user_id)

    return {"success": True, "user_id": user_id, "error": None}
