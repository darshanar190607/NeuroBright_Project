"""Complete preprocessing pipeline for raw EEG data."""

import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from .filters import notch_filter, bandpass_filter
from .windowing import create_sliding_windows, normalize_windows
from .artifact_rejection import reject_artifacts
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config
from utils.exceptions import PreprocessingError

logger = get_logger(__name__)


class PreprocessingPipeline:
    """Complete preprocessing pipeline from raw CSV to windowed numpy arrays."""
    
    def __init__(self, config):
        """
        Initialize preprocessing pipeline.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.signal_config = config['signal']
        self.window_config = config['windowing']
        self.hw_config = config['hardware']
        
        self.raw_data_dir = Path(config['paths']['raw_data'])
        self.processed_data_dir = Path(config['paths']['processed_data'])
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    def process_file(self, filepath):
        """
        Process one raw CSV file.
        
        Args:
            filepath (Path): Path to raw CSV file
        
        Returns:
            tuple: (windows, labels)
        """
        logger.info(f"Processing {filepath.name}...")
        
        # Load CSV
        df = pd.read_csv(filepath)
        label = df['label'].iloc[0]
        signal = df[['ch1_uv']].values
        
        logger.info(f"  Loaded: {signal.shape}, label={label}")
        
        # Apply filters
        signal = notch_filter(
            signal,
            self.signal_config['notch_freq'],
            self.hw_config['sample_rate'],
            self.signal_config['notch_quality']
        )
        
        signal = bandpass_filter(
            signal,
            self.signal_config['bandpass_low'],
            self.signal_config['bandpass_high'],
            self.hw_config['sample_rate'],
            self.signal_config['filter_order']
        )
        
        logger.info(f"  Filtered: mean={np.mean(np.abs(signal)):.2f} µV")
        
        # Create windows
        windows = create_sliding_windows(
            signal,
            self.window_config['window_samples'],
            self.window_config['step_samples']
        )
        
        # Normalize
        windows = normalize_windows(windows)
        windows = windows.transpose(0, 2, 1)

        
        # Create labels
        labels = np.full(len(windows), label, dtype=np.int64)
        
        logger.info(f"  Windows: {windows.shape}")
        
        return windows, labels
    
    def run(self):
        """Run complete preprocessing pipeline on all raw files."""
        log_pipeline_step("Preprocessing Pipeline")
        
        # Find all raw CSV files
        csv_files = sorted(self.raw_data_dir.glob("*.csv"))
        
        if not csv_files:
            raise PreprocessingError(f"No raw CSV files found in {self.raw_data_dir}")
        
        logger.info(f"Found {len(csv_files)} raw files")
        
        all_windows = []
        all_labels = []
        
        # Process each file
        for filepath in tqdm(csv_files, desc="Processing files"):
            windows, labels = self.process_file(filepath)
            all_windows.append(windows)
            all_labels.append(labels)
        
        # Concatenate all
        X = np.concatenate(all_windows, axis=0)
        y = np.concatenate(all_labels, axis=0)
        
        logger.info(f"\nCombined dataset: {X.shape}")
        
        # Reject artifacts
        X_clean, y_clean, rejection_rate = reject_artifacts(
            X, y,
            self.signal_config['artifact_threshold_uv'],
            self.signal_config['flatline_threshold']
        )
        
        # Print statistics
        logger.info(f"\n{'='*70}")
        logger.info("Dataset Statistics:")
        logger.info(f"  Total windows: {len(X_clean)}")
        logger.info(f"  Window shape: {X_clean.shape[1:]}")
        logger.info(f"  Rejection rate: {rejection_rate*100:.1f}%")
        
        for label_idx, label_name in enumerate(self.config['model']['class_names']):
            count = np.sum(y_clean == label_idx)
            logger.info(f"  {label_name}: {count} windows ({count/len(y_clean)*100:.1f}%)")
        
        logger.info(f"{'='*70}\n")
        
        # Save processed data
        X_path = self.processed_data_dir / 'X_windows.npy'
        y_path = self.processed_data_dir / 'y_labels.npy'
        
        np.save(X_path, X_clean)
        np.save(y_path, y_clean)
        
        logger.info(f"[OK] Saved to:")
        logger.info(f"  {X_path}")
        logger.info(f"  {y_path}")


def main():
    """Main entry point for preprocessing."""
    config = load_config()
    pipeline = PreprocessingPipeline(config)
    pipeline.run()


if __name__ == '__main__':
    main()
