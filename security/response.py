import secrets
from security.risk import RISK_LEVEL_SAFE, RISK_LEVEL_WARNING, RISK_LEVEL_HIGH_RISK
from database.models import deactivate_session_by_id


def generate_pin() -> str:
    return str(secrets.randbelow(900000) + 100000)


def verify_pin(input_pin: str, correct_pin: str) -> bool:
    return input_pin == correct_pin


def dispatch_response(
    risk_level: str,
    user_id: int,
    session_id: int,
    session_token: str = None
) -> dict:
    if risk_level == RISK_LEVEL_SAFE:
        return {
            "action": "ALLOW",
            "requires_pin": False,
            "pin": None,
            "message": "Session allowed"
        }
    elif risk_level == RISK_LEVEL_WARNING:
        challenge_pin = generate_pin()
        return {
            "action": "CHALLENGE",
            "requires_pin": True,
            "pin": challenge_pin,
            "message": "Verification required due to unusual activity"
        }
    elif risk_level == RISK_LEVEL_HIGH_RISK:
        if session_id:
            deactivate_session_by_id(session_id)
        return {
            "action": "BLOCK",
            "requires_pin": False,
            "pin": None,
            "message": "Session blocked due to high risk score"
        }
    return {
        "action": "CHALLENGE",
        "requires_pin": True,
        "pin": generate_pin(),
        "message": "Verification required"
    }


def verify_challenge(user_input_pin: str, correct_pin: str) -> dict:
    passed = verify_pin(user_input_pin, correct_pin)
    return {
        "passed": passed,
        "message": "Verification passed" if passed else "Verification failed"
    }
