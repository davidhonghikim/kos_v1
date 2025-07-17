#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from datetime import datetime

# Ensure scripts/ is in sys.path for logger import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.utils.logger import get_logger

IMAGES_FILE = os.path.join(PROJECT_ROOT, 'env', 'images.env')
FAILED_LOG_DIR = os.path.join(PROJECT_ROOT, 'logs', 'pull_all_images')

# Setup logger
logger = get_logger('pull_all_images', log_mode='per_run')

def read_images(file_path):
    images = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                images.append(line)
    return images

def ensure_log_dir():
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    log_dir = os.path.join(FAILED_LOG_DIR, year, month)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def pull_image(image):
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        logger.log(f"Pulling '{image}' (attempt {attempt}/{max_attempts})...", level="INFO")
        print(f"[INFO] Pulling '{image}' (attempt {attempt}/{max_attempts})...")
        try:
            result = subprocess.run(["docker", "pull", image], capture_output=True, text=True)
            if result.returncode == 0:
                logger.log(f"Successfully pulled '{image}'", level="SUCCESS")
                print(f"[SUCCESS] Successfully pulled '{image}'")
                return True
            else:
                logger.log(f"Failed to pull '{image}' (attempt {attempt}): {result.stderr.strip()}", level="WARNING")
                print(f"[WARN] Failed to pull '{image}' (attempt {attempt})")
        except Exception as e:
            logger.log(f"Exception pulling '{image}' (attempt {attempt}): {e}", level="ERROR")
            print(f"[ERROR] Exception pulling '{image}' (attempt {attempt}): {e}")
    return False

def main():
    if not os.path.isfile(IMAGES_FILE):
        logger.log(f"images.env file not found at: {IMAGES_FILE}", level="ERROR")
        print(f"[ERROR] images.env file not found at: {IMAGES_FILE}")
        sys.exit(1)
    images = read_images(IMAGES_FILE)
    if not images:
        logger.log("No images found in images.env.", level="ERROR")
        print("[ERROR] No images found in images.env.")
        sys.exit(1)
    logger.log("Pull order:", level="INFO")
    print("[INFO] Pull order:")
    for img in images:
        logger.log(f"  {img}", level="INFO")
        print(f"  {img}")
    print("-------------------------------------------")
    logger.log("-------------------------------------------", level="INFO")
    log_dir = ensure_log_dir()
    failed_log_path = os.path.join(log_dir, "failed_images.log")
    failed_images = []
    for image in images:
        if not pull_image(image):
            failed_images.append(image)
            logger.log(f"Failed to pull '{image}' after 3 attempts.", level="ERROR")
            print(f"[ERROR] Failed to pull '{image}' after 3 attempts.")
    with open(failed_log_path, 'w', encoding='utf-8') as f:
        for img in failed_images:
            f.write(img + '\n')
    total = len(images)
    success = total - len(failed_images)
    print("-------------------------------------------")
    print(f"Image Pull Summary:\n  - Success: {success} / {total}\n  - Failed:  {len(failed_images)} / {total}")
    logger.log(f"Image Pull Summary: Success: {success} / {total}, Failed: {len(failed_images)} / {total}", level="INFO")
    print("-------------------------------------------")
    if failed_images:
        print(f"[ERROR] Some images failed to pull. Check the log for details: {failed_log_path}")
        logger.log(f"Some images failed to pull. See: {failed_log_path}", level="ERROR")
        sys.exit(1)
    else:
        print("[SUCCESS] All configured images were pulled successfully.")
        logger.log("All configured images were pulled successfully.", level="SUCCESS")
        sys.exit(0)

if __name__ == "__main__":
    main() 