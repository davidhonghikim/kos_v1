# kitchen/core/logging.py
"""
Standardized logging setup for the Kitchen Orchestration System.

This module provides a centralized logging configuration to ensure consistent,
formatted, and easily debuggable output across all components of the
kitchen engine and its associated operations.

- Configures a root logger.
- Sets a standard format for log messages.
- Allows for easy import and use in other kitchen modules.
"""

import logging
import sys

# --- Constants ---
LOG_FORMAT = (
    "%(asctime)s - %(levelname)-8s - %(name)-25s - %(module)-15s:%(lineno)d - %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Global Logger Configuration ---

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    stream=sys.stdout,  # Log to standard output
)

# --- Functions ---

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger instance with the specified name.

    This is the primary function to be used by other modules to get a
    correctly configured logger instance. Using this function ensures
    that all loggers inherit the root configuration.

    Args:
        name: The name for the logger, typically __name__ of the calling module.

    Returns:
        A configured Logger instance.
    """
    return logging.getLogger(name)

def set_log_level(level: str):
    """
    Sets the global logging level for the root logger.

    Allows for dynamically changing the verbosity of the logs. For example,
    setting the level to 'DEBUG' for more detailed output during development.

    Args:
        level: The desired logging level as a string (e.g., "DEBUG", "INFO",
               "WARNING", "ERROR").

    Raises:
        ValueError: If the provided level is not a valid logging level.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logging.getLogger().setLevel(numeric_level)
    # Log the level change itself
    logger = get_logger(__name__)
    logger.info(f"Global log level set to {level.upper()}")


# --- Example Usage (for direct execution) ---
if __name__ == "__main__":
    # This block demonstrates how to use the logger.
    # It will only run when this script is executed directly.

    # Get a logger for this specific module
    main_logger = get_logger(__name__)

    main_logger.info("Logging system initialized. This is an info message.")
    main_logger.debug("This is a debug message. It will not be visible by default.")
    main_logger.warning("This is a warning message.")
    main_logger.error("This is an error message.")

    # Change the log level to show debug messages
    try:
        main_logger.info("Setting log level to DEBUG...")
        set_log_level("DEBUG")
        main_logger.debug("This debug message should now be visible.")
    except ValueError as e:
        main_logger.error(f"Failed to set log level: {e}")

    # Test with an invalid level
    try:
        main_logger.info("Attempting to set an invalid log level...")
        set_log_level("INVALID_LEVEL")
    except ValueError as e:
        main_logger.error(f"Caught expected error: {e}")

