import hashlib
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)


def hash_password(plain_text: str) -> str:
    return ph.hash(plain_text)


def verify_password(plain_text: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, plain_text)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False


def generate_token() -> str:
    return secrets.token_hex(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
