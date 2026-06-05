"""Artifact detection and rejection."""

import numpy as np
from .filters import is_artifact
from utils.logger import get_logger

logger = get_logger(__name__)


def reject_artifacts(windows, labels, threshold_uv, flatline_threshold):
    """
    Remove windows containing artifacts.
    
    Args:
        windows (np.ndarray): Windows array (n_windows, window_size, n_channels)
        labels (np.ndarray): Labels array (n_windows,)
        threshold_uv (float): Amplitude threshold
        flatline_threshold (float): Flatline threshold
    
    Returns:
        tuple: (clean_windows, clean_labels, rejection_rate)
    """
    clean_indices = []
    
    for i in range(len(windows)):
        if not is_artifact(windows[i], threshold_uv, flatline_threshold):
            clean_indices.append(i)
    
    clean_windows = windows[clean_indices]
    clean_labels = labels[clean_indices]
    
    rejection_rate = 1 - (len(clean_indices) / len(windows))
    
    logger.info(f"Artifact rejection: {len(windows)} -> {len(clean_windows)} windows")
    logger.info(f"Rejection rate: {rejection_rate*100:.1f}%")
    
    return clean_windows, clean_labels, rejection_rate


if __name__ == '__main__':
    # Test artifact rejection
    windows = np.random.randn(100, 1000, 3) * 50
    labels = np.random.randint(0, 3, 100)
    
    # Add some artifacts
    windows[10] = 200  # High amplitude
    windows[20] = 0.1  # Flatline
    
    clean_windows, clean_labels, rate = reject_artifacts(
        windows, labels, threshold_uv=150, flatline_threshold=0.5
    )
    
    print(f"Original: {len(windows)} windows")
    print(f"Clean: {len(clean_windows)} windows")
    print(f"Rejection rate: {rate*100:.1f}%")
