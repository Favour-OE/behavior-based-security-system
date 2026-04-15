import pytest
from bbss.auth.signup import signup, validate_username, validate_password
from bbss.auth.login import login
from bbss.auth.hashing import hash_password, verify_password, generate_token, hash_token
from bbss.database.models import get_user_by_username, get_user_by_id, get_session_by_token_hash


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("TestPassword123!")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        hashed = hash_password("TestPassword123!")
        assert verify_password("TestPassword123!", hashed) is True
    
    def test_verify_password_incorrect(self):
        hashed = hash_password("TestPassword123!")
        assert verify_password("WrongPassword", hashed) is False
    
    def test_generate_token_length(self):
        token = generate_token()
        assert len(token) == 64
    
    def test_generate_token_unique(self):
        tokens = [generate_token() for _ in range(100)]
        assert len(set(tokens)) == 100
    
    def test_hash_token_consistent(self):
        token = generate_token()
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        assert hash1 == hash2
        assert len(hash1) == 64


class TestUsernameValidation:
    def test_valid_username(self):
        valid, error = validate_username("testuser")
        assert valid is True
        assert error is None
    
    def test_username_too_short(self):
        valid, error = validate_username("ab")
        assert valid is False
        assert "at least" in error
    
    def test_username_too_long(self):
        valid, error = validate_username("a" * 33)
        assert valid is False
        assert "no more than" in error
    
    def test_username_invalid_chars(self):
        valid, error = validate_username("user@name!")
        assert valid is False
        assert "only contain" in error
    
    def test_empty_username(self):
        valid, error = validate_username("")
        assert valid is False


class TestPasswordValidation:
    def test_valid_password(self):
        valid, error = validate_password("TestPassword123!")
        assert valid is True
    
    def test_password_too_short(self):
        valid, error = validate_password("Short1!")
        assert valid is False
        assert "at least" in error
    
    def test_empty_password(self):
        valid, error = validate_password("")
        assert valid is False


class TestSignup:
    def test_signup_success(self, test_db):
        result = signup("newuser", "TestPassword123!")
        assert result["success"] is True
        assert result["user_id"] is not None
        assert result["error"] is None
    
    def test_signup_duplicate_username(self, test_db):
        signup("duplicateuser", "TestPassword123!")
        result = signup("duplicateuser", "DifferentPass123!")
        assert result["success"] is False
        assert result["user_id"] is None
        assert "exists" in result["error"]
    
    def test_signup_creates_profile(self, test_db):
        result = signup("profileuser", "TestPassword123!")
        from bbss.database.models import get_profile
        profile = get_profile(result["user_id"])
        assert profile is not None
        assert profile["profile_status"] == "bootstrapping"


class TestLogin:
    def test_login_success(self, test_db, sample_user):
        result = login("testuser", "TestPassword123!")
        assert result["success"] is True
        assert result["session_token"] is not None
        assert result["user_id"] == sample_user["user_id"]
    
    def test_login_wrong_password(self, test_db, sample_user):
        result = login("testuser", "WrongPassword!")
        assert result["success"] is False
        assert result["session_token"] is None
        assert "Invalid credentials" in result["error"]
    
    def test_login_nonexistent_user(self, test_db):
        result = login("nonexistent", "SomePassword!")
        assert result["success"] is False
        assert "Invalid credentials" in result["error"]
    
    def test_login_creates_session(self, test_db, sample_user):
        result = login("testuser", "TestPassword123!")
        session = get_session_by_token_hash(hash_token(result["session_token"]))
        assert session is not None
        assert session["user_id"] == sample_user["user_id"]
    
    def test_failed_attempts_counter(self, test_db, sample_user):
        for _ in range(3):
            login("testuser", "WrongPassword!")
        user = get_user_by_username("testuser")
        assert user["failed_attempts"] == 3
    
    def test_lockout_after_max_attempts(self, test_db, sample_user):
        from bbss.config import get_config
        config = get_config()
        for _ in range(config.MAX_FAILED_ATTEMPTS):
            login("testuser", "WrongPassword!")
        result = login("testuser", "TestPassword123!")
        assert result["success"] is False
        assert "locked" in result["error"].lower()
    
    def test_successful_login_resets_counter(self, test_db, sample_user):
        login("testuser", "WrongPassword!")
        login("testuser", "TestPassword123!")
        user = get_user_by_username("testuser")
        assert user["failed_attempts"] == 0
