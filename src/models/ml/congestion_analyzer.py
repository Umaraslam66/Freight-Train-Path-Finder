import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict
from datetime import datetime
from ...models.core.train import TrainPath
import pandas as pd
from prophet import Prophet

class CongestionAnalyzer:
    def __init__(self):
        self.model = DBSCAN(eps=30, min_samples=2)  # eps in minutes
    
    def analyze_congestion(self, paths: List[TrainPath]) -> Dict:
        """Analyze congestion patterns in the schedule"""
        if not paths:
            return {}
            
        # Convert times to minutes since midnight
        all_times = []
        sections = []
        for path in paths:
            for section_id, time, _ in path.schedule:
                minutes = time.hour * 60 + time.minute
                all_times.append(minutes)
                sections.append(section_id)
        
        # Create feature matrix for clustering
        X = np.column_stack([all_times, [hash(s) % 100 for s in sections]])
        
        if len(X) > 0:
            clusters = self.model.fit_predict(X)
            
            # Analyze clusters
            congestion_patterns = {}
            for cluster_id in set(clusters):
                if cluster_id != -1:  # Ignore noise
                    cluster_points = X[clusters == cluster_id]
                    congestion_patterns[f"cluster_{cluster_id}"] = {
                        "time_range": (
                            int(cluster_points[:, 0].min()),
                            int(cluster_points[:, 0].max())
                        ),
                        "sections": [s for i, s in enumerate(sections) 
                                   if clusters[i] == cluster_id],
                        "density": len(cluster_points)
                    }
            
            return congestion_patterns
        return {}
    
class CongestionPredictor:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True
        )
        
    def train(self, historical_data: pd.DataFrame):
        """Train on historical congestion data"""
        df = historical_data.copy()
        df.columns = ['ds', 'y']  # Prophet requires these column names
        self.model.fit(df)
        
    def predict_congestion(self, future_dates: pd.DataFrame) -> pd.DataFrame:
        """Predict future congestion levels"""
        future_dates.columns = ['ds']
        forecast = self.model.predict(future_dates)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    



    #pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org lightgbm