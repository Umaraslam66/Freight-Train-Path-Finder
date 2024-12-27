from typing import List, Tuple
from datetime import datetime, timedelta
from ..models.core.train import TrainPath

class ConflictChecker:
    def __init__(self, min_headway_minutes: float = 5):
        self.min_headway = timedelta(minutes=min_headway_minutes)
    
    def check_conflicts(self, path: TrainPath, existing_paths: List[TrainPath]) -> List[dict]:
        """Check for conflicts between proposed path and existing paths"""
        conflicts = []
        print(f"\nChecking conflicts for train {path.train.id}")
        
        for existing_path in existing_paths:
            # Skip paths in opposite direction (already handled by crossing check)
            if path.train.direction != existing_path.train.direction:
                continue
                
            for (section1, time1, dwell1), (section2, time2, dwell2) in zip(
                path.schedule, existing_path.schedule
            ):
                if section1 == section2:  # Same section
                    # Consider dwell times in conflict detection
                    path_start = time1
                    path_end = time1 + timedelta(minutes=dwell1)
                    existing_start = time2
                    existing_end = time2 + timedelta(minutes=dwell2)
                    
                    # Check if time windows overlap considering headway
                    if (
                        path_start <= existing_end + self.min_headway and 
                        existing_start <= path_end + self.min_headway
                    ):
                        conflicts.append({
                            'section': section1,
                            'train1': path.train.id,
                            'train2': existing_path.train.id,
                            'time': time1,
                            'dwell_time': dwell1,
                            'conflict_type': 'headway_violation',
                            'headway_violation': (
                                self.min_headway - min(
                                    abs(path_end - existing_start),
                                    abs(existing_end - path_start)
                                )
                            ).total_seconds() / 60
                        })
                        print(f"Found conflict in section {section1} between {path.train.id} and {existing_path.train.id}")
        
        return conflicts