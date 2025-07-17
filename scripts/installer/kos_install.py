#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import socket
import requests
import yaml
import configparser
import webbrowser
import threading
import re
import http.client

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

# Helper to run a step and log/validate
def canonicalize_service_name(name):
    return name.lower().replace('-', '_').replace(' ', '').replace('kos_', '').replace('_service', '')

def run_heartbeat():
    while True:
        print('[HEARTBEAT] Pipeline is running...')
        time.sleep(10)

hb_thread = threading.Thread(target=run_heartbeat, daemon=True)
hb_thread.start()

def check_url_status(url):
    try:
        resp = requests.get(url, timeout=5, allow_redirects=False)
        return resp.status_code, resp.headers.get('location', ''), resp.text[:200]
    except Exception as e:
        return None, None, str(e)

def print_container_log(container, lines=20):
    try:
        result = subprocess.run(["docker", "logs", "--tail", str(lines), container], capture_output=True, text=True)
        print(f"[LOGS] Last {lines} lines for {container}:")
        print(result.stdout)
    except Exception as e:
        print(f"[ERROR] Could not get logs for {container}: {e}")

try:
    compose_path = os.path.join(PROJECT_ROOT, 'docker', 'docker-compose.full.yml')
    with open(compose_path, 'r') as f:
        compose = yaml.safe_load(f)

    def parse_env_file(path):
        env = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
        return env

    settings_env = parse_env_file(os.path.join(PROJECT_ROOT, 'env', 'settings.env'))
    ports_env = parse_env_file(os.path.join(PROJECT_ROOT, 'env', 'ports.env'))

    # Canonicalize all service names from Compose
    compose_services = {canonicalize_service_name(svc): svc for svc in compose.get('services', {})}
    # Canonicalize all ENABLE flags
    enabled_services = [canonicalize_service_name(k.replace('_ENABLE', '')) for k, v in settings_env.items() if k.endswith('_ENABLE') and v.lower() == 'true']
    # Canonicalize OPTIONAL flags
    optional_services = [canonicalize_service_name(k.replace('_OPTIONAL', '')) for k, v in settings_env.items() if k.endswith('_OPTIONAL') and v.lower() == 'true']
    required_services = [s for s in enabled_services if s not in optional_services]

    # Map env/config service names to Compose service keys
    service_name_map = {s: compose_services[s] for s in enabled_services if s in compose_services}

    failed_required = []
    failed_optional = []
    running_required = []
    running_optional = []
    skipped_services = []
    for svc in enabled_services:
        svc_key = service_name_map.get(svc)
        if not svc_key:
            print(f'[WARNING] Enabled service "{svc}" not found in Compose file. Skipping.')
            logger.log(f'Enabled service "{svc}" not found in Compose file. Skipping.', 'WARNING')
            skipped_services.append(svc)
            continue
        cfg = compose['services'][svc_key]
        cname = cfg.get('container_name', svc_key)
        is_required = svc in required_services
        is_optional = svc in optional_services
        try:
            img = cfg.get('image')
            if img:
                print(f"[INFO] Pulling image for {cname}: {img}")
                result = subprocess.run(["docker", "pull", img], capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    print(f"[ERROR] Failed to pull image for {cname}: {img}")
                    logger.log(f"Failed to pull image for {cname}: {img} - {result.stderr}", 'ERROR')
                    if is_required:
                        failed_required.append((cname, 'image pull failed'))
                    else:
                        failed_optional.append((cname, 'image pull failed'))
                    continue
            print(f"[INFO] Starting container: {cname}")
            result = subprocess.run(["docker-compose", "-f", compose_path, "up", "-d", svc_key], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=300)
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
        except Exception as e:
            print(f'[ERROR] Exception while deploying {cname}: {e}')
            logger.log(f'Exception while deploying {cname}: {e}', 'ERROR')
            if is_required:
                failed_required.append((cname, f'exception: {e}'))
            else:
                failed_optional.append((cname, f'exception: {e}'))
        print(f'[HEARTBEAT] Finished deployment step for {cname}')

    # Print summary and open UIs
    print("\n[SUMMARY] Deployment Results:")
    print(f"  Required containers running: {len(running_required)} / {len(required_services)}")
    if failed_required:
        print("  [ERROR] Required containers failed:")
        for cname, reason in failed_required:
            print(f"    - {cname}: {reason}")
    if failed_optional:
        print("  [WARNING] Optional containers failed:")
        for cname, reason in failed_optional:
            print(f"    - {cname}: {reason}")
    if skipped_services:
        print("  [INFO] Skipped services (enabled in env, missing in Compose):")
        for svc in skipped_services:
            print(f"    - {svc}")
    print("\n[INFO] Service UI/Health Links:")
    for svc in enabled_services:
        svc_key = service_name_map.get(svc)
        if not svc_key:
            continue
        cfg = compose['services'][svc_key]
        cname = cfg.get('container_name', svc_key)
        envs = cfg.get('environment', [])
        env_dict = {}
        for e in envs:
            if '=' in e:
                k, v = e.split('=', 1)
                env_dict[k.strip()] = v.strip()
        public_uri = next((v for k, v in env_dict.items() if k.endswith('PUBLIC_URI')), None)
        ext_port = next((v for k, v in env_dict.items() if k.endswith('EXTERNAL_PORT')), None)
        health_cmd = next((v for k, v in env_dict.items() if k.endswith('HEALTH_CHECK_COMMAND')), None)
        # Service-specific URL overrides and health checks
        service_url_overrides = {
            'openwebui': 'http://localhost:3001',  # Direct to main UI, not auth
            'penpot': 'http://localhost:9002',     # Frontend URL
            'penpot-backend': 'http://localhost:6060',  # Backend health check
            'supabase': 'http://localhost:54321',  # API URL
            'supabase-studio': 'http://localhost:3003',  # Studio URL
            'weaviate': 'http://localhost:8082',   # Direct API
            'comfyui': 'http://localhost:8188',    # Direct UI
            'automatic1111': 'http://localhost:7860',  # Direct UI
        }
        
        # Service-specific health check URLs
        service_health_overrides = {
            'openwebui': 'http://localhost:3001/api/v1/health',
            'penpot': 'http://localhost:9002',
            'penpot-backend': 'http://localhost:6060/api/health',
            'supabase': 'http://localhost:54321/rest/v1/',
            'supabase-studio': 'http://localhost:3003',
            'weaviate': 'http://localhost:8082/v1/.well-known/ready',
            'comfyui': 'http://localhost:8188',
            'automatic1111': 'http://localhost:7860',
        }
        
        # Use service-specific overrides if available
        if svc_key in service_url_overrides:
            ui = service_url_overrides[svc_key]
        elif public_uri:
            ui = public_uri
        elif ext_port:
            ui = f"http://localhost:{ext_port}"
        else:
            ui = None
            
        # Use service-specific health check if available
        if svc_key in service_health_overrides:
            health = service_health_overrides[svc_key]
        elif health_cmd:
            m = re.search(r'curl\s+-f\s+(http[^\s]+)', health_cmd)
            if m:
                health = m.group(1)
        else:
            health = None
        if ui:
            print(f"  {cname}: UI -> {ui}")
            try:
                webbrowser.open(ui)
            except Exception as e:
                print(f"    [WARN] Could not open UI: {e}")
        elif health:
            print(f"  {cname}: Health Check -> {health}")
        else:
            print(f"  {cname}: No UI or health check link found.")
    print("\n[DIAGNOSTICS] Service Endpoint Checks:")
    for svc in enabled_services:
        svc_key = service_name_map.get(svc)
        if not svc_key:
            continue
        cfg = compose['services'][svc_key]
        cname = cfg.get('container_name', svc_key)
        envs = cfg.get('environment', [])
        env_dict = {}
        for e in envs:
            if '=' in e:
                k, v = e.split('=', 1)
                env_dict[k.strip()] = v.strip()
        public_uri = next((v for k, v in env_dict.items() if k.endswith('PUBLIC_URI')), None)
        ext_port = next((v for k, v in env_dict.items() if k.endswith('EXTERNAL_PORT')), None)
        health_cmd = next((v for k, v in env_dict.items() if k.endswith('HEALTH_CHECK_COMMAND')), None)
        service_url_overrides = {
            'openwebui': 'http://localhost:3001',
            'penpot': 'http://localhost:9002',
            'penpot-backend': 'http://localhost:6060',
            'supabase': 'http://localhost:54321',
            'supabase-studio': 'http://localhost:3003',
            'weaviate': 'http://localhost:8082',
            'comfyui': 'http://localhost:8188',
            'automatic1111': 'http://localhost:7860',
        }
        service_health_overrides = {
            'openwebui': 'http://localhost:3001/api/v1/health',
            'penpot': 'http://localhost:9002',
            'penpot-backend': 'http://localhost:6060/api/health',
            'supabase': 'http://localhost:54321/rest/v1/',
            'supabase-studio': 'http://localhost:3003',
            'weaviate': 'http://localhost:8082/v1/.well-known/ready',
            'comfyui': 'http://localhost:8188',
            'automatic1111': 'http://localhost:7860',
        }
        if svc_key in service_url_overrides:
            ui = service_url_overrides[svc_key]
        elif public_uri:
            ui = public_uri
        elif ext_port:
            ui = f"http://localhost:{ext_port}"
        else:
            ui = None
        if svc_key in service_health_overrides:
            health = service_health_overrides[svc_key]
        elif health_cmd:
            m = re.search(r'curl\s+-f\s+(http[^\s]+)', health_cmd)
            if m:
                health = m.group(1)
        else:
            health = None
        for label, url in [("UI", ui), ("Health", health)]:
            if url:
                code, location, snippet = check_url_status(url)
                if code is None:
                    print(f"  {cname} {label}: [ERROR] Could not connect: {snippet}")
                    print_container_log(cname)
                elif code in (301, 302, 307, 308):
                    print(f"  {cname} {label}: [REDIRECT] {url} -> {location}")
                elif code == 401 or code == 403:
                    print(f"  {cname} {label}: [AUTH REQUIRED] {url}")
                elif code == 200:
                    print(f"  {cname} {label}: [OK] {url}")
                else:
                    print(f"  {cname} {label}: [HTTP {code}] {url}")
                    print(f"    [SNIPPET] {snippet}")
                    print_container_log(cname)
            else:
                print(f"  {cname} {label}: [NO ENDPOINT]")
    if len(running_required) == len(required_services):
        print("[SUCCESS] All required containers are running.")
        logger.log("All required containers are running.", 'SUCCESS')
        sys.exit(0)
    else:
        print("[FATAL] Not all required containers are running.")
        logger.log("Not all required containers are running.", 'ERROR')
        sys.exit(1)

except Exception as e:
    print(f'[FATAL ERROR] {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
    logger.log(f'FATAL ERROR: {type(e).__name__}: {e}', 'ERROR')
    sys.exit(1) 