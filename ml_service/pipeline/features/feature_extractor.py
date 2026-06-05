"""Combined feature extractor for EEG signals."""

import numpy as np
from .band_powers import compute_relative_band_powers
from .hjorth_params import compute_hjorth_parameters
from .spectral_entropy import compute_spectral_entropy


class FeatureExtractor:
    """Extract all features from EEG windows."""
    
    def __init__(self, config):
        """
        Initialize feature extractor.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.fs = config['hardware']['sample_rate']
        self.bands = config['bands']
    
    def extract(self, window):
        """
        Extract all features from one window.
        
        Args:
            window (np.ndarray): EEG window (n_samples, n_channels)
        
        Returns:
            dict: All extracted features
        """
        features = {}
        
        # Band powers
        band_powers = compute_relative_band_powers(window, self.fs, self.bands)
        for band, powers in band_powers.items():
            features[f'{band}_power'] = powers
        
        # Hjorth parameters
        hjorth = compute_hjorth_parameters(window)
        for param, values in hjorth.items():
            features[f'hjorth_{param}'] = values
        
        # Spectral entropy
        entropy = compute_spectral_entropy(window, self.fs)
        features['spectral_entropy'] = entropy
        
        return features
    
    def extract_to_vector(self, window):
        """
        Extract features as flat vector.
        
        Args:
            window (np.ndarray): EEG window
        
        Returns:
            np.ndarray: Feature vector
        """
        features = self.extract(window)
        
        # Flatten all features
        feature_vector = []
        for key in sorted(features.keys()):
            values = features[key]
            if isinstance(values, np.ndarray):
                feature_vector.extend(values)
            else:
                feature_vector.append(values)
        
        return np.array(feature_vector)


if __name__ == '__main__':
    from utils.config_loader import load_config
    
    config = load_config()
    extractor = FeatureExtractor(config)
    
    # Test with random window
    window = np.random.randn(1000, 3) * 50
    
    features = extractor.extract(window)
    
    print("Extracted features:")
    for key, value in features.items():
        if isinstance(value, np.ndarray):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value:.4f}")
    
    feature_vector = extractor.extract_to_vector(window)
    print(f"\nFeature vector length: {len(feature_vector)}")
