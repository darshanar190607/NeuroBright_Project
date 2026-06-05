"""Configuration loader for NeuroBright."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path (str, optional): Path to config file. 
                                     Defaults to config/config.yaml
    
    Returns:
        dict: Configuration dictionary
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is malformed
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_config_value(config: Dict[str, Any], key_path: str, default=None):
    """
    Get nested config value using dot notation.
    
    Args:
        config (dict): Configuration dictionary
        key_path (str): Dot-separated key path (e.g., 'hardware.port')
        default: Default value if key not found
    
    Returns:
        Any: Configuration value
    
    Example:
        >>> config = load_config()
        >>> port = get_config_value(config, 'hardware.port', 'COM3')
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
