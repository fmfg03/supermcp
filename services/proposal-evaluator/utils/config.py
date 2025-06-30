"""
Configuration utilities for the proposal evaluator service
"""

import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Return default configuration
        return get_default_config()
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Merge with defaults
    default_config = get_default_config()
    return merge_configs(default_config, config)

def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        "supabase": {
            "url": "https://your-project.supabase.co",
            "service_key": "your-service-key"
        },
        "builder_agent": {
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": "your-api-key",
                "base_url": None
            }
        },
        "judge_agent": {
            "llm": {
                "provider": "openai", 
                "model": "gpt-4",
                "api_key": "your-api-key",
                "base_url": None
            }
        },
        "refiner_agent": {
            "llm": {
                "provider": "openai",
                "model": "gpt-4", 
                "api_key": "your-api-key",
                "base_url": None
            }
        },
        "evaluation": {
            "min_score": 8.0,
            "max_iterations": 5,
            "enable_validation": True
        },
        "telegram": {
            "bot_token": "your-bot-token",
            "allowed_users": []
        }
    }

def merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge user config with default config
    
    Args:
        default: Default configuration
        user: User configuration
        
    Returns:
        Merged configuration
    """
    
    result = default.copy()
    
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, indent=2)