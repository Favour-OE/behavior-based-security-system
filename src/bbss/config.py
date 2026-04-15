import os
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance: Optional['Config'] = None
    _overrides: dict[str, Any] = {}

    def __init__(self, **overrides):
        self._overrides = overrides
        self._load_from_env()
        self._apply_overrides()

    def _load_from_env(self):
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "./bbss.db")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
        self.MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
        self.LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
        self.MIN_SESSIONS_BOOTSTRAPPING = int(os.getenv("MIN_SESSIONS_BOOTSTRAPPING", "5"))
        self.MIN_SESSIONS_WARMUP = int(os.getenv("MIN_SESSIONS_WARMUP", "10"))
        self.ZSCORE_THRESHOLD = float(os.getenv("ZSCORE_THRESHOLD", "2.0"))
        self.IQR_MULTIPLIER = float(os.getenv("IQR_MULTIPLIER", "1.5"))
        self.RISK_WEIGHT_TYPING_TIME = int(os.getenv("RISK_WEIGHT_TYPING_TIME", "20"))
        self.RISK_WEIGHT_LOGIN_HOUR = int(os.getenv("RISK_WEIGHT_LOGIN_HOUR", "25"))
        self.RISK_WEIGHT_LOGIN_DAY = int(os.getenv("RISK_WEIGHT_LOGIN_DAY", "10"))
        self.RISK_WEIGHT_UNKNOWN_IP = int(os.getenv("RISK_WEIGHT_UNKNOWN_IP", "20"))
        self.RISK_WEIGHT_COMMAND_COUNT = int(os.getenv("RISK_WEIGHT_COMMAND_COUNT", "15"))
        self.RISK_WEIGHT_UNKNOWN_COMMANDS = int(os.getenv("RISK_WEIGHT_UNKNOWN_COMMANDS", "10"))
        self.RISK_WEIGHT_SESSION_DURATION = int(os.getenv("RISK_WEIGHT_SESSION_DURATION", "10"))
        self.RISK_WEIGHT_ML_FLAG = int(os.getenv("RISK_WEIGHT_ML_FLAG", "30"))
        self.RISK_THRESHOLD_WARNING = int(os.getenv("RISK_THRESHOLD_WARNING", "31"))
        self.RISK_THRESHOLD_HIGH = int(os.getenv("RISK_THRESHOLD_HIGH", "61"))
        self.LOG_DIR = os.getenv("LOG_DIR", "./logs")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
        self.CONSOLE_LOGGING = os.getenv("CONSOLE_LOGGING", "true").lower() == "true"
        self.ML_ENABLED = os.getenv("ML_ENABLED", "true").lower() == "true"
        self.ML_MIN_SESSIONS_FOR_TRAINING = int(os.getenv("ML_MIN_SESSIONS_FOR_TRAINING", "20"))
        self.ML_RETRAIN_EVERY_N_SESSIONS = int(os.getenv("ML_RETRAIN_EVERY_N_SESSIONS", "10"))
        self.ML_MODELS_DIR = os.getenv("ML_MODELS_DIR", "./ml/models")
        self.ML_ISOLATION_FOREST_CONTAMINATION = float(os.getenv("ML_ISOLATION_FOREST_CONTAMINATION", "0.1"))
        self.ML_ANOMALY_THRESHOLD = float(os.getenv("ML_ANOMALY_THRESHOLD", "-0.1"))

    def _apply_overrides(self):
        for key, value in self._overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown config option: {key}")

    @classmethod
    def get_instance(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, config: 'Config'):
        cls._instance = config

    @classmethod
    def reset(cls):
        cls._instance = None


def get_config() -> Config:
    return Config.get_instance()


def configure(**overrides) -> Config:
    config = Config(**overrides)
    Config.set_instance(config)
    return config
