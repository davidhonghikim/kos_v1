#!/usr/bin/env python3
"""
compose_file_generator.py
Generates Docker Compose files from environment variables and service configs.
"""
import os
import sys
import yaml
from pathlib import Path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.utils.logger import get_logger
from scripts.installer.compose_env_loader import load_env_vars
from scripts.installer.compose_service_config import get_enabled_services, get_service_config
from scripts.installer.compose_gpu_assignment import assign_gpus_to_services
from scripts.installer.compose_file_validator import validate_compose_file

logger = get_logger('compose_file_generator')

COMPOSE_DIR = 'docker'

# Example: Only generate a full stack compose file for brevity

def generate_compose_file():
    env_vars = load_env_vars()
    enabled_services = get_enabled_services(env_vars)
    service_configs = {svc: get_service_config(svc, env_vars) for svc in enabled_services}
    gpu_assignments = assign_gpus_to_services(env_vars, enabled_services)
    compose_data = {
        'version': '3.8',
        'services': {},
        'networks': {
            env_vars['KOS_CONTAINER_NETWORK']: {
                'driver': env_vars['KOS_NETWORK_DRIVER'],
                'ipam': {
                    'config': [{'subnet': env_vars['KOS_NETWORK_SUBNET']}]
                }
            }
        },
        'volumes': {}
    }
    for svc, config in service_configs.items():
        svc_def = {
            'image': config.get('image'),
            'container_name': config.get('container_name'),
            'networks': [env_vars['KOS_CONTAINER_NETWORK']],
            'restart': config.get('restart_policy', 'unless-stopped'),
        }
        if gpu_assignments[svc]['gpu']:
            svc_def['deploy'] = {
                'resources': {
                    'reservations': {
                        'devices': [
                            {
                                'driver': 'nvidia',
                                'count': 'all',
                                'capabilities': ['gpu']
                            }
                        ]
                    }
                }
            }
        compose_data['services'][svc] = svc_def
    # Write compose file
    Path(COMPOSE_DIR).mkdir(exist_ok=True)
    compose_file = os.path.join(COMPOSE_DIR, 'docker-compose.full.yml')
    with open(compose_file, 'w') as f:
        yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
    logger.log(f"Generated: {compose_file}", 'SUCCESS')
    # Validate
    valid, msg = validate_compose_file(compose_file)
    if not valid:
        logger.log(msg, 'ERROR')
        raise ValueError(msg)
    logger.log("Compose file validation passed.", 'SUCCESS')

if __name__ == "__main__":
    try:
        generate_compose_file()
    except Exception as e:
        logger.log(str(e), 'ERROR')
        exit(1) 