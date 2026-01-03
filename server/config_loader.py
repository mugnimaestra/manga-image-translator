"""
Config loader for server default configuration.

This module handles loading default configuration from a JSON file and 
merging it with per-request configurations.
"""
import json
from typing import Optional
from manga_translator import Config

# Global default config, loaded from --default-config file
_default_config: Optional[dict] = None


def load_default_config(config_path: str) -> None:
    """
    Load default configuration from a JSON file.
    
    Args:
        config_path: Path to the JSON configuration file
    """
    global _default_config
    
    if not config_path:
        _default_config = None
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        _default_config = json.load(f)
    
    print(f"[Config] Loaded default config from: {config_path}")


def get_default_config() -> Optional[dict]:
    """Get the loaded default configuration dictionary."""
    return _default_config


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries. Values from 'override' take precedence.
    
    This handles nested dictionaries by recursively merging them,
    rather than simply replacing the entire nested dict.
    
    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge(result[key], value)
        else:
            # Override the value
            result[key] = value
    
    return result


def merge_with_default(request_config: Config) -> Config:
    """
    Merge request config with default config.
    
    Request config values take precedence over default config values.
    Only EXPLICITLY SET values in the request config will override the defaults.
    
    Args:
        request_config: Configuration from the translation request
    
    Returns:
        Merged Config object
    """
    if _default_config is None:
        return request_config
    
    # Use exclude_unset=True to get ONLY the fields that were explicitly set
    # in the request. This way, default config values are preserved unless
    # the request explicitly overrides them.
    request_dict = request_config.model_dump(exclude_unset=True)
    
    # Deep merge: default_config as base, request_config (only explicitly set) as override
    merged_dict = deep_merge(_default_config, request_dict)
    
    print(f"[Config] Merged config - default fields: {list(_default_config.keys())}, request overrides: {list(request_dict.keys())}")
    
    # Create a new Config from merged dict
    return Config.model_validate(merged_dict)
