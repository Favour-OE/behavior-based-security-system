import pytest
import numpy as np
from ml.features import extract_features_from_log, extract_features_from_behavior, prepare_training_data
from ml.model import AnomalyDetector


class TestFeatures:
    def test_extract_features_from_log(self):
        log = {
            "typing_time": 2.0,
            "login_hour": 10,
            "login_day_of_week": 1,
            "session_duration": 300.0,
            "command_count": 5
        }
        features = extract_features_from_log(log)
        
        assert len(features) == 5
        assert features[0] == 2.0
        assert features[1] == 10 / 24.0
        assert features[2] == 1 / 6.0
        assert features[3] == 300.0
        assert features[4] == 5 / 100.0
    
    def test_extract_features_from_behavior(self):
        behavior = {
            "typing_time": 1.5,
            "login_hour": 14,
            "login_day_of_week": 3,
            "session_duration": 600.0,
            "command_count": 10
        }
        features = extract_features_from_behavior(behavior)
        
        assert len(features) == 5
        assert features[0] == 1.5
        assert features[1] == 14 / 24.0
    
    def test_prepare_training_data(self):
        logs = [
            {"typing_time": 2.0, "login_hour": 10, "login_day_of_week": 1, "session_duration": 300.0, "command_count": 5},
            {"typing_time": 2.5, "login_hour": 11, "login_day_of_week": 2, "session_duration": 350.0, "command_count": 7},
        ]
        X = prepare_training_data(logs)
        
        assert X.shape == (2, 5)
    
    def test_prepare_training_data_empty(self):
        X = prepare_training_data([])
        assert len(X) == 0


class TestAnomalyDetector:
    def test_init_creates_detector(self, test_db):
        detector = AnomalyDetector(user_id=999)
        assert detector.user_id == 999
        assert detector.model is None
    
    def test_is_trained_false_initially(self, test_db):
        detector = AnomalyDetector(user_id=999)
        assert detector.is_trained() is False
    
    def test_train_with_insufficient_data(self, test_db):
        detector = AnomalyDetector(user_id=999)
        X = np.array([[1.0, 0.5, 0.1, 100.0, 0.05]])
        result = detector.train(X)
        assert result is False
    
    def test_train_with_sufficient_data(self, test_db):
        detector = AnomalyDetector(user_id=999)
        X = np.array([
            [2.0, 0.4, 0.2, 300.0, 0.05],
            [2.2, 0.4, 0.2, 310.0, 0.06],
            [1.8, 0.4, 0.2, 290.0, 0.04],
            [2.1, 0.4, 0.2, 305.0, 0.05],
            [1.9, 0.4, 0.2, 295.0, 0.05],
        ])
        result = detector.train(X)
        assert result is True
        assert detector.is_trained() is True
    
    def test_predict_no_model(self, test_db):
        detector = AnomalyDetector(user_id=999)
        detector.delete_model()
        
        features = np.array([2.0, 0.4, 0.2, 300.0, 0.05])
        result = detector.predict(features)
        
        assert result["anomaly"] is False
        assert result["score"] == 0.0
    
    def test_predict_with_model(self, test_db):
        detector = AnomalyDetector(user_id=998)
        X = np.array([
            [2.0, 0.4, 0.2, 300.0, 0.05],
            [2.2, 0.4, 0.2, 310.0, 0.06],
            [1.8, 0.4, 0.2, 290.0, 0.04],
            [2.1, 0.4, 0.2, 305.0, 0.05],
            [1.9, 0.4, 0.2, 295.0, 0.05],
        ])
        detector.train(X)
        
        features = np.array([2.0, 0.4, 0.2, 300.0, 0.05])
        result = detector.predict(features)
        
        assert "anomaly" in result
        assert "score" in result
