#!/bin/bash
echo "[INSTALLER] Installing kOS..."
python3 -m venv venv && source venv/bin/activate
pip install -r installer/requirements.txt
