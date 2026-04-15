from datetime import datetime


class CaptureContext:
    def __init__(
        self,
        user_id: int,
        ip_address: str = None,
        user_agent: str = None,
        session_start: float = None
    ):
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.session_start = session_start if session_start is not None else datetime.now().timestamp()
        
        self.typing_time: float | None = None
        self.login_hour: int | None = None
        self.login_day_of_week: int | None = None
        self.session_duration: float | None = None
        self.command_count: int = 0
        self.commands_used: list[str] = []
    
    def record_typing_time(self, start: float, end: float) -> float:
        self.typing_time = end - start
        return self.typing_time
    
    def record_typing_time_direct(self, duration: float) -> None:
        self.typing_time = duration
    
    def record_login_time(self) -> dict:
        now = datetime.now()
        self.login_hour = now.hour
        self.login_day_of_week = now.weekday()
        return {
            "hour": self.login_hour,
            "day_of_week": self.login_day_of_week,
            "timestamp": now.isoformat()
        }
    
    def record_command(self, command_name: str) -> None:
        self.commands_used.append(command_name)
        self.command_count += 1
    
    def end_session(self) -> float:
        end_time = datetime.now().timestamp()
        self.session_duration = end_time - self.session_start
        return self.session_duration
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "typing_time": self.typing_time,
            "login_hour": self.login_hour,
            "login_day_of_week": self.login_day_of_week,
            "session_duration": self.session_duration,
            "command_count": self.command_count,
            "commands_used": self.commands_used,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }
    
    def save(self) -> int:
        from database.models import create_behavior_log
        
        log_id = create_behavior_log(
            user_id=self.user_id,
            typing_time=self.typing_time,
            login_hour=self.login_hour,
            login_day_of_week=self.login_day_of_week,
            session_duration=self.session_duration,
            command_count=self.command_count,
            commands_used=self.commands_used,
            ip_address=self.ip_address,
            user_agent=self.user_agent
        )
        return log_id


def create_capture_context(
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
    typing_time: float = None
) -> CaptureContext:
    ctx = CaptureContext(user_id, ip_address, user_agent)
    
    if typing_time is not None:
        ctx.record_typing_time_direct(typing_time)
    
    ctx.record_login_time()
    
    return ctx


def capture_behavior_from_login(
    user_id: int,
    typing_time: float,
    ip_address: str = None,
    user_agent: str = None
) -> CaptureContext:
    ctx = create_capture_context(user_id, ip_address, user_agent, typing_time)
    return ctx
