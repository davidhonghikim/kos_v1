#!/usr/bin/env python3
"""
compose_service_config.py
Extracts service configuration from environment variables for Docker Compose generation.
"""
def get_enabled_services(env_vars):
    """Get list of enabled services from env_vars."""
    enabled_services = []
    for key, value in env_vars.items():
        if key.endswith('_ENABLE') and key.startswith('KOS_') and value.lower() == 'true':
            service_name = key[4:-7].lower()  # Remove KOS_ prefix and _ENABLE suffix
            enabled_services.append(service_name)
    return enabled_services

def get_service_config(service_name, env_vars):
    """Get configuration for a specific service from env_vars."""
    config = {}
    prefix = f"KOS_{service_name.upper()}"
    for key, value in env_vars.items():
        if key.startswith(prefix):
            config_key = key[len(prefix)+1:].lower()
            config[config_key] = value
    return config

if __name__ == "__main__":
    # Example usage for testing
    from compose_env_loader import load_env_vars
    env_vars = load_env_vars()
    enabled = get_enabled_services(env_vars)
    print(f"Enabled services: {enabled}")
    for svc in enabled:
        print(f"Config for {svc}: {get_service_config(svc, env_vars)}") 