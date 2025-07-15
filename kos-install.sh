#!/bin/bash
set -x
# ==============================================================================
# KOS v1 Automated Deployment Script - FINAL DEBUG VERSION
# This script will NOT exit silently. It will show every command and error.
# ==============================================================================

# --- STEP 0: SCRIPT SETUP ---
echo "[DEBUG] Starting kos-install.sh..."
# The 'cd' command MUST be first to ensure all relative paths are correct.
# It changes the directory to the script's location.
cd "$(dirname "$0")" || exit 1
echo "[DEBUG] Current working directory set to: $(pwd)"

# --- STEP 1: PYTHON CHECK AND VENV SETUP ---
echo
echo "--- STEP 1: SETTING UP PYTHON ---"
VENV_DIR="venv"
PYTHON_CMD=""

if [ -d "$VENV_DIR" ]; then
    echo "[DEBUG] Virtual environment './${VENV_DIR}' already exists. Skipping creation."
else
    echo "[DEBUG] Searching for a python3 or python command..."
    if command -v python3 &> /dev/null; then
        echo "[DEBUG] Found python3. Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "[FATAL ERROR] Command 'python3 -m venv ${VENV_DIR}' failed."
            exit 1
        fi
    elif command -v python &> /dev/null; then
        echo "[DEBUG] Found python. Creating virtual environment..."
        python -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "[FATAL ERROR] Command 'python -m venv ${VENV_DIR}' failed."
            exit 1
        fi
    else
        echo "[FATAL ERROR] Could not find 'python3' or 'python' in your system's PATH."
        exit 1
    fi
    echo "[DEBUG] Virtual environment created successfully."
fi

PYTHON_CMD="${VENV_DIR}/bin/python"
PIP_CMD="${VENV_DIR}/bin/pip"
echo "[DEBUG] Using Python from: ${PYTHON_CMD}"

# --- STEP 2: INSTALL DEPENDENCIES ---
echo
echo "--- STEP 2: INSTALLING DEPENDENCIES ---"
echo "[DEBUG] Executing: ${PIP_CMD} install -r requirements.txt"
"${PIP_CMD}" install --verbose -r "requirements.txt" > pip-install.log 2>&1
cat pip-install.log
if [ $? -ne 0 ]; then
    echo "[FATAL ERROR] Failed to install Python packages from requirements.txt"
    exit 1
fi
echo "[DEBUG] Python dependencies installed successfully."

# --- STEP 3: RUNNING BUILD SCRIPTS ---
echo
echo "--- STEP 3: EXECUTING BUILD SCRIPTS ---"
echo "[DEBUG] Executing: ${PYTHON_CMD} installer/env_loader.py"
"${PYTHON_CMD}" "installer/env_loader.py"
if [ $? -ne 0 ]; then
    echo "[FATAL ERROR] The 'env_loader.py' script failed."
    exit 1
fi
echo "[DEBUG] 'env_loader.py' finished."

echo
echo "[DEBUG] Executing: ${PYTHON_CMD} installer/env_audit.py"
"${PYTHON_CMD}" "installer/env_audit.py"
if [ $? -ne 0 ]; then
    echo "[FATAL ERROR] The 'env_audit.py' script failed."
    exit 1
fi
echo "[DEBUG] 'env_audit.py' finished."

echo
echo "[DEBUG] Executing: ${PYTHON_CMD} installer/generate_docker_compose.py"
"${PYTHON_CMD}" "installer/generate_docker_compose.py"
if [ $? -ne 0 ]; then
    echo "[FATAL ERROR] The 'generate_docker_compose.py' script failed."
    exit 1
fi
echo "[DEBUG] 'generate_docker_compose.py' finished."

echo
echo "--- SCRIPT FINISHED ---"
echo "[SUCCESS] All scripts completed without fatal errors."
echo "Please check the output above for any WARNINGS or non-fatal ERRORS from the Python scripts."