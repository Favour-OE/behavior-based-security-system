"""
BBSS - Behavior-Based Security System

Main entry point providing integrated functions for authentication,
behavior tracking, and security response.
"""

from typing import Dict, Optional
from database.db import init_db
from auth.signup import signup as _signup
from auth.login import login as _login
from behavior.capture import CaptureContext, capture_behavior_from_login
from behavior.profile import get_or_create_profile, update_profile
from behavior.anomaly import detect_anomalies
from security.risk import compute_risk_score, classify_risk
from security.response import dispatch_response
from database.models import create_risk_log, increment_profile_session_count, get_behavior_logs_by_user


class Session:
    def __init__(self, user_id: int, token: str, session_id: int, capture_ctx: CaptureContext):
        self.user_id = user_id
        self.token = token
        self.session_id = session_id
        self.capture_ctx = capture_ctx
        self._pending_pin: Optional[str] = None
        self._verified = False
    
    def add_command(self, command_name: str):
        self.capture_ctx.record_command(command_name)
    
    def end(self):
        self.capture_ctx.end_session()
        log_id = self.capture_ctx.save()
        update_profile(self.user_id)
        increment_profile_session_count(self.user_id)
        return log_id


class BBSS:
    def __init__(self):
        init_db()
    
    def signup(self, username: str, password: str, email: str = None) -> Dict:
        return _signup(username, password, email)
    
    def login(
        self,
        username: str,
        password: str,
        typing_time: float = 0.0,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict:
        login_result = _login(username, password, typing_time, ip_address, user_agent)
        
        if not login_result["success"]:
            return {"success": False, "error": login_result["error"], **login_result}
        
        user_id = login_result["user_id"]
        session_token = login_result["session_token"]
        session_id = login_result["session_id"]
        capture_ctx = login_result.get("capture_context")
        
        profile = get_or_create_profile(user_id)
        profile_logs = get_behavior_logs_by_user(user_id, limit=50)
        
        current_behavior = capture_ctx.to_dict()
        anomaly_signals = detect_anomalies(current_behavior, profile, profile_logs)
        
        risk_score = compute_risk_score(anomaly_signals)
        risk_level = classify_risk(risk_score)
        
        session = None
        requires_verification = False
        pin = None
        
        response = dispatch_response(
            risk_level=risk_level,
            user_id=user_id,
            session_id=session_id,
            session_token=session_token
        )
        
        if response["action"] == "ALLOW":
            session = Session(user_id, session_token, session_id, capture_ctx)
        elif response["action"] == "CHALLENGE":
            requires_verification = True
            pin = response["pin"]
        elif response["action"] == "BLOCK":
            return {
                "success": False,
                "session_token": None,
                "session": None,
                "user_id": user_id,
                "risk_score": risk_score,
                "decision": "BLOCK",
                "anomaly_signals": anomaly_signals,
                "requires_verification": False,
                "pin": None,
                "error": "Session blocked due to security concerns"
            }
        
        behavior_log_id = capture_ctx.save()
        
        create_risk_log(
            user_id=user_id,
            behavior_log_id=behavior_log_id,
            risk_score=risk_score,
            risk_level=risk_level,
            anomaly_signals=anomaly_signals,
            decision="ALLOW" if session else "CHALLENGE",
            secondary_auth=False,
            secondary_passed=None
        )
        
        return {
            "success": True,
            "session_token": session_token,
            "session": session,
            "user_id": user_id,
            "risk_score": risk_score,
            "decision": "ALLOW" if session else "CHALLENGE",
            "anomaly_signals": anomaly_signals,
            "requires_verification": requires_verification,
            "pin": pin,
            "error": None
        }
    
    def execute_command(self, session: Session, command_name: str) -> Dict:
        if not isinstance(session, Session):
            return {"success": False, "message": "Invalid session"}
        
        session.add_command(command_name)
        return {"success": True, "message": f"Command '{command_name}' recorded"}
    
    def end_session(self, session: Session) -> Dict:
        if not isinstance(session, Session):
            return {"success": False, "behavior_log_id": None}
        
        log_id = session.end()
        return {"success": True, "behavior_log_id": log_id}
    
    def get_user_report(self, user_id: int) -> Dict:
        from logs.audit import get_user_security_report
        return get_user_security_report(user_id)


_engine = None


def get_engine() -> BBSS:
    global _engine
    if _engine is None:
        _engine = BBSS()
    return _engine


def signup(username: str, password: str, email: str = None) -> Dict:
    return get_engine().signup(username, password, email)


def login(username: str, password: str, typing_time: float = 0.0,
          ip_address: str = None, user_agent: str = None) -> Dict:
    return get_engine().login(username, password, typing_time, ip_address, user_agent)


def execute_command(session: Session, command_name: str) -> Dict:
    return get_engine().execute_command(session, command_name)


def end_session(session: Session) -> Dict:
    return get_engine().end_session(session)
