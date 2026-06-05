"""Signal filtering and artifact detection functions."""

import numpy as np
from scipy.signal import butter, filtfilt, iirnotch


def notch_filter(signal, freq, fs, quality):
    b, a = iirnotch(freq, quality, fs)
    if signal.ndim == 1:
        return filtfilt(b, a, signal)
    else:
        sig_sq = signal.squeeze()
        if sig_sq.ndim == 1:
            filtered = filtfilt(b, a, sig_sq)
            return filtered.reshape(signal.shape)
        else:
            filtered = np.zeros_like(signal)
            for ch in range(signal.shape[1]):
                filtered[:, ch] = filtfilt(b, a, signal[:, ch])
            return filtered


def bandpass_filter(signal, low, high, fs, order):
    nyquist = fs / 2
    low_norm = low / nyquist
    high_norm = high / nyquist
    b, a = butter(order, [low_norm, high_norm], btype='band')
    if signal.ndim == 1:
        return filtfilt(b, a, signal)
    else:
        sig_sq = signal.squeeze()
        if sig_sq.ndim == 1:
            filtered = filtfilt(b, a, sig_sq)
            return filtered.reshape(signal.shape)
        else:
            filtered = np.zeros_like(signal)
            for ch in range(signal.shape[1]):
                filtered[:, ch] = filtfilt(b, a, signal[:, ch])
            return filtered


def normalize_window(window):
    normalized = np.zeros_like(window)
    for ch in range(window.shape[1]):
        mean = np.mean(window[:, ch])
        std = np.std(window[:, ch])
        if std > 0:
            normalized[:, ch] = (window[:, ch] - mean) / std
        else:
            normalized[:, ch] = window[:, ch] - mean
    return normalized


def is_artifact(window, threshold_uv, flatline_threshold):
    """
    Check if window contains artifacts.
    Handles both (n_samples, n_channels) and (n_channels, n_samples) shapes.
    """
    # Check amplitude threshold on all values
    if np.max(np.abs(window)) > threshold_uv:
        return True

    # Determine shape — after transpose window is (n_channels, n_samples)
    # We check std along the TIME axis (longest dimension)
    if window.shape[0] <= window.shape[1]:
        # Shape is (n_channels, n_samples) — iterate over rows
        for ch in range(window.shape[0]):
            if np.std(window[ch, :]) < flatline_threshold:
                return True
    else:
        # Shape is (n_samples, n_channels) — iterate over columns
        for ch in range(window.shape[1]):
            if np.std(window[:, ch]) < flatline_threshold:
                return True

    return False