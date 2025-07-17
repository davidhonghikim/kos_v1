import os
import sys
from datetime import datetime
import re
import configparser
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.utils.logger import get_logger
from scripts.utils.hardware_utils import detect_nvidia_gpus, detect_amd_gpus, detect_intel_gpus, detect_apple_m_series
from scripts.utils.env_utils import parse_env_file
from scripts.utils.user_feedback import user_info, user_warning, user_error, user_success

logger = get_logger('gpu_autodetect', log_mode='per_run')
GPU_ENV_PATH = os.path.join(PROJECT_ROOT, 'env', 'gpu.env')

# Helper to preserve the top section of gpu.env
def read_gpu_env_sections(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    split_idx = 0
    for i, line in enumerate(lines):
        if re.match(r'^KOS_(NVIDIA|AMD|INTEL|APPLE)[0-9]+_GPU_', line):
            split_idx = i
            break
    return lines[:split_idx], lines[split_idx:]

def write_gpu_env(top_lines, gpu_vars):
    with open(GPU_ENV_PATH, 'w', encoding='utf-8') as f:
        for line in top_lines:
            f.write(line)
        for var, val in gpu_vars.items():
            f.write(f'{var}={val}\n')

def resolve_env_var(var_name, env_path=GPU_ENV_PATH):
    # Parse the env file and return the value for var_name
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith(f'{var_name}='):
                val = line.strip().split('=', 1)[1].strip()
                # If value is a variable reference, resolve recursively
                if val.startswith('${') and val.endswith('}'):
                    ref = val[2:-1]
                    return resolve_env_var(ref, env_path)
                return val
    return ''

def main():
    top_lines, _ = read_gpu_env_sections(GPU_ENV_PATH)
    gpu_vars = {}
    nvidia_gpus = detect_nvidia_gpus()
    amd_gpus = detect_amd_gpus()
    intel_gpus = detect_intel_gpus()
    apple_gpus = detect_apple_m_series()
    generic_set = False
    # NVIDIA GPUs (write both old and new image variables)
    nvidia_old_img_val = resolve_env_var('KOS_NVIDIA_GPU_OLD_IMAGE')
    nvidia_new_img_val = resolve_env_var('KOS_NVIDIA_GPU_IMAGE')
    for idx, gpu in enumerate(nvidia_gpus, 1):
        prefix = f'KOS_NVIDIA{idx}_GPU'
        new_prefix = f'KOS_NVIDIA{idx}_NEW_GPU'
        gpu_vars[f'{prefix}_NAMES'] = gpu.get('name', f'NVIDIA_GPU_{idx}')
        gpu_vars[f'{prefix}_UUIDS'] = gpu.get('uuid', f'UUID_{idx}')
        gpu_vars[f'{prefix}_CONTAINER_NAME'] = f'kos-nvidia{idx}-gpu-old'
        gpu_vars[f'{prefix}_IMAGE'] = nvidia_old_img_val
        gpu_vars[f'{prefix}_EXTERNAL_PORT'] = str(49000 + idx - 1)
        gpu_vars[f'{prefix}_INTERNAL_PORT'] = str(49000 + idx - 1)
        gpu_vars[f'{prefix}_NETWORK'] = 'kos-network'
        gpu_vars[f'{prefix}_RESTART_POLICY'] = 'unless-stopped'
        # New image variables
        gpu_vars[f'{new_prefix}_CONTAINER_NAME'] = f'kos-nvidia{idx}-gpu-new'
        gpu_vars[f'{new_prefix}_IMAGE'] = nvidia_new_img_val
        gpu_vars[f'{new_prefix}_EXTERNAL_PORT'] = str(49500 + idx - 1)
        gpu_vars[f'{new_prefix}_INTERNAL_PORT'] = str(49500 + idx - 1)
        gpu_vars[f'{new_prefix}_NETWORK'] = 'kos-network'
        gpu_vars[f'{new_prefix}_RESTART_POLICY'] = 'unless-stopped'
        gpu_vars['CUDA_VISIBLE_DEVICES'] = ','.join(str(i) for i in range(len(nvidia_gpus)))
        if idx == 1:
            # Summary variables for old image
            gpu_vars['KOS_NVIDIA_GPU_CONTAINER_NAME'] = f'kos-nvidia1-gpu-old'
            gpu_vars['KOS_NVIDIA_GPU_IMAGE'] = nvidia_old_img_val
            gpu_vars['KOS_NVIDIA_GPU_EXTERNAL_PORT'] = str(49000)
            gpu_vars['KOS_NVIDIA_GPU_INTERNAL_PORT'] = str(49000)
            gpu_vars['KOS_NVIDIA_GPU_NETWORK'] = 'kos-network'
            gpu_vars['KOS_NVIDIA_GPU_RESTART_POLICY'] = 'unless-stopped'
            # Summary variables for new image
            gpu_vars['KOS_NVIDIA_NEW_GPU_CONTAINER_NAME'] = f'kos-nvidia1-gpu-new'
            gpu_vars['KOS_NVIDIA_NEW_GPU_IMAGE'] = nvidia_new_img_val
            gpu_vars['KOS_NVIDIA_NEW_GPU_EXTERNAL_PORT'] = str(49500)
            gpu_vars['KOS_NVIDIA_NEW_GPU_INTERNAL_PORT'] = str(49500)
            gpu_vars['KOS_NVIDIA_NEW_GPU_NETWORK'] = 'kos-network'
            gpu_vars['KOS_NVIDIA_NEW_GPU_RESTART_POLICY'] = 'unless-stopped'
            # Set generic KOS_GPU_* variables if not already set (use new image as default)
            if not generic_set:
                gpu_vars['KOS_GPU_CONTAINER_NAME'] = f'kos-nvidia1-gpu-new'
                gpu_vars['KOS_GPU_IMAGE'] = nvidia_new_img_val
                gpu_vars['KOS_GPU_EXTERNAL_PORT'] = str(49500)
                gpu_vars['KOS_GPU_INTERNAL_PORT'] = str(49500)
                gpu_vars['KOS_GPU_NETWORK'] = 'kos-network'
                gpu_vars['KOS_GPU_RESTART_POLICY'] = 'unless-stopped'
                generic_set = True
    # AMD GPUs
    amd_img_val = resolve_env_var('KOS_AMD_GPU_IMAGE')
    for i, gpu in enumerate(amd_gpus, 1):
        prefix = f'KOS_AMD{i}_GPU'
        gpu_vars[f'{prefix}_NAMES'] = gpu.get('name', f'AMD_GPU_{i}')
        gpu_vars[f'{prefix}_UUIDS'] = gpu.get('uuid', f'AMD_UUID_{i}')
        gpu_vars[f'{prefix}_CONTAINER_NAME'] = f'kos-amd{i}-gpu'
        gpu_vars[f'{prefix}_IMAGE'] = amd_img_val
        gpu_vars[f'{prefix}_EXTERNAL_PORT'] = str(49100 + i - 1)
        gpu_vars[f'{prefix}_INTERNAL_PORT'] = str(49100 + i - 1)
        gpu_vars[f'{prefix}_NETWORK'] = 'kos-network'
        gpu_vars[f'{prefix}_RESTART_POLICY'] = 'unless-stopped'
        if i == 1:
            gpu_vars['KOS_AMD_GPU_CONTAINER_NAME'] = f'kos-amd1-gpu'
            gpu_vars['KOS_AMD_GPU_IMAGE'] = amd_img_val
            gpu_vars['KOS_AMD_GPU_EXTERNAL_PORT'] = str(49100)
            gpu_vars['KOS_AMD_GPU_INTERNAL_PORT'] = str(49100)
            gpu_vars['KOS_AMD_GPU_NETWORK'] = 'kos-network'
            gpu_vars['KOS_AMD_GPU_RESTART_POLICY'] = 'unless-stopped'
            if not generic_set:
                gpu_vars['KOS_GPU_CONTAINER_NAME'] = f'kos-amd1-gpu'
                gpu_vars['KOS_GPU_IMAGE'] = amd_img_val
                gpu_vars['KOS_GPU_EXTERNAL_PORT'] = str(49100)
                gpu_vars['KOS_GPU_INTERNAL_PORT'] = str(49100)
                gpu_vars['KOS_GPU_NETWORK'] = 'kos-network'
                gpu_vars['KOS_GPU_RESTART_POLICY'] = 'unless-stopped'
                generic_set = True
    # Intel GPUs
    intel_img_val = resolve_env_var('KOS_INTEL_GPU_IMAGE')
    for i, gpu in enumerate(intel_gpus, 1):
        prefix = f'KOS_INTEL{i}_GPU'
        gpu_vars[f'{prefix}_NAMES'] = gpu.get('name', f'INTEL_GPU_{i}')
        gpu_vars[f'{prefix}_UUIDS'] = gpu.get('uuid', f'INTEL_UUID_{i}')
        gpu_vars[f'{prefix}_CONTAINER_NAME'] = f'kos-intel{i}-gpu'
        gpu_vars[f'{prefix}_IMAGE'] = intel_img_val
        gpu_vars[f'{prefix}_EXTERNAL_PORT'] = str(49200 + i - 1)
        gpu_vars[f'{prefix}_INTERNAL_PORT'] = str(49200 + i - 1)
        gpu_vars[f'{prefix}_NETWORK'] = 'kos-network'
        gpu_vars[f'{prefix}_RESTART_POLICY'] = 'unless-stopped'
        if i == 1:
            gpu_vars['KOS_INTEL_GPU_CONTAINER_NAME'] = f'kos-intel1-gpu'
            gpu_vars['KOS_INTEL_GPU_IMAGE'] = intel_img_val
            gpu_vars['KOS_INTEL_GPU_EXTERNAL_PORT'] = str(49200)
            gpu_vars['KOS_INTEL_GPU_INTERNAL_PORT'] = str(49200)
            gpu_vars['KOS_INTEL_GPU_NETWORK'] = 'kos-network'
            gpu_vars['KOS_INTEL_GPU_RESTART_POLICY'] = 'unless-stopped'
            if not generic_set:
                gpu_vars['KOS_GPU_CONTAINER_NAME'] = f'kos-intel1-gpu'
                gpu_vars['KOS_GPU_IMAGE'] = intel_img_val
                gpu_vars['KOS_GPU_EXTERNAL_PORT'] = str(49200)
                gpu_vars['KOS_GPU_INTERNAL_PORT'] = str(49200)
                gpu_vars['KOS_GPU_NETWORK'] = 'kos-network'
                gpu_vars['KOS_GPU_RESTART_POLICY'] = 'unless-stopped'
                generic_set = True
    # Apple GPUs
    apple_img_val = resolve_env_var('KOS_APPLE_GPU_IMAGE')
    for i, gpu in enumerate(apple_gpus, 1):
        prefix = f'KOS_APPLE{i}_GPU'
        gpu_vars[f'{prefix}_NAMES'] = gpu.get('name', f'APPLE_GPU_{i}')
        gpu_vars[f'{prefix}_UUIDS'] = gpu.get('uuid', f'APPLE_UUID_{i}')
        gpu_vars[f'{prefix}_CONTAINER_NAME'] = f'kos-apple{i}-gpu'
        gpu_vars[f'{prefix}_IMAGE'] = apple_img_val
        gpu_vars[f'{prefix}_EXTERNAL_PORT'] = str(49300 + i - 1)
        gpu_vars[f'{prefix}_INTERNAL_PORT'] = str(49300 + i - 1)
        gpu_vars[f'{prefix}_NETWORK'] = 'kos-network'
        gpu_vars[f'{prefix}_RESTART_POLICY'] = 'unless-stopped'
        if i == 1:
            gpu_vars['KOS_APPLE_GPU_CONTAINER_NAME'] = f'kos-apple1-gpu'
            gpu_vars['KOS_APPLE_GPU_IMAGE'] = apple_img_val
            gpu_vars['KOS_APPLE_GPU_EXTERNAL_PORT'] = str(49300)
            gpu_vars['KOS_APPLE_GPU_INTERNAL_PORT'] = str(49300)
            gpu_vars['KOS_APPLE_GPU_NETWORK'] = 'kos-network'
            gpu_vars['KOS_APPLE_GPU_RESTART_POLICY'] = 'unless-stopped'
            if not generic_set:
                gpu_vars['KOS_GPU_CONTAINER_NAME'] = f'kos-apple1-gpu'
                gpu_vars['KOS_GPU_IMAGE'] = apple_img_val
                gpu_vars['KOS_GPU_EXTERNAL_PORT'] = str(49300)
                gpu_vars['KOS_GPU_INTERNAL_PORT'] = str(49300)
                gpu_vars['KOS_GPU_NETWORK'] = 'kos-network'
                gpu_vars['KOS_GPU_RESTART_POLICY'] = 'unless-stopped'
                generic_set = True
    # Write enable flags and counts
    gpu_vars['KOS_NVIDIA_GPU_ENABLE'] = str(bool(nvidia_gpus)).lower()
    gpu_vars['KOS_NVIDIA_GPU_COUNT'] = str(len(nvidia_gpus))
    gpu_vars['KOS_AMD_GPU_ENABLE'] = str(bool(amd_gpus)).lower()
    gpu_vars['KOS_AMD_GPU_COUNT'] = str(len(amd_gpus))
    gpu_vars['KOS_INTEL_GPU_ENABLE'] = str(bool(intel_gpus)).lower()
    gpu_vars['KOS_INTEL_GPU_COUNT'] = str(len(intel_gpus))
    gpu_vars['KOS_APPLE_GPU_ENABLE'] = str(bool(apple_gpus)).lower()
    gpu_vars['KOS_APPLE_GPU_COUNT'] = str(len(apple_gpus))

    # Always write summary variables for all GPU types, even if not detected
    if not nvidia_gpus:
        gpu_vars['KOS_NVIDIA_GPU_CONTAINER_NAME'] = ''
        gpu_vars['KOS_NVIDIA_GPU_IMAGE'] = ''
        gpu_vars['KOS_NVIDIA_GPU_EXTERNAL_PORT'] = ''
        gpu_vars['KOS_NVIDIA_GPU_INTERNAL_PORT'] = ''
        gpu_vars['KOS_NVIDIA_GPU_NETWORK'] = ''
        gpu_vars['KOS_NVIDIA_GPU_RESTART_POLICY'] = ''
        gpu_vars['KOS_NVIDIA_NEW_GPU_CONTAINER_NAME'] = ''
        gpu_vars['KOS_NVIDIA_NEW_GPU_IMAGE'] = ''
        gpu_vars['KOS_NVIDIA_NEW_GPU_EXTERNAL_PORT'] = ''
        gpu_vars['KOS_NVIDIA_NEW_GPU_INTERNAL_PORT'] = ''
        gpu_vars['KOS_NVIDIA_NEW_GPU_NETWORK'] = ''
        gpu_vars['KOS_NVIDIA_NEW_GPU_RESTART_POLICY'] = ''
    if not amd_gpus:
        gpu_vars['KOS_AMD_GPU_CONTAINER_NAME'] = ''
        gpu_vars['KOS_AMD_GPU_IMAGE'] = ''
        gpu_vars['KOS_AMD_GPU_EXTERNAL_PORT'] = ''
        gpu_vars['KOS_AMD_GPU_INTERNAL_PORT'] = ''
        gpu_vars['KOS_AMD_GPU_NETWORK'] = ''
        gpu_vars['KOS_AMD_GPU_RESTART_POLICY'] = ''
    if not intel_gpus:
        gpu_vars['KOS_INTEL_GPU_CONTAINER_NAME'] = ''
        gpu_vars['KOS_INTEL_GPU_IMAGE'] = ''
        gpu_vars['KOS_INTEL_GPU_EXTERNAL_PORT'] = ''
        gpu_vars['KOS_INTEL_GPU_INTERNAL_PORT'] = ''
        gpu_vars['KOS_INTEL_GPU_NETWORK'] = ''
        gpu_vars['KOS_INTEL_GPU_RESTART_POLICY'] = ''
    if not apple_gpus:
        gpu_vars['KOS_APPLE_GPU_CONTAINER_NAME'] = ''
        gpu_vars['KOS_APPLE_GPU_IMAGE'] = ''
        gpu_vars['KOS_APPLE_GPU_EXTERNAL_PORT'] = ''
        gpu_vars['KOS_APPLE_GPU_INTERNAL_PORT'] = ''
        gpu_vars['KOS_APPLE_GPU_NETWORK'] = ''
        gpu_vars['KOS_APPLE_GPU_RESTART_POLICY'] = ''

    # Compose images to pull (include only non-empty image variables)
    images_to_pull = []
    if nvidia_gpus:
        if nvidia_new_img_val:
            images_to_pull.append(nvidia_new_img_val)
        if nvidia_old_img_val:
            images_to_pull.append(nvidia_old_img_val)
    if amd_gpus:
        if amd_img_val:
            images_to_pull.append(amd_img_val)
    if intel_gpus:
        if intel_img_val:
            images_to_pull.append(intel_img_val)
    if apple_gpus:
        if apple_img_val:
            images_to_pull.append(apple_img_val)
    if not images_to_pull:
        images_to_pull.append('${KOS_CPU_GPU_IMAGE}')
    gpu_vars['KOS_GPU_IMAGES_TO_PULL'] = ','.join(images_to_pull)
    # Write to gpu.env
    write_gpu_env(top_lines, gpu_vars)
    # Validate required variables (old and new NVIDIA)
    required_vars = [
        'KOS_GPU_CONTAINER_NAME', 'KOS_GPU_IMAGE', 'KOS_GPU_EXTERNAL_PORT', 'KOS_GPU_INTERNAL_PORT', 'KOS_GPU_NETWORK', 'KOS_GPU_RESTART_POLICY',
        'KOS_NVIDIA_GPU_CONTAINER_NAME', 'KOS_NVIDIA_GPU_IMAGE', 'KOS_NVIDIA_GPU_EXTERNAL_PORT', 'KOS_NVIDIA_GPU_INTERNAL_PORT', 'KOS_NVIDIA_GPU_NETWORK', 'KOS_NVIDIA_GPU_RESTART_POLICY',
        'KOS_NVIDIA_NEW_GPU_CONTAINER_NAME', 'KOS_NVIDIA_NEW_GPU_IMAGE', 'KOS_NVIDIA_NEW_GPU_EXTERNAL_PORT', 'KOS_NVIDIA_NEW_GPU_INTERNAL_PORT', 'KOS_NVIDIA_NEW_GPU_NETWORK', 'KOS_NVIDIA_NEW_GPU_RESTART_POLICY',
        'KOS_AMD_GPU_CONTAINER_NAME', 'KOS_AMD_GPU_IMAGE', 'KOS_AMD_GPU_EXTERNAL_PORT', 'KOS_AMD_GPU_INTERNAL_PORT', 'KOS_AMD_GPU_NETWORK', 'KOS_AMD_GPU_RESTART_POLICY',
        'KOS_INTEL_GPU_CONTAINER_NAME', 'KOS_INTEL_GPU_IMAGE', 'KOS_INTEL_GPU_EXTERNAL_PORT', 'KOS_INTEL_GPU_INTERNAL_PORT', 'KOS_INTEL_GPU_NETWORK', 'KOS_INTEL_GPU_RESTART_POLICY',
        'KOS_APPLE_GPU_CONTAINER_NAME', 'KOS_APPLE_GPU_IMAGE', 'KOS_APPLE_GPU_EXTERNAL_PORT', 'KOS_APPLE_GPU_INTERNAL_PORT', 'KOS_APPLE_GPU_NETWORK', 'KOS_APPLE_GPU_RESTART_POLICY',
    ]
    missing = [v for v in required_vars if v not in gpu_vars]
    if missing:
        logger.log(f'Missing required GPU env variables: {missing}', 'ERROR')
        user_error(f'Missing required GPU env variables: {missing}')
        sys.exit(1)
    logger.log('GPU autodetection and env generation complete.', 'SUCCESS')
    user_success('GPU autodetection and env generation complete.')

if __name__ == '__main__':
    main() 