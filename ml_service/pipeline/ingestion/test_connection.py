"""Test Arduino hardware connection."""

from .arduino_reader import ArduinoReader
from utils.logger import get_logger, log_pipeline_step
from utils.config_loader import load_config

logger = get_logger(__name__)


def test_hardware():
    """Test Arduino connection and read sample data."""
    log_pipeline_step("Hardware Connection Test")
    
    config = load_config()
    reader = ArduinoReader(config)
    
    try:
        reader.connect()
        reader.test_connection()
        
        logger.info("\n [ok] Hardware test passed!")
        logger.info("  Ready for data collection")
        
        return True
        
    except Exception as e:
        logger.error(f"[no] Hardware test failed: {e}")
        return False
        
    finally:
        reader.disconnect()


if __name__ == '__main__':
    test_hardware()
