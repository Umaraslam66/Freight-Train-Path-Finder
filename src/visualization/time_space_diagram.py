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
        """Convert datetime to minutes since base_time"""
        return (time - base_time).total_seconds() / 60

    def create_diagram(self, existing_paths: List[TrainPath], optimal_path: TrainPath = None) -> go.Figure:
        print("\nCreating Time-Space Diagram:")
        fig = go.Figure()
        
        # Collect and sort all paths
        all_paths = existing_paths.copy()
        if optimal_path:
            all_paths.append(optimal_path)
        all_paths.sort(key=lambda p: p.schedule[0][1])
        
        # Find time range
        all_times = []
        for path in all_paths:
            for _, time, dwell in path.schedule:
                all_times.append(time)
                if dwell > 0:
                    all_times.append(time + timedelta(minutes=dwell))
        
        min_time = min(all_times)
        max_time = max(all_times)
        
        # Plot each path
        for path in all_paths:
            is_up = path.train.direction == Direction.UP
            station_sequence = self.stations if is_up else list(reversed(self.stations))
            
            print(f"\nPlotting {path.train.id} ({path.train.direction.value}):")
            print(f"Station sequence: {station_sequence}")
            
            # Create points for plotting
            x_times = []  # Numeric times for plotting
            y_positions = []
            hover_texts = []
            
            for (section_id, time, dwell), station in zip(path.schedule, station_sequence):
                # Add arrival point
                numeric_time = self._convert_to_numeric_time(time, min_time)
                station_pos = self.stations.index(station) * 10
                
                print(f"  {station} at {time.strftime('%H:%M')} -> pos {station_pos}")
                
                x_times.append(numeric_time)
                y_positions.append(station_pos)
                hover_texts.append(
                    f'Train: {path.train.id}<br>'
                    f'Station: {station}<br>'
                    f'Direction: {path.train.direction.value}<br>'
                    f'Arrival: {time.strftime("%H:%M")}<br>'
                    f'Dwell: {dwell:.1f} min'
                )
                
                # Add dwell point if applicable
                if dwell > 0:
                    departure_time = time + timedelta(minutes=dwell)
                    x_times.append(self._convert_to_numeric_time(departure_time, min_time))
                    y_positions.append(station_pos)
                    hover_texts.append(
                        f'Train: {path.train.id}<br>'
                        f'Station: {station}<br>'
                        f'Direction: {path.train.direction.value}<br>'
                        f'Departure: {departure_time.strftime("%H:%M")}'
                    )
            
            # Add path to plot
            color = 'red' if path == optimal_path else ('blue' if path.train.train_type == 'passenger' else 'orange')
            
            fig.add_trace(go.Scatter(
                x=x_times,
                y=y_positions,
                mode='lines+markers',
                name=f'{path.train.id} ({path.train.direction.value})',
                line=dict(
                    color=color,
                    width=3 if path == optimal_path else 2,
                    dash='solid' if path.train.train_type == 'passenger' else 'dot'
                ),
                marker=dict(size=8),
                hovertemplate='%{text}',
                text=hover_texts
            ))
        
        # Create time axis ticks
        time_ticks = []
        time_labels = []
        current_time = min_time
        while current_time <= max_time:
            time_ticks.append(self._convert_to_numeric_time(current_time, min_time))
            time_labels.append(current_time.strftime('%H:%M'))
            current_time += timedelta(minutes=10)
        
        # Update layout
        fig.update_layout(
            title='Time-Space Diagram',
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
            width=1200,
            height=600,
            plot_bgcolor='white'
        )
        
        return fig