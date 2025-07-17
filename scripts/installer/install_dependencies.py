#!/usr/bin/env python3
import os
import sys
import subprocess
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.utils.logger import get_logger

REQUIREMENTS_DIR = os.path.join(PROJECT_ROOT, 'requirements')
logger = get_logger('install_dependencies', log_mode='per_run')


def install_python_requirements():
    if not os.path.isdir(REQUIREMENTS_DIR):
        logger.log(f"Requirements directory not found: {REQUIREMENTS_DIR}", 'ERROR')
        sys.exit(1)
    req_files = [f for f in os.listdir(REQUIREMENTS_DIR) if f.endswith('.txt')]
    if not req_files:
        logger.log("No requirements files found.", 'WARNING')
        return
    for req_file in req_files:
        req_path = os.path.join(REQUIREMENTS_DIR, req_file)
        logger.log(f"Installing Python dependencies from {req_path}", 'INFO')
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_path])
        if result.returncode != 0:
            logger.log(f"Failed to install dependencies from {req_path}", 'ERROR')
            sys.exit(1)
        logger.log(f"Successfully installed dependencies from {req_path}", 'SUCCESS')


def main():
    logger.log("Starting dependency installation...", 'INFO')
    install_python_requirements()
    logger.log("All dependencies installed successfully.", 'SUCCESS')

if __name__ == '__main__':
    main() 