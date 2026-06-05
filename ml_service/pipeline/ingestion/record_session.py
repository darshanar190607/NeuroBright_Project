"""Record labeled EEG sessions for all brain states."""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import time
import json
from tqdm import tqdm

from .arduino_reader import ArduinoReader
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config
from utils.exceptions import SignalQualityError

logger = get_logger(__name__)


class SessionRecorder:
    """Records labeled EEG data for training."""
    
    def __init__(self, config):
        """
        Initialize session recorder.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.reader = ArduinoReader(config)
        self.sample_rate = config['hardware']['sample_rate']
        self.channel_names = config['hardware']['channel_names']
        self.states = config['recording']['states']
        self.raw_data_dir = Path(config['paths']['raw_data'])
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    def record_state(self, state_name, state_config):
        """
        Record one brain state.
        
        Args:
            state_name (str): State name (focused/drowsy/stressed)
            state_config (dict): State configuration
        
        Returns:
            tuple: (signal_array, label)
        """
        label = state_config['label']
        duration = state_config['duration']
        instruction = state_config['instruction']
        
        logger.info(f"\n{'='*70}")
        logger.info(f"STATE: {state_name.upper()}")
        logger.info(f"LABEL: {label}")
        logger.info(f"INSTRUCTION: {instruction}")
        logger.info(f"DURATION: {duration}s")
        logger.info(f"{'='*70}\n")
        
        input("Press ENTER when ready to start...")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        print("  GO!\n")
        
        # Record samples
        n_samples = duration * self.sample_rate
        samples = []
        
        with tqdm(total=n_samples, desc=f"Recording {state_name}", unit="samples") as pbar:
            while len(samples) < n_samples:
                packet = self.reader.read_packet()
                if packet is not None:
                    samples.append(packet)
                    pbar.update(1)
        
        signal_array = np.array(samples)
        
        logger.info(f"\n[OK] Recorded {len(signal_array)} samples")
        logger.info(f"  Mean amplitude: {np.mean(np.abs(signal_array)):.2f} µV")
        
        return signal_array, label
    
    def run_full_session(self):
        """Run complete recording session for all states."""
        log_pipeline_step("EEG Data Collection Session")
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            self.reader.connect()
            
            session_data = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'states': []
            }
            
            for state_name, state_config in self.states.items():
                signal_array, label = self.record_state(state_name, state_config)
                
                # Save to CSV
                filename = f"neurobright_raw_{state_name}_{session_id}.csv"
                filepath = self.raw_data_dir / filename
                
                df = pd.DataFrame(signal_array, columns=self.channel_names)
                df['label'] = label
                df.to_csv(filepath, index=False)
                
                logger.info(f"[OK] Saved to {filepath}\n")
                
                session_data['states'].append({
                    'state': state_name,
                    'label': label,
                    'filename': filename,
                    'n_samples': len(signal_array)
                })
                
                # Break between states
                if state_name != list(self.states.keys())[-1]:
                    buffer = self.config['recording']['buffer_seconds']
                    logger.info(f"Take a {buffer}s break...\n")
                    time.sleep(buffer)
            
            # Save metadata
            metadata_file = self.raw_data_dir / f"session_{session_id}.json"
            with open(metadata_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"[OK] Session metadata: {metadata_file}")
            logger.info(f"[OK] Recording session complete!")
            
        finally:
            self.reader.disconnect()


def main():
    """Main entry point for recording."""
    config = load_config()
    recorder = SessionRecorder(config)
    recorder.run_full_session()


if __name__ == '__main__':
    main()
