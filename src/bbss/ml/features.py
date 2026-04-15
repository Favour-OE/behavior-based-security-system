import numpy as np
from typing import List, Dict


def extract_features_from_log(log: dict) -> np.ndarray:
    features = [
        log.get("typing_time", 0.0) or 0.0,
        log.get("login_hour", 12) / 24.0,
        log.get("login_day_of_week", 0) / 6.0,
        log.get("session_duration", 0.0) or 0.0,
        log.get("command_count", 0) / 100.0,
    ]
    return np.array(features)


def extract_features_from_behavior(behavior: dict) -> np.ndarray:
    features = [
        behavior.get("typing_time", 0.0) or 0.0,
        (behavior.get("login_hour", 12) or 12) / 24.0,
        (behavior.get("login_day_of_week", 0) or 0) / 6.0,
        behavior.get("session_duration", 0.0) or 0.0,
        behavior.get("command_count", 0) / 100.0,
    ]
    return np.array(features)


def prepare_training_data(logs: List[dict]) -> np.ndarray:
    if not logs:
        return np.array([])
    
    features = []
    for log in logs:
        features.append(extract_features_from_log(log))
    
    return np.array(features)


def get_feature_names() -> List[str]:
    return [
        "typing_time_normalized",
        "login_hour_normalized",
        "login_day_normalized",
        "session_duration_normalized",
        "command_count_normalized"
    ]
