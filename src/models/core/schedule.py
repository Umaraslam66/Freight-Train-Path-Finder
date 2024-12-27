from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

@dataclass
class ScheduleEntry:
    section_id: str
    time: datetime
    dwell_time: float
    platform: str = ""

@dataclass
class Schedule:
    entries: List[ScheduleEntry]
    
    @property
    def total_duration(self) -> float:
        """Calculate total duration including dwell times"""
        if not self.entries:
            return 0.0
        first_time = self.entries[0].time
        last_time = self.entries[-1].time
        last_dwell = self.entries[-1].dwell_time
        duration = (last_time - first_time).total_seconds() / 60 + last_dwell
        return duration