"""Color-coded logging utility for NeuroBright pipeline."""

import logging
import sys
from pathlib import Path
from datetime import datetime

# ANSI color codes
COLORS = {
    'INFO': '\033[92m',      # Green
    'WARNING': '\033[93m',   # Yellow
    'ERROR': '\033[91m',     # Red
    'DEBUG': '\033[94m',     # Blue
    'RESET': '\033[0m'
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding."""
    
    def format(self, record):
        color = COLORS.get(record.levelname, COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{COLORS['RESET']}"
        return super().format(record)


def get_logger(name):
    """
    Get a color-coded logger instance.
    
    Args:
        name (str): Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(levelname)s | %(name)s | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler without colors
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / 'neurobright.log')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def log_pipeline_step(step_name):
    """
    Print a clear separator for pipeline steps.
    
    Args:
        step_name (str): Name of the pipeline step
    """
    separator = "=" * 70
    print(f"\n{COLORS['INFO']}{separator}")
    print(f"  {step_name.upper()}")
    print(f"{separator}{COLORS['RESET']}\n")
