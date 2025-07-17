#!/bin/bash
cd "$(dirname "$0")"
VENV_DIR="venv"
PYTHON_CMD="$VENV_DIR/bin/python"
if [ ! -f "$PYTHON_CMD" ]; then
    PYTHON_CMD="$VENV_DIR/Scripts/python.exe"
fi
"$PYTHON_CMD" scripts/installer/kos_install.py
exit $?