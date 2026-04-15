from typing import List, Dict
from database.models import get_risk_logs_by_user, get_recent_high_risk_events, get_user_by_id


def get_user_audit_trail(user_id: int, limit: int = 100) -> List[Dict]:
    return get_risk_logs_by_user(user_id, limit)


def get_recent_high_risk_events(hours: int = 24) -> List[Dict]:
    return get_recent_high_risk_events(hours)


def get_risk_summary_by_user(user_id: int) -> Dict:
    logs = get_risk_logs_by_user(user_id, limit=1000)
    
    if not logs:
        return {
            "total_sessions": 0,
            "allowed": 0,
            "challenged": 0,
            "blocked": 0,
            "avg_risk_score": 0.0
        }
    
    allowed = sum(1 for log in logs if log["decision"] == "ALLOW")
    challenged = sum(1 for log in logs if log["decision"] == "CHALLENGE")
    blocked = sum(1 for log in logs if log["decision"] == "BLOCK")
    
    scores = [log["risk_score"] for log in logs if log.get("risk_score") is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    return {
        "total_sessions": len(logs),
        "allowed": allowed,
        "challenged": challenged,
        "blocked": blocked,
        "avg_risk_score": round(avg_score, 2)
    }


def get_user_security_report(user_id: int) -> Dict:
    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}
    
    summary = get_risk_summary_by_user(user_id)
    trail = get_user_audit_trail(user_id, limit=20)
    
    from collections import Counter
    all_signals = []
    for log in trail:
        all_signals.extend(log.get("anomaly_signals", []))
    signal_counts = Counter(all_signals)
    
    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "created_at": user["created_at"]
        },
        "summary": summary,
        "recent_sessions": [
            {
                "timestamp": log["timestamp"],
                "risk_score": log["risk_score"],
                "decision": log["decision"],
                "anomaly_count": len(log.get("anomaly_signals", []))
            }
            for log in trail[:10]
        ],
        "anomaly_trends": dict(signal_counts.most_common(5))
    }
