"""Configuration utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_model_config(config: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """
    Get configuration for specific model.
    
    Args:
        config: Full configuration dict
        model_name: Name or alias of model
        
    Returns:
        Model configuration
    """
    models = config.get('models', {}).get('ollama', {}).get('models', [])
    
    for model in models:
        if model['name'] == model_name or model.get('alias') == model_name:
            return model
    
    raise ValueError(f"Model {model_name} not found in configuration")


def get_experiment_config(config: Dict[str, Any], experiment_name: str) -> Dict[str, Any]:
    """
    Get configuration for specific experiment.
    
    Args:
        config: Full configuration dict
        experiment_name: Name of experiment
        
    Returns:
        Experiment configuration
    """
    experiments = config.get('experiments', {})
    
    if experiment_name not in experiments:
        raise ValueError(f"Experiment {experiment_name} not found in configuration")
    
    return experiments[experiment_name]
