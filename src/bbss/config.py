import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./bcss.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
    MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
    MIN_SESSIONS_BOOTSTRAPPING = int(os.getenv("MIN_SESSIONS_BOOTSTRAPPING", "5"))
    MIN_SESSIONS_WARMUP = int(os.getenv("MIN_SESSIONS_WARMUP", "10"))
    ZSCORE_THRESHOLD = float(os.getenv("ZSCORE_THRESHOLD", "2.0"))
    IQR_MULTIPLIER = float(os.getenv("IQR_MULTIPLIER", "1.5"))
    RISK_WEIGHT_TYPING_TIME = int(os.getenv("RISK_WEIGHT_TYPING_TIME", "20"))
    RISK_WEIGHT_LOGIN_HOUR = int(os.getenv("RISK_WEIGHT_LOGIN_HOUR", "25"))
    RISK_WEIGHT_LOGIN_DAY = int(os.getenv("RISK_WEIGHT_LOGIN_DAY", "10"))
    RISK_WEIGHT_UNKNOWN_IP = int(os.getenv("RISK_WEIGHT_UNKNOWN_IP", "20"))
    RISK_WEIGHT_COMMAND_COUNT = int(os.getenv("RISK_WEIGHT_COMMAND_COUNT", "15"))
    RISK_WEIGHT_UNKNOWN_COMMANDS = int(os.getenv("RISK_WEIGHT_UNKNOWN_COMMANDS", "10"))
    RISK_WEIGHT_SESSION_DURATION = int(os.getenv("RISK_WEIGHT_SESSION_DURATION", "10"))
    RISK_WEIGHT_ML_FLAG = int(os.getenv("RISK_WEIGHT_ML_FLAG", "30"))
    RISK_THRESHOLD_WARNING = int(os.getenv("RISK_THRESHOLD_WARNING", "31"))
    RISK_THRESHOLD_HIGH = int(os.getenv("RISK_THRESHOLD_HIGH", "61"))
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
    CONSOLE_LOGGING = os.getenv("CONSOLE_LOGGING", "true").lower() == "true"
    ML_ENABLED = os.getenv("ML_ENABLED", "true").lower() == "true"
    ML_MIN_SESSIONS_FOR_TRAINING = int(os.getenv("ML_MIN_SESSIONS_FOR_TRAINING", "20"))
    ML_RETRAIN_EVERY_N_SESSIONS = int(os.getenv("ML_RETRAIN_EVERY_N_SESSIONS", "10"))
    ML_MODELS_DIR = os.getenv("ML_MODELS_DIR", "./ml/models")
    ML_ISOLATION_FOREST_CONTAMINATION = float(os.getenv("ML_ISOLATION_FOREST_CONTAMINATION", "0.1"))
    ML_ANOMALY_THRESHOLD = float(os.getenv("ML_ANOMALY_THRESHOLD", "-0.1"))


config = Config()
