#!/usr/bin/env python3
"""
compose_file_validator.py
Validates generated files (env, compose, etc.) for syntax and required keys/sections.
"""
import os
import yaml

def validate_env_file(env_file):
    if not os.path.exists(env_file):
        return False, f"Env file {env_file} does not exist."
    with open(env_file, 'r') as f:
        for line in f:
            if '=' not in line and not line.strip().startswith('#') and line.strip():
                return False, f"Malformed line in env file: {line.strip()}"
    return True, "Env file syntax OK."

def validate_compose_file(compose_file):
    if not os.path.exists(compose_file):
        return False, f"Compose file {compose_file} does not exist."
    try:
        with open(compose_file, 'r') as f:
            data = yaml.safe_load(f)
        if 'services' not in data or not data['services']:
            return False, "Compose file missing 'services' section."
        if 'networks' not in data or not data['networks']:
            return False, "Compose file missing 'networks' section."
    except Exception as e:
        return False, f"YAML parse error: {e}"
    return True, "Compose file syntax OK."

if __name__ == "__main__":
    # Example usage for testing
    print(validate_env_file('.env'))
    print(validate_compose_file('docker/docker-compose.full.yml')) 