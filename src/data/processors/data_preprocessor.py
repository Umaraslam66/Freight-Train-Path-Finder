from datetime import datetime, timedelta
from typing import List
import random
from ...models.core.train import TrainPath, TrainService, Direction

class TimetableGenerator:
    def generate_dummy_timetable(self, num_trains: int = 10) -> List[TrainPath]:
        """Generate dummy timetable data with alternating directions"""
        paths = []
        base_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        for i in range(num_trains):
            # Alternate between UP and DOWN direction
            direction = Direction.UP if i % 2 == 0 else Direction.DOWN
            
            # Create alternating passenger and freight trains
            train = (TrainService.create_dummy_passenger_train(direction) 
                    if i % 2 == 0 
                    else TrainService.create_dummy_freight_train(direction))
            
            # Select sections based on direction
            direction_suffix = "_UP" if direction == Direction.UP else "_DOWN"
            sections = [f"SEC{j}{direction_suffix}" for j in range(1, 4)]
            
            # Create schedule with 20-minute intervals
            schedule = []
            platforms = []
            current_time = base_time + timedelta(minutes=20*i)
            
            for section in sections:
                # Add random dwell time at stations
                dwell_time = random.uniform(train.min_dwell_time, train.max_dwell_time)
                schedule.append((section, current_time, dwell_time))
                platforms.append(f"P{random.randint(1,2)}")  # Random platform assignment
                current_time += timedelta(minutes=10 + dwell_time)
            
            # Assign speeds based on train type and section
            speeds = [
                min(train.max_speed, 120),  # SEC1
                min(train.max_speed, 100),  # SEC2
                min(train.max_speed, 90)    # SEC3
            ]
            
            paths.append(TrainPath(train, schedule, speeds, platforms))
        
        return paths