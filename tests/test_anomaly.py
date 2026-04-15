import pytest
from bbss.behavior.profile import compute_baseline_metrics, build_profile, update_profile
from bbss.behavior.anomaly import (
    compute_zscore, detect_typing_time_anomaly, detect_login_hour_anomaly,
    detect_unknown_ip, detect_command_count_anomaly, detect_anomalies, ANOMALY_SIGNALS
)


class TestBaselineMetrics:
    def test_compute_baseline_empty(self):
        metrics = compute_baseline_metrics([])
        assert metrics["avg_typing_time"] is None
        assert metrics["std_typing_time"] is None
        assert metrics["typical_login_hours"] == []
        assert metrics["common_commands"] == []
    
    def test_compute_baseline_single_log(self):
        logs = [
            {"typing_time": 2.0, "login_hour": 10, "command_count": 5, "session_duration": 300, "commands_used": ["cmd1"], "ip_address": "1.1.1.1"}
        ]
        metrics = compute_baseline_metrics(logs)
        assert metrics["avg_typing_time"] == 2.0
        assert metrics["std_typing_time"] == 0.0
        assert metrics["avg_session_duration"] == 300
        assert "cmd1" in metrics["common_commands"]
        assert "1.1.1.1" in metrics["known_ips"]
    
    def test_compute_baseline_multiple_logs(self):
        logs = [
            {"typing_time": 1.5, "login_hour": 9, "command_count": 3, "session_duration": 200, "commands_used": ["a", "b"], "ip_address": "1.1.1.1"},
            {"typing_time": 2.5, "login_hour": 10, "command_count": 5, "session_duration": 300, "commands_used": ["a", "c"], "ip_address": "1.1.1.2"},
            {"typing_time": 2.0, "login_hour": 11, "command_count": 4, "session_duration": 250, "commands_used": ["b", "c"], "ip_address": "1.1.1.1"}
        ]
        metrics = compute_baseline_metrics(logs)
        assert abs(metrics["avg_typing_time"] - 2.0) < 0.01
        assert metrics["avg_session_duration"] == 250
        assert metrics["avg_command_count"] == 4


class TestZScore:
    def test_zscore_basic(self):
        z = compute_zscore(10, 5, 2.5)
        assert z == 2.0
    
    def test_zscore_zero_std(self):
        z = compute_zscore(10, 5, 0)
        assert z == 0.0


class TestTypingTimeAnomaly:
    def test_no_anomaly_within_threshold(self):
        assert detect_typing_time_anomaly(3.5, 2.0, 1.0) is False
    
    def test_anomaly_outside_threshold(self):
        assert detect_typing_time_anomaly(5.0, 2.0, 1.0) is True
    
    def test_no_anomaly_no_baseline(self):
        assert detect_typing_time_anomaly(2.0, None, 1.0) is False
        assert detect_typing_time_anomaly(None, 2.0, 1.0) is False


class TestLoginHourAnomaly:
    def test_hour_in_set(self):
        assert detect_login_hour_anomaly(10, [9, 10, 11]) is False
    
    def test_hour_outside_set_small(self):
        assert detect_login_hour_anomaly(14, [9, 10, 11]) is True
    
    def test_hour_outside_iqr_range(self):
        hours = [8, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 12]
        assert detect_login_hour_anomaly(22, hours) is True


class TestUnknownIP:
    def test_known_ip(self):
        assert detect_unknown_ip("192.168.1.1", ["192.168.1.1", "192.168.1.2"]) is False
    
    def test_unknown_ip(self):
        assert detect_unknown_ip("10.0.0.1", ["192.168.1.1"]) is True
    
    def test_no_baseline_ips(self):
        assert detect_unknown_ip("10.0.0.1", []) is False


class TestDetectAnomalies:
    def test_no_anomalies_typical_session(self):
        current = {
            "typing_time": 2.0,
            "login_hour": 10,
            "login_day_of_week": 1,
            "command_count": 4,
            "commands_used": ["a", "b"],
            "ip_address": "1.1.1.1",
            "session_duration": 250
        }
        profile = {
            "avg_typing_time": 2.0,
            "std_typing_time": 0.5,
            "avg_session_duration": 250,
            "avg_command_count": 4,
            "typical_login_hours": [9, 10, 11],
            "common_commands": ["a", "b", "c"],
            "known_ips": ["1.1.1.1"],
            "profile_status": "active"
        }
        anomalies = detect_anomalies(current, profile)
        assert len(anomalies) == 0
    
    def test_single_anomaly(self):
        current = {
            "typing_time": 10.0,
            "login_hour": 10,
            "login_day_of_week": 1,
            "command_count": 4,
            "commands_used": [],
            "ip_address": "1.1.1.1",
            "session_duration": 250
        }
        profile = {
            "avg_typing_time": 2.0,
            "std_typing_time": 0.5,
            "avg_session_duration": 250,
            "avg_command_count": 4,
            "typical_login_hours": [9, 10, 11],
            "common_commands": ["a", "b"],
            "known_ips": ["1.1.1.1"],
            "profile_status": "active"
        }
        anomalies = detect_anomalies(current, profile)
        assert ANOMALY_SIGNALS["TYPING_TIME"] in anomalies
    
    def test_bootstrapping_no_detection(self):
        current = {
            "typing_time": 100.0,
            "login_hour": 3,
            "ip_address": "suspicious.ip"
        }
        profile = {
            "profile_status": "bootstrapping",
            "avg_typing_time": 2.0,
            "std_typing_time": 0.5,
            "typical_login_hours": [],
            "known_ips": []
        }
        anomalies = detect_anomalies(current, profile)
        assert len(anomalies) == 0
    
    def test_warmup_reduced_sensitivity(self):
        current = {
            "typing_time": 10.0,
            "login_hour": 3,
            "login_day_of_week": 5,
            "ip_address": "suspicious.ip",
            "commands_used": [],
            "command_count": 50,
            "session_duration": 5000
        }
        profile = {
            "avg_typing_time": 2.0,
            "std_typing_time": 0.5,
            "avg_session_duration": 250,
            "avg_command_count": 4,
            "typical_login_hours": [],
            "common_commands": [],
            "known_ips": [],
            "profile_status": "warmup"
        }
        anomalies = detect_anomalies(current, profile)
        assert len(anomalies) >= 1
