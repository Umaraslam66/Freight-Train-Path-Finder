from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import random
from ..models.core.train import TrainPath, TrainService
from ..models.core.infrastructure import Infrastructure, Direction
from .conflict_checker import ConflictChecker
from ..models.ml.path_success_predictor import PathSuccessPredictor
from ..models.ml.congestion_analyzer import CongestionAnalyzer
import numpy as np


class PathFinder:
    def __init__(self, 
                 infrastructure,
                 success_predictor,
                 congestion_analyzer):
        self.infrastructure = infrastructure
        self.success_predictor = success_predictor
        self.congestion_analyzer = congestion_analyzer
        self.conflict_checker = ConflictChecker()

    def _is_path_crossing(self, new_path: TrainPath, existing_paths: List[TrainPath]) -> bool:
        """Check if the new path crosses any existing paths in the opposite direction"""
        print(f"\nChecking path crossing for train {new_path.train.id}")
        for existing_path in existing_paths:
            if new_path.train.direction != existing_path.train.direction:
                new_times = [t for _, t, _ in new_path.schedule]
                new_sections = [s.split('_')[0] for s, _, _ in new_path.schedule]
                
                existing_times = [t for _, t, _ in existing_path.schedule]
                existing_sections = [s.split('_')[0] for s, _, _ in existing_path.schedule]
                
                print(f"Comparing with {existing_path.train.id}:")
                print(f"New path sections: {new_sections}")
                print(f"Existing path sections: {existing_sections}")
                
                for i in range(len(new_sections) - 1):
                    for j in range(len(existing_sections) - 1):
                        if (new_sections[i] == existing_sections[j]):
                            if (min(new_times[i+1], existing_times[j+1]) > 
                                max(new_times[i], existing_times[j])):
                                print(f"Found crossing at section {new_sections[i]}")
                                return True
        return False

    def _find_time_windows(self, 
                      existing_paths: List[TrainPath], 
                      direction: Direction,
                      target_start_time: datetime) -> List[Tuple[datetime, datetime]]:
        """Find potential start times for new train"""
        # Just return a single window around the target start time
        return [(target_start_time, target_start_time + timedelta(minutes=1))]

    def generate_all_feasible_paths(self, 
                              train: TrainService,
                              start_time: datetime,
                              existing_paths: List[TrainPath],
                              max_paths: int = 50) -> List[TrainPath]:  # Increased max paths
        """Generate feasible paths with varying speeds and dwell times"""
        print(f"\nGenerating feasible paths for train {train.id} - Direction: {train.direction.value}")
        
        feasible_paths = []
        attempts = 0
        max_attempts = 200  # Increased attempts

        direction_suffix = "_UP" if train.direction == Direction.UP else "_DOWN"
        section_order = (["SEC1", "SEC2", "SEC3"] if train.direction == Direction.UP 
                        else ["SEC3", "SEC2", "SEC1"])

        while attempts < max_attempts and len(feasible_paths) < max_paths:
            # Random departure time between 7:20 and 7:25
            minutes_offset = random.uniform(0, 5)
            departure_time = start_time.replace(hour=7, minute=20) + timedelta(minutes=minutes_offset)
            
            schedule = []
            platforms = []
            current_time = departure_time
            
            # Generate random speed factor (0.6 to 1.0 of max speed)
            speed_factor = random.uniform(0.6, 1.0)
            
            # Generate different dwell times for each section
            dwell_times = [
                random.uniform(train.min_dwell_time, train.max_dwell_time * 1.5)
                for _ in range(3)
            ]
            
            print(f"\nAttempt {attempts + 1}")
            print(f"Departure: {departure_time.strftime('%H:%M:%S')}")
            print(f"Speed factor: {speed_factor:.2f}")
            print(f"Dwell times: {[f'{t:.1f}' for t in dwell_times]} minutes")
            
            for idx, section_id in enumerate([f"{sec}{direction_suffix}" for sec in section_order]):
                section = self.infrastructure.sections[section_id]
                
                # Variable speed for each section
                max_speed = min(train.max_speed, section.max_speed)
                actual_speed = max_speed * speed_factor
                running_time = (section.length / actual_speed) * 60
                
                dwell_time = dwell_times[idx] if section.has_platforms else 0.0
                
                schedule.append((section_id, current_time, dwell_time))
                platforms.append(random.choice(section.platforms) if section.has_platforms else "")
                
                current_time += timedelta(minutes=running_time + dwell_time)
                print(f"  {section_id}: {schedule[-1][1].strftime('%H:%M:%S')} -> "
                    f"{current_time.strftime('%H:%M:%S')} "
                    f"(Speed: {actual_speed:.1f} km/h, Dwell: {dwell_time:.1f} min)")
            
            speeds = [min(train.max_speed, self.infrastructure.sections[s].max_speed) * speed_factor 
                    for s, _, _ in schedule]
            
            candidate_path = TrainPath(train, schedule, speeds, platforms)
            
            if (not self._is_path_crossing(candidate_path, existing_paths) and 
                not self.conflict_checker.check_conflicts(candidate_path, existing_paths)):
                journey_time = candidate_path.calculate_journey_time()
                print(f"\nFound valid path!")
                print(f"Total journey time: {journey_time:.1f} minutes")
                print(f"Average speed: {np.mean(speeds):.1f} km/h")
                print(f"Total dwell time: {sum(dwell_times):.1f} minutes")
                feasible_paths.append(candidate_path)
            else:
                print("  Path has conflicts")
            
            attempts += 1
        
        print(f"\nGenerated {len(feasible_paths)} valid paths out of {attempts} attempts")
        
        # Sort paths by journey time
        feasible_paths.sort(key=lambda p: p.calculate_journey_time())
        
        print("\nFeasible paths summary:")
        for i, path in enumerate(feasible_paths, 1):
            journey_time = path.calculate_journey_time()
            total_dwell = sum(dwell for _, _, dwell in path.schedule)
            avg_speed = np.mean([min(train.max_speed, self.infrastructure.sections[s].max_speed) * speed_factor 
                            for s, _, _ in path.schedule])
            print(f"Path {i}:")
            print(f"  Departure: {path.schedule[0][1].strftime('%H:%M:%S')}")
            print(f"  Journey time: {journey_time:.1f} minutes")
            print(f"  Total dwell: {total_dwell:.1f} minutes")
            print(f"  Average speed: {avg_speed:.1f} km/h")
        
        return feasible_paths

    def find_best_path(self, 
                      train: TrainService,
                      start_time: datetime,
                      existing_paths: List[TrainPath]) -> Tuple[TrainPath, List[TrainPath]]:
        """Find best path and return all feasible alternatives"""
        feasible_paths = self.generate_all_feasible_paths(train, start_time, existing_paths)
        
        if not feasible_paths:
            return None, []
        
        # Sort paths by journey time
        sorted_paths = sorted(feasible_paths, key=lambda p: p.calculate_journey_time())
        print("\nFeasible paths found (sorted by journey time):")
        for i, path in enumerate(sorted_paths, 1):
            journey_time = path.calculate_journey_time()
            dwell_time = sum(dwell for _, _, dwell in path.schedule)
            print(f"Path {i}: Journey time = {journey_time:.1f} min, "
                  f"Total dwell = {dwell_time:.1f} min")
        
        return sorted_paths[0], sorted_paths[1:]