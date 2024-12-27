from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class TrackType(Enum):
    SINGLE = "single"
    DOUBLE = "double"

class Direction(Enum):
    UP = "up"
    DOWN = "down"

@dataclass
class TrackSection:
    id: str
    length: float  # in kilometers
    max_speed: float  # in km/h
    start_point: str
    end_point: str
    track_type: TrackType
    has_passing_loop: bool = False
    signals: List[float] = None  # positions of signals in km from start
    platforms: List[str] = None  # platform identifiers
    min_dwell_time: float = 0.0  # minimum dwell time in minutes
    
    @property
    def has_platforms(self) -> bool:
        return bool(self.platforms)

@dataclass
class Infrastructure:
    sections: Dict[str, TrackSection]
    
    @classmethod
    def create_dummy_infrastructure(cls) -> 'Infrastructure':
        """Create a dummy infrastructure with double tracks"""
        sections = {
            "SEC1_UP": TrackSection(
                "SEC1_UP", 10.0, 120, "A", "B", 
                track_type=TrackType.DOUBLE, has_passing_loop=True,
                signals=[2.5, 7.5], platforms=["A1", "B1"], min_dwell_time=2.0
            ),
            "SEC1_DOWN": TrackSection(
                "SEC1_DOWN", 10.0, 120, "B", "A", 
                track_type=TrackType.DOUBLE, has_passing_loop=True,
                signals=[2.5, 7.5], platforms=["B2", "A2"], min_dwell_time=2.0
            ),
            "SEC2_UP": TrackSection(
                "SEC2_UP", 15.0, 100, "B", "C", 
                track_type=TrackType.DOUBLE, has_passing_loop=False,
                signals=[5.0, 10.0], platforms=["B1", "C1"], min_dwell_time=1.5
            ),
            "SEC2_DOWN": TrackSection(
                "SEC2_DOWN", 15.0, 100, "C", "B", 
                track_type=TrackType.DOUBLE, has_passing_loop=False,
                signals=[5.0, 10.0], platforms=["C2", "B2"], min_dwell_time=1.5
            ),
            "SEC3_UP": TrackSection(
                "SEC3_UP", 12.0, 90, "C", "C",  # Changed end point from D to C
                track_type=TrackType.DOUBLE, has_passing_loop=True,
                signals=[3.0, 9.0], platforms=["C1"], min_dwell_time=2.0
            ),
            "SEC3_DOWN": TrackSection(
                "SEC3_DOWN", 12.0, 90, "C", "C",  # Changed end point from D to C
                track_type=TrackType.DOUBLE, has_passing_loop=True,
                signals=[3.0, 9.0], platforms=["C2"], min_dwell_time=2.0
            )
        }
        return cls(sections)