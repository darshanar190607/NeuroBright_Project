#!/usr/bin/env python3
"""
Record DROWSY state EEG data.
Run this when: Late night when genuinely tired, or after heavy lunch.
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
    duration = config['recording']['states']['drowsy']['duration']
    sample_rate = config['hardware']['sample_rate']
    save_path = config['paths']['raw_data']
    
    os.makedirs(save_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_path, f'drowsy_{timestamp}.csv')
    
    print("=" * 60)
    print("  DROWSY STATE RECORDING")
    print("=" * 60)
    print(f"  Duration:    {duration // 60} minutes")
    print(f"  Save to:     {filename}")
    print("=" * 60)
    print()
    print("  INSTRUCTIONS:")
    print("  -> Lie back or sit reclined comfortably")
    print("  -> Eyes half open or closed")
    print("  -> Listen to brown noise or boring lecture")
    print("  -> Let your mind drift — think about nothing")
    print("  -> Best done late night or after a heavy meal")
    print("  -> Do NOT fall fully asleep")
    print()
    print("  Press ENTER when electrodes are on and you are ready...")
    input()
    
    print("  Starting in 5 seconds — relax completely NOW")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("  [RECORDING STARTED]")
    print("  Relax. Let your mind drift. Do not move.")
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
                    writer.writerow([packet[0], 1])
                    samples_collected += 1
                    
                    if samples_collected % (sample_rate * 60) == 0:
                        elapsed = (time.time() - start_time) / 60
                        remaining = (duration / 60) - elapsed
                        print(f"  [{elapsed:.0f} min elapsed] "
                              f"[{remaining:.0f} min remaining] "
                              f"[{samples_collected} samples]")
        
        print()
        print("=" * 60)
        print("  DROWSY RECORDING COMPLETE")
        print(f"  Samples: {samples_collected}")
        print(f"  File:    {filename}")
        print("  You can now disconnect electrodes.")
        print("=" * 60)
        
    finally:
        reader.disconnect()

if __name__ == '__main__':
    main()
