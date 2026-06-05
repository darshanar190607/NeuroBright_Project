"""Sliding window creation and normalization."""

import numpy as np
from .filters import normalize_window


def create_sliding_windows(signal, window_size, step_size):
    """
    Create sliding windows from continuous signal.
    
    Args:
        signal (np.ndarray): Input signal (n_samples, n_channels)
        window_size (int): Window size in samples
        step_size (int): Step size in samples
    
    Returns:
        np.ndarray: Windows array (n_windows, window_size, n_channels)
    """
    n_samples, n_channels = signal.shape
    n_windows = (n_samples - window_size) // step_size + 1
    
    windows = np.zeros((n_windows, window_size, n_channels))
    
    for i in range(n_windows):
        start = i * step_size
        end = start + window_size
        windows[i] = signal[start:end]
    
    return windows


def normalize_windows(windows):
    """
    Normalize all windows.
    
    Args:
        windows (np.ndarray): Windows array (n_windows, window_size, n_channels)
    
    Returns:
        np.ndarray: Normalized windows
    """
    normalized = np.zeros_like(windows)
    
    for i in range(len(windows)):
        normalized[i] = normalize_window(windows[i])
    
    return normalized


if __name__ == '__main__':
    # Test windowing
    signal = np.random.randn(5000, 3) * 100  # 10s @ 500Hz, 3 channels
    
    windows = create_sliding_windows(signal, window_size=1000, step_size=250)
    print(f"Signal shape: {signal.shape}")
    print(f"Windows shape: {windows.shape}")
    
    normalized = normalize_windows(windows)
    print(f"Normalized mean: {normalized.mean():.3f}")
    print(f"Normalized std: {normalized.std():.3f}")
