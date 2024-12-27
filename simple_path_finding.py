from datetime import datetime, timedelta
import numpy as np
from src.models.core.infrastructure import Infrastructure
from src.models.core.train import TrainService, TrainPath, Direction
from src.data.processors.data_preprocessor import TimetableGenerator
from src.models.ml.path_success_predictor import PathSuccessPredictor
from src.models.ml.congestion_analyzer import CongestionAnalyzer
from src.algorithms.path_finder import PathFinder
from src.visualization.time_space_diagram import TimeSpaceDiagram

def main():
    print("Starting path finding process...")
    
    # Create infrastructure
    infrastructure = Infrastructure.create_dummy_infrastructure()
    print("\nInfrastructure created with sections:", list(infrastructure.sections.keys()))
    
    # Generate dummy timetable
    timetable_gen = TimetableGenerator()
    existing_paths = timetable_gen.generate_dummy_timetable(num_trains=10)
    print(f"\nGenerated {len(existing_paths)} existing train paths")
    
    # Initialize ML models
    print("\nInitializing ML models...")
    success_predictor = PathSuccessPredictor()
    
    # Create balanced training data
    training_paths = existing_paths.copy()
    
    # Add some "unsuccessful" variations
    for path in existing_paths[:5]:
        print(f"\nCreating unsuccessful variation for train {path.train.id}")
        modified_schedule = [
            (s, t + timedelta(minutes=np.random.randint(1, 30)), d) 
            for s, t, d in path.schedule
        ]
        modified_path = TrainPath(
            train=path.train,
            schedule=modified_schedule,
            speeds=[s * 0.8 for s in path.speeds],
            platforms=path.platforms
        )
        training_paths.append(modified_path)
    
    # Create balanced labels
    success_labels = [True] * len(existing_paths) + [False] * 5
    
    # Train the success predictor
    print(f"\nTraining success predictor with {len(training_paths)} paths")
    success_predictor.train(training_paths, success_labels)
    
    congestion_analyzer = CongestionAnalyzer()
    print("\nInitialized congestion analyzer")
    
    # Initialize path finder
    path_finder = PathFinder(infrastructure, success_predictor, congestion_analyzer)

    # Create a new freight train (DOWN direction to match other freight trains)
    freight_train = TrainService.create_dummy_freight_train(Direction.DOWN)
    print(f"\nCreated new freight train {freight_train.id}")  # Should now be FDOWN201
    
    # Find best path
    start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    print(f"\nFinding best path starting at {start_time.strftime('%H:%M')}")
    best_path = path_finder.find_best_path(freight_train, start_time, existing_paths)
    
    if best_path:
        print("\nFound optimal path for freight train:")
        for section, time, dwell in best_path.schedule:
            print(f"Section {section}: {time.strftime('%H:%M')} (Dwell: {dwell:.1f} min)")
        
        # Visualize result
        viz = TimeSpaceDiagram(infrastructure.sections)
        fig = viz.create_diagram(existing_paths, best_path)
        fig.show()
    else:
        print("\nNo feasible path found.")

if __name__ == "__main__":
    main()