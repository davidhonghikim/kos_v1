# kitchen/pantry/operations/system/generate_env.py
"""
Pantry Ingredient for generating .env files.

This ingredient creates the necessary environment variable files for all
services based on templates.
"""
import os
import shutil
from typing import List, Dict, Any

from kitchen.core.logging import get_logger

logger = get_logger(__name__)

def create_all_env_files(force_overwrite: bool = False) -> Dict[str, Any]:
    """
    Finds all `.env.template` files in the project and copies them to `.env` files.

    Args:
        force_overwrite: If True, existing .env files will be overwritten.

    Returns:
        A dictionary containing the status and a list of created/existing files.
    """
    logger.info(f"Starting .env file generation (force_overwrite={force_overwrite})...")
    
    project_root = os.getcwd()
    created_files: List[str] = []
    skipped_files: List[str] = []

    for root, _, files in os.walk(project_root):
        # Avoid traversing into virtual environments or node_modules
        if "venv" in root or "node_modules" in root or ".git" in root:
            continue
            
        for file in files:
            if file.endswith(".env.template"):
                template_path = os.path.join(root, file)
                env_path = os.path.join(root, ".env")
                
                if not os.path.exists(env_path) or force_overwrite:
                    try:
                        shutil.copy(template_path, env_path)
                        logger.info(f"Created .env file at: {env_path}")
                        created_files.append(env_path)
                    except IOError as e:
                        logger.error(f"Failed to create .env file at {env_path}: {e}", exc_info=True)
                        return {"status": "failure", "error": str(e)}
                else:
                    logger.info(f"Skipping existing .env file at: {env_path}")
                    skipped_files.append(env_path)

    logger.info(f"Finished .env file generation. Created: {len(created_files)}, Skipped: {len(skipped_files)}.")
    return {
        "status": "success", 
        "created_files": created_files,
        "skipped_files": skipped_files
    }
