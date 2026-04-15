import pytest
from security.response import (
    generate_pin, verify_pin, dispatch_response, verify_challenge,
    RISK_LEVEL_SAFE, RISK_LEVEL_WARNING, RISK_LEVEL_HIGH_RISK
)


class TestPIN:
    def test_generate_pin_length(self):
        pin = generate_pin()
        assert len(pin) == 6
        assert pin.isdigit()
    
    def test_generate_pin_range(self):
        for _ in range(100):
            pin = generate_pin()
            assert 100000 <= int(pin) <= 999999
    
    def test_verify_pin_correct(self):
        assert verify_pin("123456", "123456") is True
    
    def test_verify_pin_incorrect(self):
        assert verify_pin("123456", "654321") is False


class TestDispatchResponse:
    def test_safe_allows(self, test_db):
        result = dispatch_response(RISK_LEVEL_SAFE, user_id=1, session_id=1)
        assert result["action"] == "ALLOW"
        assert result["requires_pin"] is False
        assert result["pin"] is None
    
    def test_warning_requires_challenge(self, test_db):
        result = dispatch_response(RISK_LEVEL_WARNING, user_id=1, session_id=1)
        assert result["action"] == "CHALLENGE"
        assert result["requires_pin"] is True
        assert result["pin"] is not None
        assert len(result["pin"]) == 6
    
    def test_high_risk_blocks(self, test_db, sample_user):
        result = dispatch_response(RISK_LEVEL_HIGH_RISK, user_id=sample_user["user_id"], session_id=1)
        assert result["action"] == "BLOCK"
        assert result["requires_pin"] is False


class TestVerifyChallenge:
    def test_verify_challenge_passed(self):
        result = verify_challenge("123456", "123456")
        assert result["passed"] is True
        assert "passed" in result["message"].lower()
    
    def test_verify_challenge_failed(self):
        result = verify_challenge("123456", "654321")
        assert result["passed"] is False
        assert "failed" in result["message"].lower()
