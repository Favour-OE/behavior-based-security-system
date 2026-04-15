import os
from typing import List, Optional
from ..database.models import get_behavior_logs_by_user, get_profile
from .features import prepare_training_data
from .model import AnomalyDetector
from ..config import config


class ModelTrainer:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.detector = AnomalyDetector(user_id)
        self.profile = get_profile(user_id)
        self.sessions_trained = 0
    
    def should_train(self) -> bool:
        if not config.ML_ENABLED:
            return False
        
        if self.profile is None:
            return False
        
        session_count = self.profile.get("session_count", 0)
        
        if session_count < config.ML_MIN_SESSIONS_FOR_TRAINING:
            return False
        
        trained_sessions = self._get_trained_sessions()
        needs_retrain = (session_count - trained_sessions) >= config.ML_RETRAIN_EVERY_N_SESSIONS
        
        return needs_retrain or not self.detector.is_trained()
    
    def _get_trained_sessions(self) -> int:
        model_path = os.path.join(config.ML_MODELS_DIR, f"user_{self.user_id}.pkl")
        if not os.path.exists(model_path):
            return 0
        
        session_count = self.profile.get("session_count", 0) if self.profile else 0
        previous_trainings = (session_count // config.ML_RETRAIN_EVERY_N_SESSIONS) * config.ML_RETRAIN_EVERY_N_SESSIONS
        return previous_trainings
    
    def train(self) -> bool:
        if not config.ML_ENABLED:
            return False
        
        logs = get_behavior_logs_by_user(self.user_id, limit=100)
        
        if len(logs) < config.ML_MIN_SESSIONS_FOR_TRAINING:
            return False
        
        X = prepare_training_data(logs)
        
        if len(X) == 0:
            return False
        
        success = self.detector.train(X)
        
        if success:
            self.sessions_trained = self.profile.get("session_count", 0) if self.profile else 0
        
        return success
    
    def detect_anomaly(self, behavior: dict) -> Optional[dict]:
        if not config.ML_ENABLED:
            return None
        
        if not self.detector.is_trained():
            return None
        
        from .features import extract_features_from_behavior
        features = extract_features_from_behavior(behavior)
        
        return self.detector.predict(features)


def get_trainer(user_id: int) -> Optional[ModelTrainer]:
    if not config.ML_ENABLED:
        return None
    
    trainer = ModelTrainer(user_id)
    
    if trainer.should_train():
        trainer.train()
    
    return trainer


def detect_ml_anomaly(user_id: int, behavior: dict) -> Optional[dict]:
    trainer = get_trainer(user_id)
    if trainer is None:
        return None
    
    return trainer.detect_anomaly(behavior)
