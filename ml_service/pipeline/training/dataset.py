"""PyTorch Dataset for EEG windows."""

import torch
from torch.utils.data import Dataset
import numpy as np


class EEGDataset(Dataset):
    """PyTorch Dataset for EEG windows."""
    
    def __init__(self, X, y, transform=None):
        """
        Initialize dataset.
        
        Args:
            X (np.ndarray): Windows array (n_windows, n_samples, n_channels)
            y (np.ndarray): Labels array (n_windows,)
            transform (callable, optional): Optional transform
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        self.transform = transform
    
    def __len__(self):
        """Return dataset size."""
        return len(self.X)
    
    def __getitem__(self, idx):
       window = self.X[idx]
       label = self.y[idx]
    
       if self.transform:
          window = self.transform(window)
    
    # Shape is already (n_channels, n_samples) — no transpose needed
       return window, label


if __name__ == '__main__':
    # Test dataset
    X = np.random.randn(100, 1000, 3)
    y = np.random.randint(0, 3, 100)
    
    dataset = EEGDataset(X, y)
    
    print(f"Dataset size: {len(dataset)}")
    
    window, label = dataset[0]
    print(f"Window shape: {window.shape}")  # Should be (3, 1000)
    print(f"Label: {label}")
