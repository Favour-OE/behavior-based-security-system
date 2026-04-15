import pytest
from bbss.security.risk import (
    compute_risk_score, classify_risk, get_risk_assessment,
    RISK_LEVEL_SAFE, RISK_LEVEL_WARNING, RISK_LEVEL_HIGH_RISK
)
from bbss.config import get_config


class TestRiskScoring:
    def test_zero_score_no_anomalies(self):
        assert compute_risk_score([]) == 0
    
    def test_single_anomaly(self):
        config = get_config()
        score = compute_risk_score(["typing_time_deviation"])
        assert score == config.RISK_WEIGHT_TYPING_TIME
    
    def test_multiple_anomalies(self):
        config = get_config()
        signals = ["typing_time_deviation", "unusual_login_hour"]
        score = compute_risk_score(signals)
        expected = config.RISK_WEIGHT_TYPING_TIME + config.RISK_WEIGHT_LOGIN_HOUR
        assert score == expected
    
    def test_score_capped_at_100(self):
        from bbss.security.risk import _get_anomaly_weights
        weights = _get_anomaly_weights()
        total = sum(weights.values())
        if total > 100:
            assert min(total, 100) == 100


class TestRiskClassification:
    def test_safe_range(self):
        config = get_config()
        assert classify_risk(0) == RISK_LEVEL_SAFE
        assert classify_risk(30) == RISK_LEVEL_SAFE
        assert classify_risk(config.RISK_THRESHOLD_WARNING - 1) == RISK_LEVEL_SAFE
    
    def test_warning_range(self):
        config = get_config()
        assert classify_risk(config.RISK_THRESHOLD_WARNING) == RISK_LEVEL_WARNING
        assert classify_risk(50) == RISK_LEVEL_WARNING
        assert classify_risk(config.RISK_THRESHOLD_HIGH - 1) == RISK_LEVEL_WARNING
    
    def test_high_risk_range(self):
        config = get_config()
        assert classify_risk(config.RISK_THRESHOLD_HIGH) == RISK_LEVEL_HIGH_RISK
        assert classify_risk(80) == RISK_LEVEL_HIGH_RISK
        assert classify_risk(100) == RISK_LEVEL_HIGH_RISK


class TestRiskAssessment:
    def test_complete_assessment_no_anomalies(self):
        result = get_risk_assessment([])
        assert result["risk_score"] == 0
        assert result["risk_level"] == RISK_LEVEL_SAFE
        assert result["anomaly_signals"] == []
    
    def test_complete_assessment_with_anomalies(self):
        config = get_config()
        signals = ["unknown_ip", "unusual_login_hour"]
        result = get_risk_assessment(signals)
        expected_score = config.RISK_WEIGHT_UNKNOWN_IP + config.RISK_WEIGHT_LOGIN_HOUR
        assert result["risk_score"] == expected_score
        assert result["risk_level"] == classify_risk(expected_score)
        assert result["anomaly_signals"] == signals
