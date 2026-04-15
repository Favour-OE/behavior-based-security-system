import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Optional
from ..config import get_config


class AnomalyDetector:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.model: Optional[IsolationForest] = None
        self._ensure_models_dir()
        self._load_model()
    
    def _get_model_path(self) -> str:
        config = get_config()
        return os.path.join(config.ML_MODELS_DIR, f"user_{self.user_id}.pkl")
    
    def _ensure_models_dir(self):
        config = get_config()
        os.makedirs(config.ML_MODELS_DIR, exist_ok=True)
    
    def _load_model(self):
        model_path = self._get_model_path()
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception:
                self.model = None
    
    def _save_model(self):
        config = get_config()
        if self.model is not None:
            joblib.dump(self.model, self._get_model_path())
    
    def train(self, X: np.ndarray) -> bool:
        config = get_config()
        if len(X) < 5:
            return False
        
        try:
            self.model = IsolationForest(
                contamination=config.ML_ISOLATION_FOREST_CONTAMINATION,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(X)
            self._save_model()
            return True
        except Exception:
            return False
    
    def predict(self, X: np.ndarray) -> dict:
        config = get_config()
        if self.model is None:
            return {"anomaly": False, "score": 0.0}
        
        try:
            prediction = self.model.predict([X])[0]
            score = self.model.score_samples([X])[0]
            
            is_anomaly = prediction == -1 or score < config.ML_ANOMALY_THRESHOLD
            
            return {
                "anomaly": bool(is_anomaly),
                "score": float(score),
                "threshold": config.ML_ANOMALY_THRESHOLD
            }
        except Exception:
            return {"anomaly": False, "score": 0.0}
    
    def is_trained(self) -> bool:
        return self.model is not None
    
    def delete_model(self):
        model_path = self._get_model_path()
        if os.path.exists(model_path):
            os.remove(model_path)
        self.model = None
