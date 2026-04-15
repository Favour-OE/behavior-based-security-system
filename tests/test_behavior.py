import pytest
from datetime import datetime
from behavior.capture import CaptureContext, create_capture_context, capture_behavior_from_login


class TestCaptureContext:
    def test_create_context(self):
        ctx = CaptureContext(user_id=1, ip_address="192.168.1.1", user_agent="TestBrowser/1.0")
        assert ctx.user_id == 1
        assert ctx.ip_address == "192.168.1.1"
        assert ctx.command_count == 0
        assert len(ctx.commands_used) == 0
    
    def test_record_typing_time_direct(self):
        ctx = CaptureContext(user_id=1)
        ctx.record_typing_time_direct(2.5)
        assert ctx.typing_time == 2.5
    
    def test_record_typing_time_calculated(self):
        ctx = CaptureContext(user_id=1)
        duration = ctx.record_typing_time(start=100.0, end=102.5)
        assert duration == 2.5
        assert ctx.typing_time == 2.5
    
    def test_record_login_time(self):
        ctx = CaptureContext(user_id=1)
        info = ctx.record_login_time()
        assert "hour" in info
        assert "day_of_week" in info
        assert ctx.login_hour == datetime.now().hour
        assert ctx.login_day_of_week == datetime.now().weekday()
    
    def test_record_commands(self):
        ctx = CaptureContext(user_id=1)
        ctx.record_command("view_report")
        ctx.record_command("export_data")
        ctx.record_command("delete_record")
        assert ctx.command_count == 3
        assert ctx.commands_used == ["view_report", "export_data", "delete_record"]
    
    def test_end_session(self):
        ctx = CaptureContext(user_id=1)
        assert ctx.session_duration is None
        duration = ctx.end_session()
        assert duration >= 0
        assert ctx.session_duration is not None
    
    def test_to_dict(self):
        ctx = CaptureContext(user_id=1, ip_address="10.0.0.1")
        ctx.record_typing_time_direct(1.5)
        ctx.record_login_time()
        ctx.record_command("test_cmd")
        ctx.end_session()
        
        data = ctx.to_dict()
        assert data["user_id"] == 1
        assert data["typing_time"] == 1.5
        assert data["ip_address"] == "10.0.0.1"
        assert data["command_count"] == 1
        assert "test_cmd" in data["commands_used"]
    
    def test_save_to_database(self, test_db, sample_user):
        ctx = CaptureContext(user_id=sample_user["user_id"], ip_address="172.16.0.1")
        ctx.record_typing_time_direct(2.0)
        ctx.record_login_time()
        ctx.record_command("cmd1")
        ctx.end_session()
        
        log_id = ctx.save()
        assert log_id is not None
        
        from database.models import get_behavior_log_by_id
        log = get_behavior_log_by_id(log_id)
        assert log is not None
        assert log["user_id"] == sample_user["user_id"]
        assert log["typing_time"] == 2.0
        assert log["command_count"] == 1


class TestCaptureFactory:
    def test_create_capture_context(self):
        ctx = create_capture_context(user_id=1, typing_time=3.0, ip_address="192.168.1.100")
        assert ctx.user_id == 1
        assert ctx.typing_time == 3.0
        assert ctx.ip_address == "192.168.1.100"
        assert ctx.login_hour is not None
        assert ctx.login_day_of_week is not None
    
    def test_capture_behavior_from_login(self):
        ctx = capture_behavior_from_login(user_id=5, typing_time=1.5, ip_address="10.10.10.10")
        assert ctx.user_id == 5
        assert ctx.typing_time == 1.5
        assert ctx.ip_address == "10.10.10.10"
