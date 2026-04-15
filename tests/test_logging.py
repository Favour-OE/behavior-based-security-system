import pytest
from bbss.logs.logger import log_event, log_login_attempt, log_security_decision
from bbss.logs.audit import get_user_audit_trail, get_risk_summary_by_user


class TestLogging:
    def test_log_event_creates_record(self, test_db, monkeypatch):
        monkeypatch.setenv("CONSOLE_LOGGING", "false")
        
        log_event(
            event_type="TEST_EVENT",
            user_id=1,
            username="testuser",
            level="INFO",
            message="Test message"
        )
    
    def test_log_login_attempt_success(self, test_db, monkeypatch):
        monkeypatch.setenv("CONSOLE_LOGGING", "false")
        log_login_attempt("testuser", success=True, user_id=1)
    
    def test_log_login_attempt_failure(self, test_db, monkeypatch):
        monkeypatch.setenv("CONSOLE_LOGGING", "false")
        log_login_attempt("testuser", success=False, reason="Invalid password")
    
    def test_log_security_decision_allow(self, test_db, monkeypatch):
        monkeypatch.setenv("CONSOLE_LOGGING", "false")
        log_security_decision(
            user_id=1,
            username="testuser",
            risk_score=10,
            anomaly_signals=[],
            decision="ALLOW",
            behavior_snapshot={"typing_time": 2.0}
        )
    
    def test_log_security_decision_block(self, test_db, monkeypatch):
        monkeypatch.setenv("CONSOLE_LOGGING", "false")
        log_security_decision(
            user_id=1,
            username="testuser",
            risk_score=75,
            anomaly_signals=["unknown_ip", "unusual_login_hour"],
            decision="BLOCK",
            behavior_snapshot={"ip_address": "suspicious.ip"}
        )


class TestAudit:
    def test_get_user_audit_trail_empty(self, test_db):
        trail = get_user_audit_trail(999)
        assert trail == []
    
    def test_get_risk_summary_empty_user(self, test_db):
        summary = get_risk_summary_by_user(999)
        assert summary["total_sessions"] == 0
        assert summary["allowed"] == 0
    
    def test_get_risk_summary_with_logs(self, test_db, sample_user):
        from bbss.database.models import create_risk_log
        
        create_risk_log(
            user_id=sample_user["user_id"],
            behavior_log_id=None,
            risk_score=10,
            risk_level="SAFE",
            anomaly_signals=[],
            decision="ALLOW"
        )
        create_risk_log(
            user_id=sample_user["user_id"],
            behavior_log_id=None,
            risk_score=40,
            risk_level="WARNING",
            anomaly_signals=["unknown_ip"],
            decision="CHALLENGE"
        )
        create_risk_log(
            user_id=sample_user["user_id"],
            behavior_log_id=None,
            risk_score=80,
            risk_level="HIGH_RISK",
            anomaly_signals=["unknown_ip", "typing_time_deviation"],
            decision="BLOCK"
        )
        
        summary = get_risk_summary_by_user(sample_user["user_id"])
        assert summary["total_sessions"] == 3
        assert summary["allowed"] == 1
        assert summary["challenged"] == 1
        assert summary["blocked"] == 1
        assert summary["avg_risk_score"] == 43.33
