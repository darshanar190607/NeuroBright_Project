"""Compute EEG frequency band powers."""

import numpy as np
from scipy.signal import welch


def compute_band_powers(signal, fs, bands):
    """
    Compute power in each frequency band.
    
    Args:
        signal (np.ndarray): EEG signal (n_samples, n_channels)
        fs (float): Sampling rate (Hz)
        bands (dict): Frequency bands {'delta': [1, 4], ...}
    
    Returns:
        dict: Band powers for each channel
              {'delta': [ch1, ch2, ch3], 'theta': [...], ...}
    """
    n_channels = signal.shape[1] if signal.ndim > 1 else 1
    band_powers = {band: [] for band in bands.keys()}
    
    for ch in range(n_channels):
        ch_signal = signal[:, ch] if signal.ndim > 1 else signal
        
        # Compute power spectral density
        freqs, psd = welch(ch_signal, fs=fs, nperseg=min(256, len(ch_signal)))
        
        # Compute power in each band
        for band_name, (low, high) in bands.items():
            idx = np.logical_and(freqs >= low, freqs <= high)
            band_power = np.trapz(psd[idx], freqs[idx])
            band_powers[band_name].append(band_power)
    
    # Convert to numpy arrays
    for band in band_powers:
        band_powers[band] = np.array(band_powers[band])
    
    return band_powers


def compute_relative_band_powers(signal, fs, bands):
    """
    Compute relative band powers (normalized by total power).
    
    Args:
        signal (np.ndarray): EEG signal
        fs (float): Sampling rate
        bands (dict): Frequency bands
    
    Returns:
        dict: Relative band powers
    """
    band_powers = compute_band_powers(signal, fs, bands)
    
    # Compute total power
    total_power = sum(np.sum(powers) for powers in band_powers.values())
    
    # Normalize
    relative_powers = {}
    for band, powers in band_powers.items():
        relative_powers[band] = powers / total_power if total_power > 0 else powers
    
    return relative_powers


if __name__ == '__main__':
    # Test band power computation
    fs = 500
    t = np.linspace(0, 2, 1000)
    
    # Generate test signal with multiple frequencies
    signal = (
        np.sin(2 * np.pi * 3 * t) +    # Delta
        np.sin(2 * np.pi * 6 * t) +    # Theta
        np.sin(2 * np.pi * 10 * t)     # Alpha
    )
    signal = signal.reshape(-1, 1)
    
    bands = {
        'delta': [1, 4],
        'theta': [4, 8],
        'alpha': [8, 12],
        'beta': [13, 30],
        'gamma': [30, 45]
    }
    
    powers = compute_band_powers(signal, fs, bands)
    rel_powers = compute_relative_band_powers(signal, fs, bands)
    
    print("Absolute band powers:")
    for band, power in powers.items():
        print(f"  {band}: {power[0]:.4f}")
    
    print("\nRelative band powers:")
    for band, power in rel_powers.items():
        print(f"  {band}: {power[0]:.4f}")
