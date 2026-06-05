"""Setup script for NeuroBright package."""

from setuptools import setup, find_packages

setup(
    name="neurobright",
    version="0.1.0",
    description="Neuroadaptive learning platform with real-time EEG brain state classification",
    author="NeuroBright Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.0.0",
        "braindecode==0.8.0",
        "mne==1.6.0",
        "scipy==1.12.0",
        "numpy==1.26.4",
        "pandas==2.2.0",
        "scikit-learn==1.4.0",
        "optuna==3.5.0",
        "pyserial==3.5",
        "matplotlib==3.8.0",
        "seaborn==0.13.0",
        "pyyaml==6.0.1",
        "python-dotenv==1.0.0",
        "tqdm==4.66.0",
        "joblib==1.3.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.9",
    ],
)
