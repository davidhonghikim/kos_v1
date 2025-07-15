#!/usr/bin/env python3
"""
kOS v1 Automated Post-Install Diagnostic Script (Generic)
- Dynamically discovers all services from env/ports.env and .env
- Checks service status, logs, and configuration
- Summarizes issues and recommendations
- Prints summary and writes detailed report to logs/post_install_diagnostic.log
"""
import os
import sys
import subprocess
from datetime import datetime
import re
import yaml

# --- Constants ---
LOG_DIR = 'logs'
REPORT_FILE = os.path.join(LOG_DIR, 'post_install_diagnostic.log')
ENV_AUDIT_LOG = os.path.join(LOG_DIR, 'env_audit.log')
ENV_LOADER_LOG = os.path.join(LOG_DIR, 'env_loader.log')
DOCKER_GEN_LOG = os.path.join(LOG_DIR, 'docker_generator.log')
ENV_FILE = '.env'
PORTS_ENV = os.path.join('env', 'ports.env')
COMPOSE_FILE = os.path.join('docker', 'docker-compose.full.yml')

# --- Logging ---
def log_report(lines):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def print_and_log(lines):
    for line in lines:
        print(line)
    log_report(lines)

# --- Utility Functions ---
def parse_log_for_errors(logfile):
    errors = []
    if not os.path.exists(logfile):
        return errors
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'ERROR' in line or 'WARNING' in line:
                errors.append(line.strip())
    return errors

def parse_env_for_enabled_services(env_file):
    enabled = set()
    if not os.path.exists(env_file):
        return enabled
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('KOS_') and line.strip().endswith('_ENABLE=true'):
                name = line.strip()[4:-12].lower()
                enabled.add(name)
    return enabled

def parse_ports_env_services(ports_env_file):
    services = set()
    if not os.path.exists(ports_env_file):
        return services
    with open(ports_env_file, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'KOS_([A-Z0-9_]+)_EXTERNAL_PORT', line.strip())
            if m:
                services.add(m.group(1).lower())
    return services

def parse_compose_services(compose_file):
    if not os.path.exists(compose_file):
        return set()
    with open(compose_file, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
            return set(data.get('services', {}).keys())
        except Exception:
            return set()

def docker_compose_ps():
    try:
        result = subprocess.run(['docker-compose', '-f', COMPOSE_FILE, 'ps', '--services', '--filter', 'status=running'], capture_output=True, text=True)
        running = set(result.stdout.strip().split('\n')) if result.returncode == 0 else set()
        result = subprocess.run(['docker-compose', '-f', COMPOSE_FILE, 'ps', '--services', '--filter', 'status=exited'], capture_output=True, text=True)
        exited = set(result.stdout.strip().split('\n')) if result.returncode == 0 else set()
        return running, exited
    except Exception:
        return set(), set()

def get_service_logs(service):
    try:
        result = subprocess.run(['docker-compose', '-f', COMPOSE_FILE, 'logs', '--tail', '20', service], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else ''
    except Exception:
        return ''

# --- Main Diagnostic Logic ---
def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    summary = [f"===== kOS v1 Post-Install Diagnostic Report =====", f"Timestamp: {now}", ""]
    # 1. Parse logs for errors/warnings
    audit_errors = parse_log_for_errors(ENV_AUDIT_LOG)
    loader_errors = parse_log_for_errors(ENV_LOADER_LOG)
    gen_errors = parse_log_for_errors(DOCKER_GEN_LOG)
    if audit_errors:
        summary.append("[ENV AUDIT LOG ERRORS/WARNINGS]")
        summary.extend(audit_errors)
        summary.append("")
    if loader_errors:
        summary.append("[ENV LOADER LOG ERRORS/WARNINGS]")
        summary.extend(loader_errors)
        summary.append("")
    if gen_errors:
        summary.append("[DOCKER GENERATOR LOG ERRORS/WARNINGS]")
        summary.extend(gen_errors)
        summary.append("")
    # 2. Discover all services from ports.env
    discovered_services = parse_ports_env_services(PORTS_ENV)
    # 3. Check enabled services in .env
    enabled_services = parse_env_for_enabled_services(ENV_FILE)
    # 4. Check services in compose file
    compose_services = parse_compose_services(COMPOSE_FILE)
    # 5. Check running/exited services
    running, exited = docker_compose_ps()
    # 6. Cross-reference all discovered services
    summary.append("[SERVICE STATUS CHECK]")
    for name in sorted(discovered_services):
        status = []
        if name in enabled_services:
            status.append("ENABLED")
        else:
            status.append("NOT ENABLED")
        if name in compose_services:
            status.append("IN COMPOSE")
        else:
            status.append("NOT IN COMPOSE")
        if name in running:
            status.append("RUNNING")
        elif name in exited:
            status.append("EXITED/FAILED")
        else:
            status.append("NOT RUNNING")
        summary.append(f"- {name}: {', '.join(status)}")
        # If not running, get last logs
        if name in exited or (name in compose_services and name not in running):
            logs = get_service_logs(name)
            if logs:
                summary.append(f"  Last logs for {name}:")
                for line in logs.split('\n'):
                    summary.append(f"    {line}")
    summary.append("")
    # 7. Recommendations
    summary.append("[RECOMMENDATIONS]")
    for name in sorted(discovered_services):
        if name not in enabled_services:
            summary.append(f"- {name}: Add KOS_{name.upper()}_ENABLE=true to your env/settings.env or env/local.env.")
        elif name not in compose_services:
            summary.append(f"- {name}: Check for errors in logs/docker_generator.log and ensure all required variables are set in env/ports.env.")
        elif name not in running:
            summary.append(f"- {name}: Check docker-compose logs for {name} and resolve any container errors. See above for last logs.")
    summary.append("")
    summary.append("See logs/post_install_diagnostic.log for this full report.")
    print_and_log(summary)

if __name__ == '__main__':
    main() 