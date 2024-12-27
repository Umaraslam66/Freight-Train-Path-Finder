from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta
from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"

@dataclass
class TrainService:
    id: str
    train_type: str  # "passenger" or "freight"
    direction: Direction
    max_speed: float
    length: float
    acceleration: float
    deceleration: float
    priority: int
    min_dwell_time: float = 0.0
    max_dwell_time: float = 5.0

    @classmethod
    def create_dummy_passenger_train(cls, direction: Direction) -> 'TrainService':
        return cls(
            id=f"P{direction.value.upper()}101",
            train_type="passenger",
            direction=direction,
            max_speed=160.0,
            length=200.0,
            acceleration=0.8,
            deceleration=0.6,
            priority=1,
            min_dwell_time=1.0,
            max_dwell_time=3.0
        )

    @classmethod
    def create_dummy_freight_train(cls, direction: Direction) -> 'TrainService':
        return cls(
            id=f"F{'UP' if direction == Direction.UP else 'DOWN'}201",
            train_type="freight",
            direction=direction,  # Use the direction as passed
            max_speed=100.0,
            length=500.0,
            acceleration=0.3,
            deceleration=0.2,
            priority=2,
            min_dwell_time=2.0,
            max_dwell_time=5.0
        )

@dataclass
class TrainPath:
    train: TrainService
    schedule: List[tuple[str, datetime, float]]  # section_id, time, dwell_time
    speeds: List[float]
    platforms: List[str]
    
    @property
    def start_time(self) -> datetime:
        return self.schedule[0][1]
    
    @property
    def end_time(self) -> datetime:
        last_time = self.schedule[-1][1]
        last_dwell = self.schedule[-1][2]
        return last_time + timedelta(minutes=last_dwell)