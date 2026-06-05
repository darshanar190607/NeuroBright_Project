"""Arduino EEG reader with binary packet protocol."""

import serial
import numpy as np
import time
import struct
from utils.logger import get_logger
from utils.exceptions import HardwareConnectionError, SignalQualityError

logger = get_logger(__name__)

# Packet protocol constants
SYNC1 = 0xC7
SYNC2 = 0x7C
END_BYTE = 0x01
PACKET_LENGTH = 16


class ArduinoReader:
    """Reads 3-channel EEG data from Arduino via binary packets."""
    
    def __init__(self, config):
        """
        Initialize Arduino reader.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.hw_config = config['hardware']
        self.port = self.hw_config['port']
        self.baud_rate = self.hw_config['baud_rate']
        self.n_channels = self.hw_config['n_channels']
        self.adc_resolution = self.hw_config['adc_resolution']
        self.vref = self.hw_config['adc_reference_voltage']
        self.serial_conn = None
        
        logger.info(f"Initialized ArduinoReader for {self.port} @ {self.baud_rate} baud")
    
    def connect(self):
        """
        Establish serial connection and verify Arduino.
        
        Raises:
            HardwareConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to {self.port}...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=2
            )
            time.sleep(2)  # Arduino reset delay
            
            # Verify device
            self.serial_conn.write(b'WHORU\n')
            time.sleep(0.1)
            response = self.serial_conn.readline().decode('utf-8').strip()
            
            if 'UNO-R4' not in response:
                raise HardwareConnectionError(f"Unexpected device: {response}")
            
            # Start streaming
            self.serial_conn.write(b'START\n')
            time.sleep(0.1)
            
            logger.info(f" [ok] Connected to {response}")
            
        except serial.SerialException as e:
            raise HardwareConnectionError(f"Serial connection failed: {e}")
    
    def disconnect(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(b'STOP\n')
            time.sleep(0.1)
            self.serial_conn.close()
            logger.info("Disconnected from Arduino")
    
    def adc_to_microvolts(self, raw_value):
        max_adc = (1 << self.adc_resolution) - 1
        microvolts = ((raw_value / max_adc) - 0.5) * self.vref * 1e6 / 1000
        return microvolts
    
    def read_packet(self):
        """
        Read one 16-byte binary packet from Arduino.
        
        Packet format:
            [SYNC1][SYNC2][CH1_H][CH1_L][CH2_H][CH2_L][CH3_H][CH3_L]
            [TIMESTAMP_4B][CHECKSUM][END]
        
        Returns:
            np.ndarray: [ch1_uv, ch2_uv, ch3_uv] or None if invalid
        """
        try:
            # Find sync bytes
            while True:
                byte = self.serial_conn.read(1)
                if not byte:
                    return None
                if byte[0] == SYNC1:
                    byte2 = self.serial_conn.read(1)
                    if byte2 and byte2[0] == SYNC2:
                        break
            
            # Read remaining 14 bytes
            data = self.serial_conn.read(14)
            if len(data) != 14:
                return None
            
            # Verify end byte
            if data[-1] != END_BYTE:
                logger.debug("Invalid end byte")
                return None
            
            # Single channel only — BioAmp EXG Pill outputs 1 EEG channel on A0
            # data[0] = packet counter, data[1:3] = CH0 (A0 = Fp1)
            ch0_raw = struct.unpack('>H', data[1:3])[0]
            return np.array([self.adc_to_microvolts(ch0_raw)])
            
        except Exception as e:
            logger.debug(f"Packet read error: {e}")
            return None
    
    def read_n_samples(self, n):
        """
        Read exactly n samples from Arduino.
        
        Args:
            n (int): Number of samples to collect
        
        Returns:
            np.ndarray: Shape (n, 1) in microvolts
        
        Raises:
            SignalQualityError: If too many failed reads
        """
        samples = []
        failed_reads = 0
        max_failures = n // 10  # Allow 10% failure rate
        
        while len(samples) < n:
            packet = self.read_packet()
            if packet is not None:
                samples.append(packet)
                failed_reads = 0
            else:
                failed_reads += 1
                if failed_reads > max_failures:
                    raise SignalQualityError(
                        f"Too many failed reads: {failed_reads}/{len(samples)}"
                    )
        
        return np.array(samples)
    
    def test_connection(self):
        logger.info("Testing connection — reading 500 samples (1 second)...")
        samples = []
        for i in range(500):
            packet = self.read_packet()
            if packet is not None:
                samples.append(packet)
        
        if len(samples) == 0:
            logger.error("No samples received — check Arduino connection")
            return False
        
        arr = np.array(samples)
        std = np.std(arr[:, 0])
        mean = np.mean(arr[:, 0])
        
        logger.info(f"Samples received: {len(samples)}/500")
        logger.info(f"CH1 (Fp1) mean: {mean:.2f} uV")
        logger.info(f"CH1 (Fp1) std:  {std:.2f} uV")
        
        if std < 5.0:
            logger.warning("Signal std below 5uV — electrode contact is poor")
            logger.warning("Re-seat electrode firmly on forehead and test again")
            return False
        elif std < 10.0:
            logger.warning("Signal std between 5-10uV — contact is weak, acceptable for now")
        else:
            logger.info("Signal quality GOOD — std above 10uV, ready to record")
        
        return True


if __name__ == '__main__':
    from utils.config_loader import load_config
    
    config = load_config()
    reader = ArduinoReader(config)
    
    try:
        reader.connect()
        reader.test_connection()
        
        print("\nReading 5 seconds of data...")
        data = reader.read_n_samples(2500)  # 5s x 500Hz
        print(f" [ok] Shape: {data.shape}")
        print(f" [ok] Mean: {np.mean(data, axis=0)} µV")
        
    finally:
        reader.disconnect()
