# setup_project.py
import os
import yaml
#pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyyaml

def create_directory_structure():
    # Base directory structure
    directories = [
        'src',
        'src/config',
        'src/data/loaders',
        'src/data/processors',
        'src/models/ml',
        'src/models/core',
        'src/algorithms',
        'src/visualization/static',
        'src/visualization/templates',
        'src/utils',
        'tests/test_data',
        'tests/test_models',
        'tests/test_algorithms',
        'tests/test_visualization',
        'examples',
        'docs'
    ]

    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py in Python package directories
        if directory.startswith('src') or directory.startswith('tests'):
            with open(os.path.join(directory, '__init__.py'), 'w') as f:
                pass

    # Create basic configuration file
    config = {
        'paths': {
            'data_dir': 'data/',
            'output_dir': 'output/',
            'model_dir': 'models/'
        },
        'visualization': {
            'default_width': 1200,
            'default_height': 800,
            'color_scheme': {
                'passenger_trains': '#1f77b4',
                'freight_trains': '#ff7f0e',
                'conflicts': '#d62728'
            }
        },
        'ml_parameters': {
            'prediction_threshold': 0.7,
            'clustering_eps': 0.3,
            'min_samples': 2
        },
        'optimization': {
            'max_iterations': 1000,
            'convergence_threshold': 0.001
        }
    }

    with open('src/config/default_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    # Create requirements.txt
    requirements = """numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=0.24.0
torch>=1.9.0
plotly>=5.1.0
streamlit>=0.84.0
pyyaml>=5.4.1
pytest>=6.2.0"""

    with open('requirements.txt', 'w') as f:
        f.write(requirements)

    # Create basic README
    readme_content = """# Freight Train Path Finder

An AI-enhanced tool for finding optimal freight train paths within existing passenger timetables.

## Setup
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run example: `python examples/simple_path_finding.py`

## Documentation
See `docs/` directory for detailed documentation."""

    with open('README.md', 'w') as f:
        f.write(readme_content)

    # Create .gitignore
    gitignore_content = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.idea/
.vscode/"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)

if __name__ == '__main__':
    create_directory_structure()
    print("Project structure created successfully!")