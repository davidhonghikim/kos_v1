#!/usr/bin/env python3
"""
kOS v1 Environment Audit Script (env_audit.py)
- Detects port conflicts and missing enable flags
- Logs all findings to logs/env_audit.log
- Always runs env_loader.py and generate_docker_compose.py after audit
- OS-agnostic, robust, and uses current timestamp
"""
import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import re
import subprocess
from datetime import datetime
from scripts.utils.logger import get_logger
from scripts.utils.env_utils import parse_env_file
logger = get_logger('env_audit')

# --- Constants ---
PORTS_ENV = os.path.join('env', 'ports.env')
SETTINGS_ENV = os.path.join('env', 'settings.env')
LOCAL_ENV = os.path.join('env', 'local.env')
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'env_audit.log')
ENV_LOADER = 'scripts/installer/env_loader.py'
DOCKER_GEN = 'scripts/installer/generate_docker_compose.py'

# --- Logging ---
def print_summary(summary):
    print("\n===== kOS v1 Environment Audit Summary =====")
    for line in summary:
        print(line)
    print("===========================================\n")

# --- Utility Functions ---
def get_services_from_ports_env(env):
    services = set()
    for k in env:
        m = re.match(r'KOS_([A-Z0-9_]+)_EXTERNAL_PORT', k)
        if m:
            services.add(m.group(1))
    return sorted(services)

def get_port_map(env):
    port_map = {}
    for k, v in env.items():
        m = re.match(r'KOS_([A-Z0-9_]+)_EXTERNAL_PORT', k)
        if m:
            port = v
            service = m.group(1)
            port_map.setdefault(port, []).append(service)
    return port_map

def get_enable_flags(settings_env, local_env):
    flags = set()
    for env in (settings_env, local_env):
        for k in env:
            m = re.match(r'KOS_([A-Z0-9_]+)_ENABLE', k)
            if m:
                flags.add(m.group(1))
    return flags

def run_script(script):
    if not os.path.exists(script):
        logger.log(f"Script not found: {script}", 'WARNING')  # Changed from ERROR to WARNING
        return 0  # Do not treat as error
    logger.log(f"Running {script}...", 'INFO')
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode != 0:
        logger.log(f"{script} failed: {result.stderr}", 'ERROR')
    else:
        logger.log(f"{script} completed successfully.", 'INFO')
    return result.returncode

# --- Main Audit Logic ---
# Only require enable flags for real, user-requested, separately managed services
REQUIRED_ENABLE_FLAGS = [
    'KOS_SUPABASE_STUDIO_ENABLE',
    # Add other real, user-requested service enable flags here as needed
]

def main():
    summary = []
    # Parse env files
    ports_env = parse_env_file(PORTS_ENV)
    settings_env = parse_env_file(SETTINGS_ENV)
    local_env = parse_env_file(LOCAL_ENV)
    if not ports_env:
        logger.log("Failed to parse ports.env. Aborting audit.", 'ERROR')
        sys.exit(1)
    # 1. Port Conflict Audit
    port_map = get_port_map(ports_env)
    conflicts = {p: s for p, s in port_map.items() if len(s) > 1}
    if conflicts:
        for port, services in conflicts.items():
            msg = f"Port conflict: {port} used by {', '.join(services)}"
            logger.log(msg, 'ERROR')
            summary.append(f"ERROR: {msg}")
    else:
        logger.log("No port conflicts detected.", 'INFO')
        summary.append("No port conflicts detected.")
    # 2. Enable Flag Audit (only for REQUIRED_ENABLE_FLAGS)
    all_flags = set(list(settings_env.keys()) + list(local_env.keys()))
    missing_flags = [flag for flag in REQUIRED_ENABLE_FLAGS if flag not in all_flags]
    if missing_flags:
        for flag in missing_flags:
            msg = f"Required enable flag missing: {flag}"
            logger.log(msg, 'WARNING')
            summary.append(f"WARNING: {msg}")
    else:
        logger.log("All required enable flags present.", 'INFO')
        summary.append("All required enable flags present.")
    # 3. Summary
    summary.append(f"Total port conflicts: {len(conflicts)}")
    summary.append(f"Total missing required enable flags: {len(missing_flags)}")
    print_summary(summary)
    # 4. Always run env_loader.py and generate_docker_compose.py
    run_script(ENV_LOADER)
    run_script(DOCKER_GEN)

if __name__ == '__main__':
    main() 