import numpy as np
from lightgbm import LGBMClassifier
from typing import List
from ...models.core.train import TrainPath

class PathSuccessPredictor:
    def __init__(self):
        self.model = LGBMClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            num_leaves=20,
            min_child_samples=5
        )
    
    def _extract_features(self, path: TrainPath) -> np.ndarray:
        """Extract meaningful features from a train path"""
        # Time features
        start_time = path.schedule[0][1].hour + path.schedule[0][1].minute / 60
        end_time = path.schedule[-1][1].hour + path.schedule[-1][1].minute / 60
        duration = end_time - start_time if end_time > start_time else (24 + end_time - start_time)
        
        # Speed features
        avg_speed = np.mean(path.speeds)
        speed_std = np.std(path.speeds)
        
        # Dwell time features
        dwell_times = [dt for _, _, dt in path.schedule]
        avg_dwell = np.mean(dwell_times)
        total_dwell = np.sum(dwell_times)
        
        # Create feature array
        features = np.array([
            start_time,
            duration,
            avg_speed,
            speed_std,
            avg_dwell,
            total_dwell,
            path.train.max_speed,
            path.train.length,
            path.train.acceleration,
            path.train.deceleration,
            1 if path.train.train_type == "passenger" else 0,  # Train type as binary
            1 if path.train.direction.value == "up" else 0,    # Direction as binary
        ])
        
        return features.reshape(1, -1)
    
    def train(self, paths: List[TrainPath], success_labels: List[bool]):
        """Train the success predictor"""
        X = np.vstack([self._extract_features(path) for path in paths])
        print(f"\nTraining with {X.shape[1]} features, {len(paths)} samples")
        print("Feature values sample:", X[0])
        self.model.fit(X, success_labels)
    
    def predict_success_probability(self, path: TrainPath) -> float:
        """Predict the probability of a path being successful"""
        features = self._extract_features(path)
        try:
            return self.model.predict_proba(features)[0][1]
        except:
            return 0.5  # Default to neutral probability if prediction fails