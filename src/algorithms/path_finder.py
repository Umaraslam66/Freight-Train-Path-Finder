from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
from ..models.core.train import TrainPath, TrainService
from ..models.core.infrastructure import Infrastructure, Direction
from .conflict_checker import ConflictChecker
from ..models.ml.path_success_predictor import PathSuccessPredictor
from ..models.ml.congestion_analyzer import CongestionAnalyzer

class PathFinder:
    def __init__(self, 
                 infrastructure,
                 success_predictor,
                 congestion_analyzer):
        """Initialize PathFinder with required components"""
        self.infrastructure = infrastructure
        self.success_predictor = success_predictor
        self.congestion_analyzer = congestion_analyzer
        self.conflict_checker = ConflictChecker()

    def _is_path_crossing(self, new_path: TrainPath, existing_paths: List[TrainPath]) -> bool:
        """Check if the new path crosses any existing paths in the opposite direction"""
        print(f"\nChecking path crossing for train {new_path.train.id}")
        for existing_path in existing_paths:
            # Only check paths in opposite direction
            if new_path.train.direction != existing_path.train.direction:
                new_times = [t for _, t, _ in new_path.schedule]
                new_sections = [s.split('_')[0] for s, _, _ in new_path.schedule]  # Remove UP/DOWN suffix
                
                existing_times = [t for _, t, _ in existing_path.schedule]
                existing_sections = [s.split('_')[0] for s, _, _ in existing_path.schedule]
                
                print(f"Comparing with {existing_path.train.id}:")
                print(f"New path sections: {new_sections}")
                print(f"Existing path sections: {existing_sections}")
                
                # Check for crossings
                for i in range(len(new_sections) - 1):
                    for j in range(len(existing_sections) - 1):
                        if (new_sections[i] == existing_sections[j]):
                            # Same section, check times
                            if (min(new_times[i+1], existing_times[j+1]) > 
                                max(new_times[i], existing_times[j])):
                                print(f"Found crossing at section {new_sections[i]}")
                                return True
        return False

    def generate_candidate_paths(self, 
                           train: TrainService,
                           start_time: datetime,
                           existing_paths: List[TrainPath],
                           num_candidates: int = 5) -> List[TrainPath]:
        """Generate candidate paths considering direction and dwell times"""
        print(f"\nGenerating candidate paths for train {train.id} - Direction: {train.direction.value}")
        candidates = []
        time_step = 10
        attempts = 0
        max_attempts = 20
        
        while len(candidates) < num_candidates and attempts < max_attempts:
            departure_time = start_time + timedelta(minutes=time_step * attempts)
            print(f"\nAttempt {attempts + 1} with departure time {departure_time.strftime('%H:%M')}")
            
            # Get sections for the correct direction
            direction_suffix = "_UP" if train.direction == Direction.UP else "_DOWN"
            
            # Fix the section ordering based on direction
            if train.direction == Direction.UP:
                # For UP trains: Start at A, go through B, end at C
                section_order = ["SEC1", "SEC2", "SEC3"]
            else:
                # For DOWN trains: Start at C, go through B, end at A
                section_order = ["SEC3", "SEC2", "SEC1"]
            
            # Create sections list with direction suffix
            relevant_sections = [f"{sec}{direction_suffix}" for sec in section_order]
            print(f"Section sequence: {relevant_sections}")
            
            schedule = []
            platforms = []
            current_time = departure_time
            
            for section_id in relevant_sections:
                section = self.infrastructure.sections[section_id]
                # Calculate running time
                speed = min(train.max_speed, section.max_speed)
                running_time = (section.length / speed) * 60
                
                # Calculate dwell time if platform exists
                dwell_time = 0.0
                if section.has_platforms:
                    dwell_time = random.uniform(train.min_dwell_time, train.max_dwell_time)
                    platform = random.choice(section.platforms)
                    platforms.append(platform)
                else:
                    platforms.append("")
                
                schedule.append((section_id, current_time, dwell_time))
                current_time += timedelta(minutes=int(running_time + dwell_time))
                print(f"Added section {section_id} at {current_time.strftime('%H:%M')}")
            
            # Create path
            speeds = [min(train.max_speed, self.infrastructure.sections[s].max_speed) 
                    for s, _, _ in schedule]
            
            candidate_path = TrainPath(train, schedule, speeds, platforms)
            
            if not self._is_path_crossing(candidate_path, existing_paths):
                print(f"Found valid path with departure {departure_time.strftime('%H:%M')}")
                candidates.append(candidate_path)
            
            attempts += 1
        
        print(f"\nGenerated {len(candidates)} valid paths out of {attempts} attempts")
        return candidates

    def find_best_path(self, 
                      train: TrainService,
                      start_time: datetime,
                      existing_paths: List[TrainPath]) -> Optional[TrainPath]:
        """Find the best path for a train"""
        candidates = self.generate_candidate_paths(train, start_time, existing_paths)
        
        if not candidates:
            return None
            
        best_path = None
        best_score = -1
        
        print("\nEvaluating candidate paths:")
        for path in candidates:
            # Check conflicts
            conflicts = self.conflict_checker.check_conflicts(path, existing_paths)
            if not conflicts:
                # Predict success probability
                success_prob = self.success_predictor.predict_success_probability(path)
                print(f"Path starting at {path.schedule[0][1].strftime('%H:%M')} has success probability {success_prob:.2f}")
                
                if success_prob > best_score:
                    best_score = success_prob
                    best_path = path
        
        if best_path:
            print(f"\nSelected best path with success probability {best_score:.2f}")
        
        return best_path