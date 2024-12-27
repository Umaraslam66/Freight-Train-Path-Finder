# setup.py
from setuptools import setup, find_packages

setup(
    name="freight_path_finder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'scikit-learn>=0.24.0',
        'plotly>=5.1.0',
    ],
    author="Umar",
    author_email="umaraslam66@hotmail.com",
    description="A tool for finding optimal freight train paths",
    keywords="railway,optimization,machine learning",
)