# kitchen/pantry/operations/system/env_audit.py
"""
Pantry Ingredient for Environment Auditing.

This ingredient is responsible for validating that the host environment
meets all the prerequisites for running the kOS system.
"""
import sys
import shutil
import subprocess
from typing import Dict, Any

from kitchen.core.logging import get_logger

logger = get_logger(__name__)

MIN_PYTHON_VERSION = (3, 8)

def _check_python_version() -> Dict[str, Any]:
    """Checks if the current Python version meets the minimum requirement."""
    current_version = sys.version_info
    is_ok = current_version >= MIN_PYTHON_VERSION
    status = "OK" if is_ok else "FAIL"
    message = f"Current: {current_version.major}.{current_version.minor}.{current_version.micro}. Required: >={MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}"
    logger.info(f"Python version check: {status}. {message}")
    return {"check": "python_version", "status": status, "details": message}

def _check_command_exists(command: str) -> Dict[str, Any]:
    """Checks if a command-line tool is installed and available in the system's PATH."""
    path = shutil.which(command)
    is_ok = path is not None
    status = "OK" if is_ok else "FAIL"
    message = f"Found at: {path}" if is_ok else f"'{command}' not found in system PATH."
    logger.info(f"{command} check: {status}. {message}")
    return {"check": command, "status": status, "details": message}

def _check_docker_running() -> Dict[str, Any]:
    """Checks if the Docker daemon is running and responsive."""
    if not shutil.which("docker"):
        return {"check": "docker_daemon", "status": "FAIL", "details": "Docker command not found."}
    
    try:
        subprocess.run(["docker", "info"], capture_output=True, text=True, check=True, timeout=10)
        message = "Docker daemon is running."
        logger.info(f"Docker daemon check: OK. {message}")
        return {"check": "docker_daemon", "status": "OK", "details": message}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        message = f"Docker daemon is not running or responsive. Error: {e}"
        logger.error(f"Docker daemon check: FAIL. {message}")
        return {"check": "docker_daemon", "status": "FAIL", "details": message}

def run_audit() -> dict:
    """
    Validates the host environment for necessary dependencies.

    Returns:
        A dictionary containing the overall audit status and detailed results.
    """
    logger.info("--- Starting Environment Audit ---")
    
    results = [
        _check_python_version(),
        _check_command_exists("docker"),
        _check_command_exists("docker-compose"),
        _check_docker_running(),
    ]
    
    failures = [res for res in results if res["status"] == "FAIL"]
    
    if failures:
        logger.error("Environment audit FAILED. One or more checks did not pass.")
        return {"status": "failure", "details": failures}
    else:
        logger.info("--- Environment Audit PASSED ---")
        return {"status": "success", "details": results}

