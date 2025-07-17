#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time

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

# Always attempt to deploy all containers, regardless of failures
for attempt in range(1, max_retries+1):
    result = subprocess.run(["docker-compose", "-f", "docker/docker-compose.full.yml", "up", "-d", "--pull", "never"], cwd=PROJECT_ROOT)
    last_result = result
    if result.returncode == 0:
        logger.log(f"docker-compose up succeeded (attempt {attempt})", 'SUCCESS')
        print(f"[INFO] docker-compose up succeeded (attempt {attempt})")
    else:
        logger.log(f"docker-compose up failed (attempt {attempt})", 'ERROR')
        print(f"[ERROR] docker-compose up failed (attempt {attempt})")
    # After each attempt, check which required containers are running
    ps = subprocess.run(["docker", "ps", "-a", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"], capture_output=True, text=True)
    lines = ps.stdout.strip().split('\n')[1:]  # skip header
    failed = []
    running = []
    for l in lines:
        if not l: continue
        parts = l.split('\t')
        if len(parts) < 3:
            continue
        name = parts[0]
        status = parts[2]
        if name in OPTIONAL_CONTAINERS:
            continue  # Do not treat optional containers as required
        if status.startswith('Up'):
            running.append((name, status))
        else:
            failed.append((name, status))
    required_running = [name for name, _ in running if name in REQUIRED_CONTAINERS]
    required_failed = [name for name, _ in failed if name in REQUIRED_CONTAINERS]
    # If all required containers are running, break early
    if len(required_failed) == 0:
        break
    else:
        print(f"[WARNING] Not all required containers are running after attempt {attempt}. Retrying failed containers...")
        time.sleep(15)
# Final status summary
ps = subprocess.run(["docker", "ps", "-a", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"], capture_output=True, text=True)
print("[INFO] Final Docker container status:")
print(ps.stdout)
lines = ps.stdout.strip().split('\n')[1:]  # skip header
failed = []
running = []
created = []
for l in lines:
    if not l: continue
    parts = l.split('\t')
    if len(parts) < 3:
        continue
    name = parts[0]
    status = parts[2]
    if name in OPTIONAL_CONTAINERS:
        continue  # Do not treat optional containers as required
    if status.startswith('Up'):
        running.append((name, status))
    elif status.startswith('Created') or status.startswith('Exited'):
        created.append((name, status))
    else:
        failed.append((name, status))
required_running = [name for name, _ in running if name in REQUIRED_CONTAINERS]
required_created = [name for name, _ in created if name in REQUIRED_CONTAINERS]
required_failed = [name for name, _ in failed if name in REQUIRED_CONTAINERS]
# Attempt to start any required containers that are in 'Created' or 'Exited' state
for name, status in created:
    if name in REQUIRED_CONTAINERS:
        print(f"[INFO] Attempting to start required container: {name} (was {status})")
        logger.log(f"Attempting to start required container: {name} (was {status})", 'WARNING')
        try:
            result = subprocess.run(["docker", "start", name], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[SUCCESS] Started container: {name}")
                logger.log(f"Started container: {name}", 'SUCCESS')
            else:
                print(f"[ERROR] Failed to start container: {name}")
                logger.log(f"Failed to start container: {name} - {result.stderr}", 'ERROR')
        except Exception as e:
            print(f"[ERROR] Exception while starting container {name}: {e}")
            logger.log(f"Exception while starting container {name}: {e}", 'ERROR')
# Re-check status after individual starts
ps = subprocess.run(["docker", "ps", "-a", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"], capture_output=True, text=True)
print("[INFO] Docker container status after individual starts:")
print(ps.stdout)
lines = ps.stdout.strip().split('\n')[1:]  # skip header
failed = []
running = []
for l in lines:
    if not l: continue
    parts = l.split('\t')
    if len(parts) < 3:
        continue
    name = parts[0]
    status = parts[2]
    if name in OPTIONAL_CONTAINERS:
        continue
    if status.startswith('Up'):
        running.append((name, status))
    else:
        failed.append((name, status))
required_running = [name for name, _ in running if name in REQUIRED_CONTAINERS]
required_failed = [name for name, _ in failed if name in REQUIRED_CONTAINERS]
if len(required_running) == 0:
    logger.log(f"[FATAL] No required containers are running after all attempts.", 'ERROR')
    print(f"[FATAL] No required containers are running after all attempts.")
    for name, status in failed:
        print(f"  - {name}: {status}")
        print(f"[INFO] Last 50 lines of logs for {name}:")
        try:
            logs = subprocess.run(["docker", "logs", name, "--tail", "50"], capture_output=True, text=True)
            print(logs.stdout)
        except Exception as e:
            print(f"[ERROR] Could not fetch logs for {name}: {e}")
    sys.exit(1)
elif len(required_failed) > 0:
    logger.log(f"[WARNING] Some required containers failed to start after all attempts.", 'WARNING')
    print(f"[WARNING] Some required containers failed to start after all attempts.")
    for name, status in failed:
        print(f"  - {name}: {status}")
        print(f"[INFO] Last 50 lines of logs for {name}:")
        try:
            logs = subprocess.run(["docker", "logs", name, "--tail", "50"], capture_output=True, text=True)
            print(logs.stdout)
        except Exception as e:
            print(f"[ERROR] Could not fetch logs for {name}: {e}")
    print(f"[INFO] Required containers running: {len(required_running)} / {len(REQUIRED_CONTAINERS)}")
    print(f"[INFO] Installer pipeline completed with warnings. Some services may be unavailable.")
    sys.exit(2)
else:
    logger.log("All required containers are running. Optional containers may have failed.", 'SUCCESS')
    print("[SUCCESS] All required containers are running. Optional containers may have failed.")
    sys.exit(0)
# 8. Print summary
logger.log("Installer pipeline completed.", 'INFO')
print("[INFO] Installer pipeline completed.") 