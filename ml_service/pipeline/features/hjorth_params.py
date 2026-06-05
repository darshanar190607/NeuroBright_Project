"""Compute Hjorth parameters for EEG signals."""

import numpy as np


def compute_hjorth_parameters(signal):
    """
    Compute Hjorth parameters: Activity, Mobility, Complexity.
    
    Activity: Variance of the signal
    Mobility: Square root of variance of first derivative / variance of signal
    Complexity: Mobility of first derivative / mobility of signal
    
    Args:
        signal (np.ndarray): EEG signal (n_samples,) or (n_samples, n_channels)
    
    Returns:
        dict: {'activity': array, 'mobility': array, 'complexity': array}
    """
    if signal.ndim == 1:
        signal = signal.reshape(-1, 1)
    
    n_channels = signal.shape[1]
    
    activity = np.zeros(n_channels)
    mobility = np.zeros(n_channels)
    complexity = np.zeros(n_channels)
    
    for ch in range(n_channels):
        ch_signal = signal[:, ch]
        
        # First derivative
        first_deriv = np.diff(ch_signal)
        
        # Second derivative
        second_deriv = np.diff(first_deriv)
        
        # Activity (variance)
        activity[ch] = np.var(ch_signal)
        
        # Mobility
        if activity[ch] > 0:
            mobility[ch] = np.sqrt(np.var(first_deriv) / activity[ch])
        
        # Complexity
        if mobility[ch] > 0:
            mobility_deriv = np.sqrt(np.var(second_deriv) / np.var(first_deriv))
            complexity[ch] = mobility_deriv / mobility[ch]
    
    return {
        'activity': activity,
        'mobility': mobility,
        'complexity': complexity
    }


if __name__ == '__main__':
    # Test Hjorth parameters
    t = np.linspace(0, 2, 1000)
    
    # Simple sine wave
    signal1 = np.sin(2 * np.pi * 10 * t).reshape(-1, 1)
    
    # Complex signal
    signal2 = (
        np.sin(2 * np.pi * 5 * t) +
        0.5 * np.sin(2 * np.pi * 15 * t) +
        0.3 * np.random.randn(len(t))
    ).reshape(-1, 1)
    
    params1 = compute_hjorth_parameters(signal1)
    params2 = compute_hjorth_parameters(signal2)
    
    print("Simple sine wave:")
    print(f"  Activity: {params1['activity'][0]:.4f}")
    print(f"  Mobility: {params1['mobility'][0]:.4f}")
    print(f"  Complexity: {params1['complexity'][0]:.4f}")
    
    print("\nComplex signal:")
    print(f"  Activity: {params2['activity'][0]:.4f}")
    print(f"  Mobility: {params2['mobility'][0]:.4f}")
    print(f"  Complexity: {params2['complexity'][0]:.4f}")
