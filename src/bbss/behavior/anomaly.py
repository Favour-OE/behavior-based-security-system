from typing import List
from ..config import config

ANOMALY_SIGNALS = {
    "TYPING_TIME": "typing_time_deviation",
    "LOGIN_HOUR": "unusual_login_hour",
    "LOGIN_DAY": "unusual_login_day",
    "UNKNOWN_IP": "unknown_ip",
    "COMMAND_COUNT": "command_count_anomaly",
    "UNKNOWN_COMMANDS": "unknown_commands",
    "SESSION_DURATION": "session_duration_anomaly"
}


def compute_zscore(value: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0
    return (value - mean) / std


def detect_typing_time_anomaly(current: float, profile_avg: float, profile_std: float) -> bool:
    if current is None or profile_avg is None or profile_std is None:
        return False
    zscore = abs(compute_zscore(current, profile_avg, profile_std))
    return zscore > config.ZSCORE_THRESHOLD


def detect_login_hour_anomaly(current_hour: int, profile_hours: List[int]) -> bool:
    if current_hour is None or not profile_hours:
        return False
    
    if len(profile_hours) < 4:
        return current_hour not in profile_hours
    
    sorted_hours = sorted(profile_hours)
    q1_idx = len(sorted_hours) // 4
    q3_idx = 3 * len(sorted_hours) // 4
    q1 = sorted_hours[q1_idx]
    q3 = sorted_hours[q3_idx]
    iqr = q3 - q1
    
    lower_bound = q1 - config.IQR_MULTIPLIER * iqr
    upper_bound = q3 + config.IQR_MULTIPLIER * iqr
    
    return current_hour < lower_bound or current_hour > upper_bound


def detect_login_day_anomaly(current_day: int, profile_logs: list) -> bool:
    if current_day is None:
        return False
    
    profile_days = [log["login_day_of_week"] for log in profile_logs if log.get("login_day_of_week") is not None]
    
    if not profile_days:
        return False
    
    unique_days = set(profile_days)
    if len(unique_days) <= 1:
        return current_day not in unique_days
    
    return current_day not in unique_days


def detect_unknown_ip(current_ip: str, known_ips: List[str]) -> bool:
    if current_ip is None or not known_ips:
        return False
    return current_ip not in known_ips


def detect_command_count_anomaly(current_count: int, profile_avg: float, profile_std: float) -> bool:
    if current_count is None or profile_avg is None or profile_std is None:
        return False
    zscore = abs(compute_zscore(current_count, profile_avg, profile_std))
    return zscore > config.ZSCORE_THRESHOLD


def detect_unknown_commands(current_commands: List[str], common_commands: List[str]) -> bool:
    if not current_commands or not common_commands:
        return False
    
    unknown = [cmd for cmd in current_commands if cmd not in common_commands]
    return len(unknown) / len(current_commands) > 0.3


def detect_session_duration_anomaly(current_duration: float, profile_avg: float, profile_std: float) -> bool:
    if current_duration is None or profile_avg is None or profile_std is None:
        return False
    zscore = abs(compute_zscore(current_duration, profile_avg, profile_std))
    return zscore > config.ZSCORE_THRESHOLD


def get_sensitivity_multiplier(profile_status: str) -> float:
    if profile_status == "bootstrapping":
        return 0.0
    elif profile_status == "warmup":
        return 0.5
    else:
        return 1.0


def detect_anomalies(current_behavior: dict, profile: dict, profile_logs: list = None) -> List[str]:
    anomalies = []
    
    status = profile.get("profile_status", "bootstrapping")
    sensitivity = get_sensitivity_multiplier(status)
    
    if sensitivity == 0.0:
        return anomalies
    
    if detect_typing_time_anomaly(
        current_behavior.get("typing_time"),
        profile.get("avg_typing_time"),
        profile.get("std_typing_time")
    ):
        anomalies.append(ANOMALY_SIGNALS["TYPING_TIME"])
    
    if profile_logs is None:
        profile_logs = []
    if detect_login_hour_anomaly(
        current_behavior.get("login_hour"),
        profile.get("typical_login_hours", [])
    ):
        anomalies.append(ANOMALY_SIGNALS["LOGIN_HOUR"])
    
    if detect_login_day_anomaly(
        current_behavior.get("login_day_of_week"),
        profile_logs
    ):
        anomalies.append(ANOMALY_SIGNALS["LOGIN_DAY"])
    
    if detect_unknown_ip(
        current_behavior.get("ip_address"),
        profile.get("known_ips", [])
    ):
        anomalies.append(ANOMALY_SIGNALS["UNKNOWN_IP"])
    
    if detect_command_count_anomaly(
        current_behavior.get("command_count"),
        profile.get("avg_command_count"),
        5.0
    ):
        anomalies.append(ANOMALY_SIGNALS["COMMAND_COUNT"])
    
    commands = current_behavior.get("commands_used", [])
    if isinstance(commands, str):
        import json
        commands = json.loads(commands)
    if detect_unknown_commands(commands, profile.get("common_commands", [])):
        anomalies.append(ANOMALY_SIGNALS["UNKNOWN_COMMANDS"])
    
    if detect_session_duration_anomaly(
        current_behavior.get("session_duration"),
        profile.get("avg_session_duration"),
        60.0
    ):
        anomalies.append(ANOMALY_SIGNALS["SESSION_DURATION"])
    
    if status == "warmup" and anomalies:
        keep_count = len(anomalies) // 2 + (1 if len(anomalies) % 2 else 0)
        anomalies = anomalies[:keep_count]
    
    return anomalies
