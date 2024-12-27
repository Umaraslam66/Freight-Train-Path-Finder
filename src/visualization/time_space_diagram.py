import plotly.graph_objects as go
from typing import List
from ..models.core.train import TrainPath, Direction
from datetime import datetime, timedelta
import numpy as np

class TimeSpaceDiagram:
    def __init__(self, infrastructure_sections: dict):
        self.stations = ['A', 'B', 'C']
        print(f"Stations: {self.stations}")

    def _convert_to_numeric_time(self, time: datetime, base_time: datetime) -> float:
        return (time - base_time).total_seconds() / 60

    def create_diagram(self, existing_paths: List[TrainPath], optimal_path: TrainPath = None, 
                      alternative_paths: List[TrainPath] = None) -> go.Figure:
        print("\nCreating Time-Space Diagram:")
        fig = go.Figure()
        
        # Collect all paths
        all_paths = existing_paths.copy()
        if alternative_paths:
            all_paths.extend(alternative_paths)
        if optimal_path:
            all_paths.append(optimal_path)
            
        all_paths.sort(key=lambda p: p.schedule[0][1])
        
        # Time range calculation
        all_times = [time for path in all_paths 
                    for _, time, dwell in path.schedule 
                    for t in [time, time + timedelta(minutes=dwell) if dwell > 0 else time]]
        min_time = min(all_times)
        max_time = max(all_times)
        
        # Plot paths
        for path in all_paths:
            is_up = path.train.direction == Direction.UP
            station_sequence = self.stations if is_up else list(reversed(self.stations))
            
            # Prepare plotting data
            x_times, y_positions, hover_texts = [], [], []
            journey_time = (path.schedule[-1][1] - path.schedule[0][1]).total_seconds() / 60
            total_dwell = sum(dwell for _, _, dwell in path.schedule)
            
            for (section_id, time, dwell), station in zip(path.schedule, station_sequence):
                numeric_time = self._convert_to_numeric_time(time, min_time)
                station_pos = self.stations.index(station) * 10
                
                # Add arrival point
                x_times.append(numeric_time)
                y_positions.append(station_pos)
                hover_texts.append(
                    f'Train: {path.train.id}<br>'
                    f'Station: {station}<br>'
                    f'Direction: {path.train.direction.value}<br>'
                    f'Arrival: {time.strftime("%H:%M")}<br>'
                    f'Journey Time: {journey_time:.1f} min<br>'
                    f'Total Dwell: {total_dwell:.1f} min'
                )
                
                # Add dwell point
                if dwell > 0:
                    departure_time = time + timedelta(minutes=dwell)
                    x_times.append(self._convert_to_numeric_time(departure_time, min_time))
                    y_positions.append(station_pos)
                    hover_texts.append(
                        f'Train: {path.train.id}<br>'
                        f'Station: {station}<br>'
                        f'Dwell: {dwell:.1f} min<br>'
                        f'Departure: {departure_time.strftime("%H:%M")}'
                    )
            
            # Set path style
            if path == optimal_path:
                color, width, dash = 'red', 3, 'solid'
                name = f'{path.train.id} (OPTIMAL - {journey_time:.1f}min)'
            elif path in (alternative_paths or []):
                color, width, dash = 'green', 2, 'dash'
                name = f'{path.train.id} (Alternative - {journey_time:.1f}min)'
            else:
                color = 'blue' if path.train.train_type == 'passenger' else 'orange'
                width, dash = 2, 'solid' if path.train.train_type == 'passenger' else 'dot'
                name = f'{path.train.id} ({path.train.direction.value})'
            
            fig.add_trace(go.Scatter(
                x=x_times,
                y=y_positions,
                mode='lines+markers',
                name=name,
                line=dict(color=color, width=width, dash=dash),
                marker=dict(size=8),
                hovertemplate='%{text}',
                text=hover_texts
            ))
        
        # Time axis setup
        time_ticks, time_labels = [], []
        current_time = min_time
        while current_time <= max_time:
            time_ticks.append(self._convert_to_numeric_time(current_time, min_time))
            time_labels.append(current_time.strftime('%H:%M'))
            current_time += timedelta(minutes=10)
        
        # Layout
        fig.update_layout(
            title='Time-Space Diagram with Alternative Paths',
            xaxis=dict(
                title='Time',
                tickmode='array',
                ticktext=time_labels,
                tickvals=time_ticks,
                gridwidth=1,
                gridcolor='LightGrey',
            ),
            yaxis=dict(
                title='Stations',
                ticktext=self.stations,
                tickvals=[i * 10 for i in range(len(self.stations))],
                gridwidth=1,
                gridcolor='LightGrey',
            ),
            showlegend=True,
            width=2400,
            height=1200,
            plot_bgcolor='white'
        )
        
        return fig