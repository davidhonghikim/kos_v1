#!/bin/bash
set -e
set -x
cd "$(dirname "$0")"

# --- STEP 1: HARDWARE DETECTION ---
VENV_DIR="venv"
PYTHON_CMD="$VENV_DIR/bin/python"
if [ ! -f "$PYTHON_CMD" ]; then
    PYTHON_CMD="$VENV_DIR/Scripts/python.exe"
fi
$PYTHON_CMD scripts/installer/gpu_autodetect.py

# --- STEP 2: ENV LOADER ---
$PYTHON_CMD scripts/installer/env_loader.py

# --- STEP 3: COMPOSE GENERATOR ---
$PYTHON_CMD scripts/installer/generate_docker_compose.py

# --- STEP 4: DOCKER COMPOSE UP ---
docker-compose -f docker/docker-compose.full.yml up -d --pull never

# --- STEP 5: LIVE MONITORING ---
while true; do
    docker ps --format '{{.Names}} {{.Status}}' | while read name status; do
        echo "[MONITOR] $name: $status"
        if [[ "$status" != Up* ]]; then
            echo "[ERROR] Container $name is not running. Investigate logs."
            docker logs "$name"
        fi
    done
    sleep 10
done

# --- STEP 6: USER OVERRIDE ---
# User can edit env files and rerun this script to reload config and restart containers

echo "[SUCCESS] All scripts completed without fatal errors."