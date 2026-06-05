#!/usr/bin/env python3
"""
Record STRESSED state EEG data.
Run this when: Under genuine time pressure or frustration.
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
    duration = config['recording']['states']['stressed']['duration']
    sample_rate = config['hardware']['sample_rate']
    save_path = config['paths']['raw_data']
    
    os.makedirs(save_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(save_path, f'stressed_{timestamp}.csv')
    
    print("=" * 60)
    print("  STRESSED STATE RECORDING")
    print("=" * 60)
    print(f"  Duration:    {duration // 60} minutes")
    print(f"  Save to:     {filename}")
    print("=" * 60)
    print()
    print("  INSTRUCTIONS:")
    print("  -> Open typeracer.com OR a timed Stroop task")
    print("  -> Set a 30-second alarm that buzzes when too slow")
    print("  -> Play a fast-paced frustrating game")
    print("  -> Feel genuine urgency and pressure to perform")
    print("  -> Sit still physically — only mental stress needed")
    print()
    print("  Press ENTER when electrodes are on and you are ready...")
    input()
    
    print("  Starting in 5 seconds — begin your stressful task NOW")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("  [RECORDING STARTED]")
    print("  Stay under pressure. Keep performing. Do not relax.")
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
                    writer.writerow([packet[0], 2])
                    samples_collected += 1
                    
                    if samples_collected % (sample_rate * 60) == 0:
                        elapsed = (time.time() - start_time) / 60
                        remaining = (duration / 60) - elapsed
                        print(f"  [{elapsed:.0f} min elapsed] "
                              f"[{remaining:.0f} min remaining] "
                              f"[{samples_collected} samples]")
        
        print()
        print("=" * 60)
        print("  STRESSED RECORDING COMPLETE")
        print(f"  Samples: {samples_collected}")
        print(f"  File:    {filename}")
        print("  You can now disconnect electrodes.")
        print("=" * 60)
        
    finally:
        reader.disconnect()

if __name__ == '__main__':
    main()
