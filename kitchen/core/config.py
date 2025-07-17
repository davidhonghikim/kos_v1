# kitchen/core/config.py
"""
Configuration management for the Kitchen Orchestration System.

This module is responsible for loading, validating, and providing access to
the kitchen's configuration settings from a central JSON file. This approach
allows for easy modification of system behavior without altering the source code.
"""

import json
import os
from typing import Any, Dict, Optional

from .logging import get_logger

# --- Constants ---
CONFIG_FILENAME = "kitchen_config.json"
DEFAULT_PANTRY_PATH = "kitchen/pantry"
DEFAULT_RECIPES_PATH = "kitchen/recipes"

# --- Logger ---
logger = get_logger(__name__)

# --- Configuration Class ---

class KitchenConfig:
    """
    A class to hold and provide access to kitchen configuration settings.
    """
    def __init__(self, config_data: Dict[str, Any]):
        """
        Initializes the configuration object.

        Args:
            config_data: A dictionary containing the configuration settings.
        """
        self._config = config_data
        self.pantry_path: str = self._get_path('pantry_path', DEFAULT_PANTRY_PATH)
        self.recipes_path: str = self._get_path('recipes_path', DEFAULT_RECIPES_PATH)
        self.log_level: str = self._config.get('log_level', 'INFO').upper()
        logger.info(f"Configuration loaded. Log level: {self.log_level}")

    def _get_path(self, key: str, default: str) -> str:
        """
        Retrieves a path from the config, ensuring it's an absolute path.
        If the path doesn't exist, it logs a warning.
        """
        path = self._config.get(key, default)
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            logger.warning(f"The configured path '{key}' does not exist: {abs_path}")
        return abs_path

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves a configuration value by key.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value or the default.
        """
        return self._config.get(key, default)

    def __repr__(self) -> str:
        return f"<KitchenConfig pantry='{self.pantry_path}' recipes='{self.recipes_path}'>"

# --- Global Instance ---
_config_instance: Optional[KitchenConfig] = None

# --- Functions ---

def load_config(config_path: Optional[str] = None) -> KitchenConfig:
    """
    Loads the kitchen configuration from a JSON file.

    It searches for the config file in the provided path or in the root
    directory of the project. If not found, it creates a default config object.

    Args:
        config_path: The optional path to the configuration file.

    Returns:
        A KitchenConfig instance.
    """
    global _config_instance
    if _config_instance:
        return _config_instance

    path = config_path or os.path.join(os.getcwd(), CONFIG_FILENAME)
    config_data = {}
    
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                config_data = json.load(f)
            logger.info(f"Successfully loaded configuration from {path}")
        else:
            logger.warning(f"Configuration file not found at {path}. Using default settings.")
            # Create a default config file for the user to edit
            default_config = {
                "pantry_path": DEFAULT_PANTRY_PATH,
                "recipes_path": DEFAULT_RECIPES_PATH,
                "log_level": "INFO"
            }
            with open(path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Created a default '{CONFIG_FILENAME}' file. Please review it.")
            config_data = default_config

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading or creating config file at {path}: {e}", exc_info=True)
        logger.warning("Falling back to default configuration values.")
        config_data = {
            "pantry_path": DEFAULT_PANTRY_PATH,
            "recipes_path": DEFAULT_RECIPES_PATH,
            "log_level": "INFO"
        }

    _config_instance = KitchenConfig(config_data)
    return _config_instance

# --- Example Usage ---
if __name__ == "__main__":
    # This block demonstrates how to use the config loader.
    logger.info("Demonstrating configuration loading...")
    
    # Create a dummy config file for the demonstration
    dummy_config_path = "temp_kitchen_config.json"
    with open(dummy_config_path, 'w') as f:
        json.dump({"log_level": "DEBUG", "pantry_path": "kitchen/pantry_test"}, f)

    # Load the dummy config
    config = load_config(dummy_config_path)
    
    logger.info(f"Config object: {config}")
    logger.info(f"Pantry Path: {config.pantry_path}")
    logger.info(f"Log Level: {config.log_level}")

    # Clean up the dummy file
    os.remove(dummy_config_path)
    
    # Demonstrate fallback
    logger.info("\nDemonstrating fallback to default config...")
    _config_instance = None # Reset for demonstration
    non_existent_path = "non_existent_config.json"
    if os.path.exists(non_existent_path):
        os.remove(non_existent_path)
        
    config = load_config(non_existent_path)
    logger.info(f"Config object: {config}")
    logger.info(f"Pantry Path: {config.pantry_path}")
    logger.info(f"Log Level: {config.log_level}")
    
    # Clean up the created default file
    if os.path.exists(non_existent_path):
        os.remove(non_existent_path)

