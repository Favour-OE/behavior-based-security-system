import json
from datetime import datetime


def parse_json_field(value: str | None, default=None):
    if value is None:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def get_login_time_info() -> dict:
    now = datetime.now()
    return {
        "hour": now.hour,
        "day_of_week": now.weekday(),
        "timestamp": now.isoformat()
    }


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"
