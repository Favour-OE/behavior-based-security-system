from typing import List
from config import config

RISK_LEVEL_SAFE = "SAFE"
RISK_LEVEL_WARNING = "WARNING"
RISK_LEVEL_HIGH_RISK = "HIGH_RISK"

ANOMALY_WEIGHTS = {
    "typing_time_deviation": config.RISK_WEIGHT_TYPING_TIME,
    "unusual_login_hour": config.RISK_WEIGHT_LOGIN_HOUR,
    "unusual_login_day": config.RISK_WEIGHT_LOGIN_DAY,
    "unknown_ip": config.RISK_WEIGHT_UNKNOWN_IP,
    "command_count_anomaly": config.RISK_WEIGHT_COMMAND_COUNT,
    "unknown_commands": config.RISK_WEIGHT_UNKNOWN_COMMANDS,
    "session_duration_anomaly": config.RISK_WEIGHT_SESSION_DURATION,
    "ml_isolation_forest": config.RISK_WEIGHT_ML_FLAG
}


def compute_risk_score(anomaly_signals: List[str]) -> int:
    total = 0
    for signal in anomaly_signals:
        weight = ANOMALY_WEIGHTS.get(signal, 0)
        total += weight
    return min(total, 100)


def classify_risk(score: int) -> str:
    if score < config.RISK_THRESHOLD_WARNING:
        return RISK_LEVEL_SAFE
    elif score < config.RISK_THRESHOLD_HIGH:
        return RISK_LEVEL_WARNING
    else:
        return RISK_LEVEL_HIGH_RISK


def get_risk_assessment(anomaly_signals: List[str]) -> dict:
    return {
        "anomaly_signals": anomaly_signals,
        "risk_score": compute_risk_score(anomaly_signals),
        "risk_level": classify_risk(compute_risk_score(anomaly_signals))
    }
