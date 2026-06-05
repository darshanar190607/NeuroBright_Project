"""Setup script for NeuroBright ML service."""

from setuptools import setup, find_packages

setup(
    name="neurobright-ml",
    version="1.0.0",
    description="NeuroBright ML Service - EEG Brain State Classification",
    author="NeuroBright Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.0.0",
        "braindecode==0.7.1",
        "mne>=1.6.0",
        "scipy==1.12.0",
        "numpy==1.26.4",
        "pandas==2.2.0",
        "scikit-learn==1.4.0",
        "optuna==3.5.0",
        "pyserial==3.5",
        "matplotlib==3.8.0",
        "seaborn==0.13.0",
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "websockets==12.0",
        "pyyaml==6.0.1",
        "python-dotenv==1.0.0",
        "tqdm==4.66.0",
    ],
    entry_points={
        'console_scripts': [
            'neurobright=app:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
