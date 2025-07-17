#!/usr/bin/env python3
"""
compose_env_loader.py
Loads and validates environment variables for Docker Compose generation.
"""
import os
import re
from scripts.utils.env_utils import parse_env_file, validate_env_vars
from scripts.logger.logger import get_logger

logger = get_logger('compose_env_loader')

ENV_FILE = '.env'
REQUIRED_KEYS = [
    'KOS_API_ENABLE',
    'KOS_API_CONTAINER_NAME',
    'KOS_CONTAINER_NETWORK',
    'KOS_NETWORK_DRIVER',
    'KOS_NETWORK_SUBNET'
]

def load_env_vars(env_file=ENV_FILE):
    env_vars = {}
    if not os.path.exists(env_file):
        logger.log(f"Environment file {env_file} not found!", 'ERROR')
        raise FileNotFoundError(f"Environment file {env_file} not found!")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    # Resolve variable substitutions
    resolved_vars = resolve_variables(env_vars)
    # Validate required keys
    valid, missing = validate_env_vars(resolved_vars, REQUIRED_KEYS)
    if not valid:
        logger.log(f"Missing required env variables: {missing}", 'ERROR')
        raise ValueError(f"Missing required env variables: {missing}")
    return resolved_vars

def resolve_variables(env_vars):
    resolved = {}
    pattern = re.compile(r'\$\{([^}]+)\}')
    unresolved_vars = env_vars.copy()
    for _ in range(10):
        fully_resolved_this_pass = True
        for key, value in unresolved_vars.items():
            if pattern.search(value):
                fully_resolved_this_pass = False
                matches = pattern.findall(value)
                can_resolve = True
                for placeholder in matches:
                    if placeholder not in resolved:
                        can_resolve = False
                        break
                if can_resolve:
                    for placeholder in matches:
                        value = value.replace(f'${{{placeholder}}}', resolved.get(placeholder, ''))
                    resolved[key] = value
            else:
                resolved[key] = value
        for key in resolved:
            if key in unresolved_vars:
                del unresolved_vars[key]
        if not unresolved_vars or fully_resolved_this_pass:
            break
    if unresolved_vars:
        for key, value in unresolved_vars.items():
            logger.log(f"Could not fully resolve variable '{key}={value}'.", "ERROR")
            resolved[key] = value
    return resolved

if __name__ == "__main__":
    try:
        env = load_env_vars()
        logger.log(f"Loaded and validated {len(env)} environment variables.", 'SUCCESS')
    except Exception as e:
        logger.log(str(e), 'ERROR')
        exit(1) 