import statistics
from collections import Counter
from typing import List
from ..database.models import get_behavior_logs_by_user, get_profile, update_behavior_profile
from ..config import config

MIN_SESSIONS_FOR_PROFILE = 3


def compute_baseline_metrics(logs: List[dict]) -> dict:
    if not logs:
        return {
            "avg_typing_time": None,
            "std_typing_time": None,
            "avg_session_duration": None,
            "avg_command_count": None,
            "typical_login_hours": [],
            "common_commands": [],
            "known_ips": []
        }
    
    typing_times = [log["typing_time"] for log in logs if log.get("typing_time") is not None]
    avg_typing = statistics.mean(typing_times) if typing_times else None
    std_typing = statistics.stdev(typing_times) if len(typing_times) > 1 else 0.0
    
    durations = [log["session_duration"] for log in logs if log.get("session_duration") is not None]
    avg_duration = statistics.mean(durations) if durations else None
    
    command_counts = [log["command_count"] for log in logs if log.get("command_count") is not None]
    avg_command_count = statistics.mean(command_counts) if command_counts else None
    
    login_hours = [log["login_hour"] for log in logs if log.get("login_hour") is not None]
    
    all_commands = []
    for log in logs:
        commands = log.get("commands_used")
        if commands:
            if isinstance(commands, str):
                import json
                commands = json.loads(commands)
            all_commands.extend(commands)
    
    command_counts_by_freq = Counter(all_commands)
    common_commands = [cmd for cmd, _ in command_counts_by_freq.most_common(10)]
    
    known_ips = list(set(log["ip_address"] for log in logs if log.get("ip_address")))
    
    return {
        "avg_typing_time": avg_typing,
        "std_typing_time": std_typing,
        "avg_session_duration": avg_duration,
        "avg_command_count": avg_command_count,
        "typical_login_hours": login_hours,
        "common_commands": common_commands,
        "known_ips": known_ips
    }


def build_profile(user_id: int, limit: int = 50) -> dict | None:
    logs = get_behavior_logs_by_user(user_id, limit=limit)
    
    if len(logs) < MIN_SESSIONS_FOR_PROFILE:
        return None
    
    metrics = compute_baseline_metrics(logs)
    
    current = get_profile(user_id)
    session_count = current["session_count"] if current else len(logs)
    profile_status = current["profile_status"] if current else "bootstrapping"
    
    return {
        "user_id": user_id,
        "session_count": session_count,
        "profile_status": profile_status,
        **metrics
    }


def update_profile(user_id: int) -> dict | None:
    profile = build_profile(user_id)
    
    if profile is None:
        return None
    
    update_behavior_profile(
        user_id=user_id,
        avg_typing_time=profile["avg_typing_time"],
        std_typing_time=profile["std_typing_time"],
        avg_session_duration=profile["avg_session_duration"],
        avg_command_count=profile["avg_command_count"],
        typical_login_hours=profile["typical_login_hours"],
        common_commands=profile["common_commands"],
        known_ips=profile["known_ips"],
        session_count=profile["session_count"],
        profile_status=profile["profile_status"]
    )
    
    return profile


def get_or_create_profile(user_id: int) -> dict:
    profile = get_profile(user_id)
    if profile:
        return profile
    
    return {
        "user_id": user_id,
        "session_count": 0,
        "profile_status": "bootstrapping",
        "avg_typing_time": None,
        "std_typing_time": None,
        "avg_session_duration": None,
        "avg_command_count": None,
        "typical_login_hours": [],
        "common_commands": [],
        "known_ips": []
    }
