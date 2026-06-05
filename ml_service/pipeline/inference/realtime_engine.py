"""Real-time EEG inference engine."""

import torch
import numpy as np
from pathlib import Path
from collections import deque

from pipeline.ingestion.arduino_reader import ArduinoReader
from pipeline.preprocessing.filters import notch_filter, bandpass_filter, normalize_window
from pipeline.features.band_powers import compute_relative_band_powers
from pipeline.training.eegnet import EEGNet
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config
from utils.exceptions import ModelNotFoundError, InferenceError

logger = get_logger(__name__)


class RealtimeEngine:
    """Real-time brain state classification engine."""
    
    def __init__(self, config):
        """
        Initialize inference engine.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.reader = ArduinoReader(config)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model
        model_path = Path(config['paths']['saved_models']) / 'eegnet_best.pth'
        if not model_path.exists():
            raise ModelNotFoundError(f"Model not found: {model_path}")
        
        self.model = EEGNet(
            n_classes=config['model']['n_classes'],
            n_channels=config['model']['n_channels'],
            n_samples=config['model']['n_samples'],
            F1=config['model']['F1'],
            D=config['model']['D'],
            F2=config['model']['F2'],
            dropout=config['model']['dropout']
        ).to(self.device)
        
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        logger.info(f"[OK] Model loaded from {model_path}")
        
        # Prediction smoothing
        self.prediction_history = deque(maxlen=5)
        self.current_state = None
        self.confidence = 0.0
        self.band_powers = {}
    
    def preprocess_window(self, window):
        """
        Preprocess window (same as training pipeline).
        
        Args:
            window (np.ndarray): Raw window (n_samples, n_channels)
        
        Returns:
            torch.Tensor: Preprocessed window
        """
        # Apply filters
        window = notch_filter(
            window,
            self.config['signal']['notch_freq'],
            self.config['hardware']['sample_rate'],
            self.config['signal']['notch_quality']
        )
        
        window = bandpass_filter(
            window,
            self.config['signal']['bandpass_low'],
            self.config['signal']['bandpass_high'],
            self.config['hardware']['sample_rate'],
            self.config['signal']['filter_order']
        )
        
        # Normalize
        window = normalize_window(window)
        
        # Convert to tensor (channels, samples)
        window_tensor = torch.FloatTensor(window).transpose(0, 1).unsqueeze(0)
        
        return window_tensor
    
    def predict_window(self, window):
        """
        Predict brain state for one window.
        
        Args:
            window (np.ndarray): Raw window
        
        Returns:
            tuple: (state_idx, confidence)
        """
        try:
            # Preprocess
            window_tensor = self.preprocess_window(window).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(window_tensor)
                probs = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probs, 1)
            
            state_idx = predicted.item()
            conf = confidence.item()
            
            # Compute band powers for visualization
            self.band_powers = compute_relative_band_powers(
                window,
                self.config['hardware']['sample_rate'],
                self.config['bands']
            )
            
            return state_idx, conf
            
        except Exception as e:
            raise InferenceError(f"Prediction failed: {e}")
    
    def smooth_predictions(self, state_idx):
        """
        Apply majority vote smoothing.
        
        Args:
            state_idx (int): Current prediction
        
        Returns:
            int: Smoothed prediction
        """
        self.prediction_history.append(state_idx)
        
        if len(self.prediction_history) < 3:
            return state_idx
        
        # Majority vote
        counts = np.bincount(list(self.prediction_history), minlength=3)
        return np.argmax(counts)
    
    def get_current_state(self):
        """
        Get current brain state.
        
        Returns:
            dict: State information
        """
        return {
            'state': self.config['model']['class_names'][self.current_state] if self.current_state is not None else 'unknown',
            'state_idx': self.current_state,
            'confidence': self.confidence,
            'band_powers': {k: v.mean() for k, v in self.band_powers.items()} if self.band_powers else {}
        }
    
    def start(self):
        """Start real-time inference loop."""
        log_pipeline_step("Real-Time Inference")
        
        try:
            self.reader.connect()
            
            window_size = self.config['windowing']['window_samples']
            step_size = self.config['windowing']['step_samples']
            
            buffer = []
            
            logger.info("Streaming predictions (Ctrl+C to stop)...\n")
            
            while True:
                # Read packet
                packet = self.reader.read_packet()
                if packet is not None:
                    buffer.append(packet)
                
                # Process when window is full
                if len(buffer) >= window_size:
                    window = np.array(buffer[:window_size])
                    
                    # Predict
                    state_idx, conf = self.predict_window(window)
                    smoothed_state = self.smooth_predictions(state_idx)
                    
                    self.current_state = smoothed_state
                    self.confidence = conf
                    
                    state_name = self.config['model']['class_names'][smoothed_state]
                    logger.info(f"State: {state_name.upper():<10} | Confidence: {conf:.3f}")
                    
                    # Slide window
                    buffer = buffer[step_size:]
        
        except KeyboardInterrupt:
            logger.info("\n[OK] Inference stopped")
        
        finally:
            self.reader.disconnect()


def main():
    """Main entry point for inference."""
    config = load_config()
    engine = RealtimeEngine(config)
    engine.start()


if __name__ == '__main__':
    main()
