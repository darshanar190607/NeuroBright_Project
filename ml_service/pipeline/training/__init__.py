"""Model training and hyperparameter tuning."""

from .eegnet import EEGNet
from .dataset import EEGDataset

__all__ = ['EEGNet', 'EEGDataset']
