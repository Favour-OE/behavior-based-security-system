import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import config

LOG_DIR = config.LOG_DIR
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "security.log")


class SecurityLogFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logger():
    logger = logging.getLogger("bcss.security")
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    logger.handlers = []
    
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=config.LOG_RETENTION_DAYS
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(SecurityLogFormatter())
    logger.addHandler(file_handler)
    
    if config.CONSOLE_LOGGING:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


_logger = None


def get_logger():
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def log_event(
    event_type: str,
    user_id: int = None,
    username: str = None,
    risk_score: int = None,
    anomaly_signals: list = None,
    behavior_snapshot: dict = None,
    decision: str = None,
    level: str = "INFO",
    message: str = None
):
    logger = get_logger()
    
    extra_data = {
        "event_type": event_type,
        "user_id": user_id,
        "username": username,
        "risk_score": risk_score,
        "anomaly_signals": anomaly_signals or [],
        "behavior_snapshot": behavior_snapshot or {},
        "decision": decision,
        "message": message
    }
    
    record = logging.LogRecord(
        name="bcss.security",
        level=getattr(logging, level.upper(), logging.INFO),
        pathname="",
        lineno=0,
        msg=message or event_type,
        args=(),
        exc_info=None
    )
    record.extra_data = extra_data
    
    logger.handle(record)


def log_login_attempt(username: str, success: bool, reason: str = None, user_id: int = None):
    if success:
        log_event(
            event_type="LOGIN_ATTEMPT",
            username=username,
            user_id=user_id,
            level="INFO",
            message=f"Successful login for {username}"
        )
    else:
        log_event(
            event_type="LOGIN_ATTEMPT_FAILED",
            username=username,
            user_id=user_id,
            level="WARNING",
            message=f"Failed login attempt for {username}: {reason}"
        )


def log_security_decision(
    user_id: int,
    username: str,
    risk_score: int,
    anomaly_signals: list,
    decision: str,
    behavior_snapshot: dict
):
    if decision == "ALLOW":
        level = "INFO"
    elif decision == "CHALLENGE":
        level = "WARNING"
    else:
        level = "ERROR"
    
    log_event(
        event_type=f"LOGIN_{decision}",
        user_id=user_id,
        username=username,
        risk_score=risk_score,
        anomaly_signals=anomaly_signals,
        behavior_snapshot=behavior_snapshot,
        decision=decision,
        level=level,
        message=f"Security decision: {decision} (score: {risk_score})"
    )


def log_capture_error(operation: str, error: str, user_id: int = None):
    log_event(
        event_type="CAPTURE_ERROR",
        user_id=user_id,
        level="ERROR",
        message=f"Behavior capture error in {operation}: {error}"
    )


def log_system_error(operation: str, error: str, user_id: int = None):
    log_event(
        event_type="SYSTEM_ERROR",
        user_id=user_id,
        level="CRITICAL",
        message=f"System error in {operation}: {error}"
    )
