import os
import sys
from datetime import datetime

# Ensure scripts/ and scripts/utils are in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
SCRIPTS_PATH = os.path.join(PROJECT_ROOT, 'scripts')
UTILS_PATH = os.path.join(SCRIPTS_PATH, 'utils')
if SCRIPTS_PATH not in sys.path:
    sys.path.insert(0, SCRIPTS_PATH)
if UTILS_PATH not in sys.path:
    sys.path.insert(0, UTILS_PATH)

from hardware_utils import detect_nvidia_gpus, detect_amd_gpus, detect_intel_gpus, detect_apple_m_series  # type: ignore
from env_utils import parse_env_file  # type: ignore
from user_feedback import user_info, user_warning, user_error, user_success  # type: ignore
import re

now = datetime.now()
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs', f'{now.year:04d}', f'{now.month:02d}', 'gpu_autodetect.log'))

def log(msg):
    timestamp = datetime.now().isoformat()
    log_dir = os.path.dirname(LOG_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")
    user_info(msg)

def resolve_var(val, env):
    # Resolve ${VAR} in val using env dict
    pattern = re.compile(r'\$\{([^}]+)\}')
    while True:
        match = pattern.search(val)
        if not match:
            break
        var = match.group(1)
        val = val.replace(f'${{{var}}}', env.get(var, ''))
    return val

def write_gpu_env(env_path, nvidia_gpus, amd_gpus, intel_gpus, apple_gpus, extra_env):
    # Parse all image variables from extra_env and local assignments
    image_vars = {}
    for k, v in extra_env.items():
        if k.endswith('GPU_IMAGE'):
            image_vars[k] = v
    # Add local assignments from this script (if any)
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip()
            if k.endswith('GPU_IMAGE'):
                image_vars[k] = v
    # Build list of images to pull based on detected GPUs
    images_to_pull = []
    # NVIDIA
    if nvidia_gpus:
        # Assign LLM to GPU 0, media gen to GPU 1 if more than 1, else both to 0
        llm_image = resolve_var(image_vars.get('KOS_NVIDIA_GPU_IMAGE', ''), image_vars)
        if llm_image and llm_image not in images_to_pull:
            images_to_pull.append(llm_image)
        if len(nvidia_gpus) > 1:
            media_image = resolve_var(image_vars.get('KOS_NVIDIA_GPU_OLD_IMAGE', ''), image_vars)
            if media_image and media_image not in images_to_pull:
                images_to_pull.append(media_image)
        else:
            # Only one GPU, assign both to same image
            if llm_image and llm_image not in images_to_pull:
                images_to_pull.append(llm_image)
    # AMD
    if amd_gpus:
        amd_image = resolve_var(image_vars.get('KOS_AMD_GPU_IMAGE', ''), image_vars)
        if amd_image and amd_image not in images_to_pull:
            images_to_pull.append(amd_image)
    # INTEL
    if intel_gpus:
        intel_image = resolve_var(image_vars.get('KOS_INTEL_GPU_IMAGE', ''), image_vars)
        if intel_image and intel_image not in images_to_pull:
            images_to_pull.append(intel_image)
    # APPLE
    if apple_gpus:
        apple_image = resolve_var(image_vars.get('KOS_APPLE_GPU_IMAGE', ''), image_vars)
        if apple_image and apple_image not in images_to_pull:
            images_to_pull.append(apple_image)
    # Write all original variables and new KOS_GPU_IMAGES_TO_PULL
    with open(env_path, 'r') as f:
        original_lines = f.readlines()
    with open(env_path, 'w') as f:
        for line in original_lines:
            f.write(line)
        f.write(f'KOS_GPU_IMAGES_TO_PULL={" ,".join(images_to_pull)}\n')

def write_ai_ml_env(env_path, nvidia_gpus, amd_gpus, intel_gpus, apple_gpus):
    with open(env_path, 'w') as f:
        if nvidia_gpus:
            f.write('AI_ML_BACKEND=CUDA\n')
        elif amd_gpus:
            f.write('AI_ML_BACKEND=ROCM\n')
        elif intel_gpus:
            f.write('AI_ML_BACKEND=INTEL\n')
        elif apple_gpus:
            f.write('AI_ML_BACKEND=APPLE\n')
        else:
            f.write('AI_ML_BACKEND=CPU\n')

def main():
    env_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'env'))
    if not os.path.exists(env_dir):
        os.makedirs(env_dir, exist_ok=True)
    gpu_env_path = os.path.join(env_dir, 'gpu.env')
    ai_ml_env_path = os.path.join(env_dir, 'ai-ml.env')
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    log("Starting GPU autodetection...")
    nvidia_gpus = detect_nvidia_gpus()
    amd_gpus = detect_amd_gpus()
    intel_gpus = detect_intel_gpus()
    apple_gpus = detect_apple_m_series()
    ports_env = parse_env_file(os.path.join(env_dir, 'ports.env'))
    settings_env = parse_env_file(os.path.join(env_dir, 'settings.env'))
    extra_env = {}
    for k in ports_env:
        if 'IMAGE' in k or 'TORCH' in k or 'RESTART_POLICY' in k:
            extra_env[k] = ports_env[k]
    for k in settings_env:
        if 'IMAGE' in k or 'TORCH' in k or 'RESTART_POLICY' in k:
            extra_env[k] = settings_env[k]
    write_gpu_env(gpu_env_path, nvidia_gpus, amd_gpus, intel_gpus, apple_gpus, extra_env)
    write_ai_ml_env(ai_ml_env_path, nvidia_gpus, amd_gpus, intel_gpus, apple_gpus)
    log(f"Wrote {gpu_env_path} and {ai_ml_env_path} with detection results and extra image info from env files.")
    if not (nvidia_gpus or amd_gpus or intel_gpus or apple_gpus):
        log("No supported GPU detected. All GPU features will be disabled.")
    else:
        log("GPU autodetection complete. System is ready for GPU-accelerated workloads.")

if __name__ == '__main__':
    main() 