#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import socket
import requests
import yaml

# Ensure scripts/ is in sys.path for logger import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.utils.logger import get_logger

logger = get_logger('kos_install', log_mode='per_run')
PYTHON = sys.executable
INSTALLER_DIR = SCRIPT_DIR

# Helper to run a step and log/validate
def run_step(cmd, desc, check_file=None, background=False):
    logger.log(f"Starting: {desc}", 'INFO')
    print(f"[STEP] {desc}")
    if background:
        proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
        return proc
    else:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        if result.returncode != 0:
            logger.log(f"FAILED: {desc}", 'ERROR')
            print(f"[ERROR] {desc} failed.")
            sys.exit(1)
        if check_file and not os.path.exists(os.path.join(PROJECT_ROOT, check_file)):
            logger.log(f"FAILED: {desc} (missing {check_file})", 'ERROR')
            print(f"[ERROR] {desc} did not produce {check_file}.")
            sys.exit(1)
        logger.log(f"SUCCESS: {desc}", 'SUCCESS')
        print(f"[SUCCESS] {desc}")

# 1. Start dependency install in background (if script exists)
dep_installer = os.path.join(INSTALLER_DIR, 'install_dependencies.py')
dep_proc = None
if os.path.exists(dep_installer):
    dep_proc = run_step([PYTHON, dep_installer], "Dependency install (background)", background=True)
else:
    logger.log("No install_dependencies.py found, skipping dependency install.", 'WARNING')

# 2. Hardware detection (blocking)
gpu_detector = os.path.join(INSTALLER_DIR, 'gpu_autodetect.py')
run_step([PYTHON, gpu_detector], "Hardware detection (GPU)", check_file='env/gpu.env')

# 3. Env loader (blocking, creates images.env)
env_loader = os.path.join(INSTALLER_DIR, 'env_loader.py')
run_step([PYTHON, env_loader], "Environment loader", check_file='env/images.env')

# 4. Start image puller in background as soon as images.env is ready
image_puller = os.path.join(INSTALLER_DIR, 'pull_all_images.py')
img_proc = run_step([PYTHON, image_puller], "Image puller (background)", background=True)

# 5. Compose generator (blocking)
compose_gen = os.path.join(INSTALLER_DIR, 'generate_docker_compose.py')
run_step([PYTHON, compose_gen], "Docker Compose generator", check_file='docker/docker-compose.full.yml')

# 6. Wait for dependencies and image pulls to finish (or poll for readiness)
if dep_proc is not None:
    logger.log("Waiting for dependency install to finish...", 'INFO')
    dep_proc.wait()
if img_proc is not None:
    logger.log("Waiting for image pull to finish...", 'INFO')
    img_proc.wait()

# 7. Deploy: Recursively check for image availability and deploy containers
logger.log("Starting deployment (docker-compose up)...", 'INFO')
print("[STEP] Deploying containers...")
max_retries = 3
last_result = None
REQUIRED_CONTAINERS = [
    'kos-api', 'kos-frontend', 'kos-registry', 'kos-vault', 'kos-prompt-manager', 'kos-artifact-manager',
    'kos-postgres', 'kos-pgadmin', 'kos-mongo', 'kos-mongo-express', 'kos-neo4j', 'kos-weaviate', 'kos-minio',
    'kos-redis', 'kos-redis-commander', 'kos-elasticsearch', 'kos-n8n', 'kos-penpot', 'kos-penpot-backend',
    'kos-browseruse', 'kos-codium', 'kos-gitea', 'kos-supabase', 'kos-supabase-studio', 'kos-nextcloud',
    'kos-ollama', 'kos-openwebui', 'kos-automatic1111', 'kos-comfyui', 'kos-invokeai', 'kos-huggingface',
    'kos-prometheus', 'kos-grafana', 'kos-cadvisor', 'kos-admin-panel'
]
OPTIONAL_CONTAINERS = ['kos-context7']

def get_services_from_compose(compose_path):
    with open(compose_path, 'r') as f:
        compose = yaml.safe_load(f)
    return list(compose.get('services', {}).keys())

compose_path = os.path.join(PROJECT_ROOT, 'docker', 'docker-compose.full.yml')
services = get_services_from_compose(compose_path)

# Map service names to container names (from Compose)
service_to_container = {}
with open(compose_path, 'r') as f:
    compose = yaml.safe_load(f)
    for svc, cfg in compose.get('services', {}).items():
        service_to_container[svc] = cfg.get('container_name', svc)

# Attempt to pull and start each service individually
failed_required = []
failed_optional = []
running_required = []
running_optional = []
for svc in services:
    cname = service_to_container.get(svc, svc)
    is_required = cname in REQUIRED_CONTAINERS
    is_optional = cname in OPTIONAL_CONTAINERS
    # Pull image
    img = compose['services'][svc].get('image')
    if img:
        print(f"[INFO] Pulling image for {cname}: {img}")
        result = subprocess.run(["docker", "pull", img], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Failed to pull image for {cname}: {img}")
            logger.log(f"Failed to pull image for {cname}: {img} - {result.stderr}", 'ERROR')
            if is_required:
                failed_required.append((cname, 'image pull failed'))
            else:
                failed_optional.append((cname, 'image pull failed'))
            continue
    # Start container
    print(f"[INFO] Starting container: {cname}")
    result = subprocess.run(["docker-compose", "-f", compose_path, "up", "-d", svc], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Failed to start container: {cname}")
        logger.log(f"Failed to start container: {cname} - {result.stderr}", 'ERROR')
        if is_required:
            failed_required.append((cname, 'start failed'))
        else:
            failed_optional.append((cname, 'start failed'))
        continue
    # Check if running
    ps = subprocess.run(["docker", "ps", "-a", "--filter", f"name={cname}", "--format", "{{.Names}}\t{{.Status}}"], capture_output=True, text=True)
    status = ps.stdout.strip().split('\t')[-1] if '\t' in ps.stdout else ps.stdout.strip()
    if status.startswith('Up'):
        if is_required:
            running_required.append(cname)
        else:
            running_optional.append(cname)
    else:
        if is_required:
            failed_required.append((cname, status))
        else:
            failed_optional.append((cname, status))

# Print summary
print("\n[SUMMARY] Deployment Results:")
print(f"  Required containers running: {len(running_required)} / {len(REQUIRED_CONTAINERS)}")
if failed_required:
    print("  [ERROR] Required containers failed:")
    for cname, reason in failed_required:
        print(f"    - {cname}: {reason}")
if failed_optional:
    print("  [WARNING] Optional containers failed:")
    for cname, reason in failed_optional:
        print(f"    - {cname}: {reason}")
if len(running_required) == len(REQUIRED_CONTAINERS):
    print("[SUCCESS] All required containers are running.")
    sys.exit(0)
else:
    print("[FATAL] Not all required containers are running.")
    sys.exit(1)

# 8. Print summary
logger.log("Installer pipeline completed.", 'INFO')
print("[INFO] Installer pipeline completed.")

def check_http_health(url, timeout=5):
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False

def check_tcp_health(host, port, timeout=5):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

# Map service to health check (add more as needed)
SERVICE_HEALTH_CHECKS = {
    'kos-api': lambda: check_http_health('http://localhost:8000/health'),
    'kos-frontend': lambda: check_http_health('http://localhost:3000'),
    'kos-postgres': lambda: check_tcp_health('localhost', 5432),
    'kos-mongo': lambda: check_tcp_health('localhost', 27017),
    'kos-redis': lambda: check_tcp_health('localhost', 6379),
    'kos-neo4j': lambda: check_tcp_health('localhost', 7687),
    # Add more mappings as needed
}

# E2E health checks
print("[INFO] Running E2E health checks for required services...")
health_results = {}
for name in REQUIRED_CONTAINERS:
    # Only check if container is Up
    is_up = any(n == name for n, _ in running)
    if not is_up:
        health_results[name] = 'NOT UP'
        continue
    check = SERVICE_HEALTH_CHECKS.get(name)
    if check:
        healthy = check()
        health_results[name] = 'HEALTHY' if healthy else 'UNHEALTHY'
    else:
        health_results[name] = 'UNKNOWN (no check)'
# Print summary
print("\n[INFO] Service Health Summary:")
print("SERVICE           STATUS")
for name, status in health_results.items():
    print(f"{name:16} {status}")
# Attempt to restart unhealthy services and re-check
for name, status in health_results.items():
    if status == 'UNHEALTHY':
        print(f"[WARNING] Attempting to restart unhealthy service: {name}")
        logger.log(f"Attempting to restart unhealthy service: {name}", 'WARNING')
        subprocess.run(["docker", "restart", name])
        check = SERVICE_HEALTH_CHECKS.get(name)
        if check and check():
            print(f"[SUCCESS] {name} is now HEALTHY after restart.")
            logger.log(f"{name} is now HEALTHY after restart.", 'SUCCESS')
            health_results[name] = 'HEALTHY'
        else:
            print(f"[ERROR] {name} is still UNHEALTHY after restart.")
            logger.log(f"{name} is still UNHEALTHY after restart.", 'ERROR')
# Final health summary and exit code
total = len(REQUIRED_CONTAINERS)
healthy = sum(1 for s in health_results.values() if s == 'HEALTHY')
if healthy == total:
    print("[SUCCESS] All required services are healthy.")
    logger.log("All required services are healthy.", 'SUCCESS')
    sys.exit(0)
elif healthy > 0:
    print(f"[WARNING] Some required services are unhealthy. Healthy: {healthy}/{total}")
    logger.log(f"Some required services are unhealthy. Healthy: {healthy}/{total}", 'WARNING')
    sys.exit(2)
else:
    print("[FATAL] No required services are healthy after all attempts.")
    logger.log("No required services are healthy after all attempts.", 'ERROR')
    sys.exit(1) 