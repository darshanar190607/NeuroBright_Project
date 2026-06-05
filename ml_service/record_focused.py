#!/usr/bin/env python3
"""
Record FOCUSED state EEG data.
Run this when: Morning, fresh mind, doing hard LeetCode/CodeChef.
Duration: 20 minutes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import csv
import numpy as np
from datetime import datetime
from utils.config_loader import load_config
from utils.logger import get_logger
from pipeline.ingestion.arduino_reader import ArduinoReader

logger = get_logger(__name__)

def main():
    config = load_config()
    duration = config['recording']['states']['focused']['duration']
    sample_rate = config['hardware']['sample_rate']
    save_path = config['paths']['raw_data']
    
    os.makedirs(save_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_path, f'focused_{timestamp}.csv')
    
    print("=" * 60)
    print("  FOCUSED STATE RECORDING")
    print("=" * 60)
    print(f"  Duration:    {duration // 60} minutes")
    print(f"  Save to:     {filename}")
    print("=" * 60)
    print()
    print("  INSTRUCTIONS:")
    print("  -> Open a hard LeetCode or CodeChef problem")
    print("  -> Solve it with full concentration")
    print("  -> Sit physically still — no jaw clenching")
    print("  -> No head nodding or movement")
    print()
    print("  Press ENTER when electrodes are on and you are ready...")
    input()
    
    print("  Starting in 5 seconds — begin solving your problem NOW")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("  [RECORDING STARTED]")
    print("  Stay focused and keep solving. Do not move.")
    print()
    
    reader = ArduinoReader(config)
    
    try:
        reader.connect()
        
        total_samples = duration * sample_rate
        samples_collected = 0
        start_time = time.time()
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ch1_uv', 'label'])
            
            while samples_collected < total_samples:
                packet = reader.read_packet()
                if packet is not None:
                    writer.writerow([packet[0], 0])
                    samples_collected += 1
                    
                    # Progress every 60 seconds
                    if samples_collected % (sample_rate * 60) == 0:
                        elapsed = (time.time() - start_time) / 60
                        remaining = (duration / 60) - elapsed
                        print(f"  [{elapsed:.0f} min elapsed] "
                              f"[{remaining:.0f} min remaining] "
                              f"[{samples_collected} samples]")
        
        print()
        print("=" * 60)
        print("  FOCUSED RECORDING COMPLETE")
        print(f"  Samples: {samples_collected}")
        print(f"  File:    {filename}")
        print("  You can now disconnect electrodes.")
        print("=" * 60)
        
    finally:
        reader.disconnect()

if __name__ == '__main__':
    main()
