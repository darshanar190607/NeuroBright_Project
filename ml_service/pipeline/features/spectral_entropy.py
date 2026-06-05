"""Compute spectral entropy of EEG signals."""

import numpy as np
from scipy.signal import welch
from scipy.stats import entropy


def compute_spectral_entropy(signal, fs, normalize=True):
    """
    Compute spectral entropy (measure of signal randomness).
    
    Higher entropy = more random/complex signal
    Lower entropy = more regular/simple signal
    
    Args:
        signal (np.ndarray): EEG signal (n_samples,) or (n_samples, n_channels)
        fs (float): Sampling rate (Hz)
        normalize (bool): Normalize entropy to [0, 1]
    
    Returns:
        np.ndarray: Spectral entropy for each channel
    """
    if signal.ndim == 1:
        signal = signal.reshape(-1, 1)
    
    n_channels = signal.shape[1]
    entropies = np.zeros(n_channels)
    
    for ch in range(n_channels):
        ch_signal = signal[:, ch]
        
        # Compute power spectral density
        freqs, psd = welch(ch_signal, fs=fs, nperseg=min(256, len(ch_signal)))
        
        # Normalize PSD to probability distribution
        psd_norm = psd / np.sum(psd)
        
        # Compute Shannon entropy
        spec_entropy = entropy(psd_norm)
        
        # Normalize to [0, 1] if requested
        if normalize:
            spec_entropy = spec_entropy / np.log(len(psd_norm))
        
        entropies[ch] = spec_entropy
    
    return entropies


if __name__ == '__main__':
    # Test spectral entropy
    fs = 500
    t = np.linspace(0, 2, 1000)
    
    # Regular signal (low entropy)
    signal1 = np.sin(2 * np.pi * 10 * t).reshape(-1, 1)
    
    # Random signal (high entropy)
    signal2 = np.random.randn(1000, 1)
    
    # Mixed signal (medium entropy)
    signal3 = (
        np.sin(2 * np.pi * 10 * t) +
        0.5 * np.random.randn(len(t))
    ).reshape(-1, 1)
    
    entropy1 = compute_spectral_entropy(signal1, fs)
    entropy2 = compute_spectral_entropy(signal2, fs)
    entropy3 = compute_spectral_entropy(signal3, fs)
    
    print("Spectral Entropy:")
    print(f"  Regular sine: {entropy1[0]:.4f} (low)")
    print(f"  Random noise: {entropy2[0]:.4f} (high)")
    print(f"  Mixed signal: {entropy3[0]:.4f} (medium)")
