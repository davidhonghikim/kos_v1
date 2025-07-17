# kitchen/pantry/operations/system/generate_docker_compose.py
"""
Pantry Ingredient for generating the main docker-compose.yml file.

This ingredient combines multiple docker-compose profile files into a single,
cohesive docker-compose.yml file for execution. It requires the PyYAML package.
"""
import os
from typing import List, Dict, Any
import yaml  # PyYAML must be installed

from kitchen.core.logging import get_logger

logger = get_logger(__name__)

def _merge_dicts(base: Dict, merge: Dict) -> Dict:
    """
    Recursively merges two dictionaries. The `merge` dict's values
    overwrite the `base` dict's values.
    """
    for key, value in merge.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            base[key] = _merge_dicts(base[key], value)
        else:
            base[key] = value
    return base

def build_from_profiles(profiles: List[str], output_file: str, docker_dir: str = "docker") -> Dict[str, Any]:
    """
    Generates a docker-compose.yml file from a list of service profiles.

    Args:
        profiles: A list of profile names (e.g., ['core', 'ai']) to include.
        output_file: The path to write the final docker-compose file to.
        docker_dir: The directory containing the docker-compose profile files.

    Returns:
        A dictionary containing the status and the path to the generated file.
    """
    logger.info(f"Building docker-compose from profiles: {profiles} -> {output_file}")
    
    if not os.path.isdir(docker_dir):
        msg = f"Docker profiles directory not found: {docker_dir}"
        logger.error(msg)
        return {"status": "failure", "error": msg}

    merged_config: Dict[str, Any] = {"version": "3.8", "services": {}, "volumes": {}, "networks": {}}
    
    for profile in profiles:
        profile_path = os.path.join(docker_dir, f"docker-compose.{profile}.yml")
        if not os.path.exists(profile_path):
            logger.warning(f"Profile file not found, skipping: {profile_path}")
            continue
        
        try:
            with open(profile_path, 'r') as f:
                profile_data = yaml.safe_load(f)
            
            if profile_data:
                merged_config = _merge_dicts(merged_config, profile_data)
                logger.info(f"Successfully merged profile: {profile}")
            else:
                logger.warning(f"Profile file is empty, skipping: {profile_path}")

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML from {profile_path}: {e}", exc_info=True)
            return {"status": "failure", "error": f"YAML error in {profile_path}"}

    try:
        with open(output_file, 'w') as f:
            yaml.dump(merged_config, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Successfully wrote merged docker-compose file to: {output_file}")
    except IOError as e:
        logger.error(f"Failed to write merged docker-compose file: {e}", exc_info=True)
        return {"status": "failure", "error": f"Could not write to {output_file}"}

    return {"status": "success", "output_file": os.path.abspath(output_file)}
