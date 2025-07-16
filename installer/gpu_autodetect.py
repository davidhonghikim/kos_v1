import os
import subprocess
import platform
import sys
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'gpu_autodetect.log')

def log(msg):
    timestamp = datetime.now().isoformat()
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[gpu_autodetect] {msg}")

def detect_nvidia_gpus():
    # Try nvidia-smi first
    try:
        result = subprocess.run([
            'nvidia-smi',
            '--query-gpu=name,index,uuid',
            '--format=csv,noheader'
        ], capture_output=True, text=True, check=True)
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        if lines:
            gpus = []
            for line in lines:
                name, index, uuid = [x.strip() for x in line.split(',')]
                gpus.append({'name': name, 'index': index, 'uuid': uuid})
            log(f"Detected {len(gpus)} NVIDIA GPU(s) via nvidia-smi: {[g['name'] for g in gpus]}")
            return gpus
    except Exception:
        log("nvidia-smi not available or failed. Trying fallback detection for NVIDIA GPUs.")
    # Fallback: Windows wmic
    if platform.system() == 'Windows':
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True, text=True, check=True
            )
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            nvidia_gpus = [l for l in lines if 'nvidia' in l.lower()]
            if nvidia_gpus:
                gpus = [{'name': name, 'index': str(i), 'uuid': f'unknown-{i}'} for i, name in enumerate(nvidia_gpus)]
                log(f"Detected {len(gpus)} NVIDIA GPU(s) via wmic: {nvidia_gpus}")
                return gpus
        except Exception:
            log("WMIC fallback failed for NVIDIA GPUs.")
    # Fallback: Linux lspci
    if platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            nvidia_gpus = [l for l in lines if 'nvidia' in l.lower()]
            if nvidia_gpus:
                gpus = [{'name': 'NVIDIA GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(nvidia_gpus)]
                log(f"Detected {len(gpus)} NVIDIA GPU(s) via lspci.")
                return gpus
        except Exception:
            log("lspci fallback failed for NVIDIA GPUs.")
    return []

def detect_amd_gpus():
    # Try rocm-smi first
    try:
        result = subprocess.run(['rocm-smi', '-i'], capture_output=True, text=True, check=True)
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        amd_gpus = [l for l in lines if l.startswith('GPU')]
        if amd_gpus:
            gpus = [{'name': 'AMD GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(amd_gpus)]
            log(f"Detected {len(gpus)} AMD GPU(s) via rocm-smi.")
            return gpus
    except Exception:
        log("rocm-smi not available or failed. Trying fallback detection for AMD GPUs.")
    # Fallback: Windows wmic
    if platform.system() == 'Windows':
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True, text=True, check=True
            )
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            amd_gpus = [l for l in lines if 'amd' in l.lower() or 'radeon' in l.lower()]
            if amd_gpus:
                gpus = [{'name': name, 'index': str(i), 'uuid': f'unknown-{i}'} for i, name in enumerate(amd_gpus)]
                log(f"Detected {len(gpus)} AMD GPU(s) via wmic: {amd_gpus}")
                return gpus
        except Exception:
            log("WMIC fallback failed for AMD GPUs.")
    # Fallback: Linux lspci
    if platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            amd_gpus = [l for l in lines if 'amd' in l.lower() or 'radeon' in l.lower()]
            if amd_gpus:
                gpus = [{'name': 'AMD GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(amd_gpus)]
                log(f"Detected {len(gpus)} AMD GPU(s) via lspci.")
                return gpus
        except Exception:
            log("lspci fallback failed for AMD GPUs.")
    return []

def detect_intel_gpus():
    # Windows wmic
    if platform.system() == 'Windows':
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True, text=True, check=True
            )
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            intel_gpus = [l for l in lines if 'intel' in l.lower()]
            if intel_gpus:
                gpus = [{'name': name, 'index': str(i), 'uuid': f'unknown-{i}'} for i, name in enumerate(intel_gpus)]
                log(f"Detected {len(gpus)} Intel GPU(s) via wmic: {intel_gpus}")
                return gpus
        except Exception:
            log("WMIC failed for Intel GPUs.")
    # Linux lspci
    if platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            intel_gpus = [l for l in lines if 'intel' in l.lower()]
            if intel_gpus:
                gpus = [{'name': 'Intel GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(intel_gpus)]
                log(f"Detected {len(gpus)} Intel GPU(s) via lspci.")
                return gpus
        except Exception:
            log("lspci failed for Intel GPUs.")
    return []

def detect_apple_m_series():
    if platform.system() == 'Darwin':
        try:
            result = subprocess.run(['sysctl', 'machdep.cpu.brand_string'], capture_output=True, text=True, check=True)
            if 'Apple' in result.stdout:
                log("Detected Apple Silicon (M series) via sysctl.")
                return [{'name': 'Apple M Series', 'index': '0', 'uuid': 'unknown-0'}]
        except Exception:
            log("sysctl failed for Apple Silicon detection.")
    return []

def check_cuda_support():
    try:
        import torch
        if torch.cuda.is_available():
            log("CUDA support: Available (torch.cuda.is_available() == True)")
            return True
        else:
            log("CUDA support: Not available (torch.cuda.is_available() == False)")
    except Exception as e:
        log(f"CUDA support: Not available (torch not importable: {e})")
    return False

def check_rocm_support():
    try:
        import torch
        if hasattr(torch.version, 'hip') and torch.version.hip:
            log("ROCm support: Available (torch.version.hip present)")
            return True
        else:
            log("ROCm support: Not available (torch.version.hip not present)")
    except Exception as e:
        log(f"ROCm support: Not available (torch not importable: {e})")
    return False

def check_metal_support():
    if platform.system() == 'Darwin':
        try:
            import torch
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                log("Metal support: Available (torch.backends.mps.is_available() == True)")
                return True
            else:
                log("Metal support: Not available (torch.backends.mps.is_available() == False)")
        except Exception as e:
            log(f"Metal support: Not available (torch not importable: {e})")
    return False

def write_gpu_env(env_path, nvidia_gpus, amd_gpus, intel_gpus, apple_gpus, cuda_ok, rocm_ok, metal_ok):
    with open(env_path, 'w') as f:
        # General flags
        any_gpu = bool(nvidia_gpus or amd_gpus or intel_gpus or apple_gpus)
        f.write(f'KOS_GPU_ENABLE={str(any_gpu).lower()}\n')
        f.write(f'KOS_NVIDIA_GPU_ENABLE={str(bool(nvidia_gpus)).lower()}\n')
        f.write(f'KOS_AMD_GPU_ENABLE={str(bool(amd_gpus)).lower()}\n')
        f.write(f'KOS_INTEL_GPU_ENABLE={str(bool(intel_gpus)).lower()}\n')
        f.write(f'KOS_APPLE_GPU_ENABLE={str(bool(apple_gpus)).lower()}\n')
        f.write(f'KOS_GPU_COMPUTE_SUPPORTED={str(cuda_ok or rocm_ok or metal_ok).lower()}\n')
        # Device details
        if nvidia_gpus:
            names = ','.join(g['name'] for g in nvidia_gpus)
            uuids = ','.join(g['uuid'] for g in nvidia_gpus)
            indices = ','.join(g['index'] for g in nvidia_gpus)
            f.write(f'KOS_GPU_NAMES={names}\n')
            f.write(f'KOS_GPU_UUIDS={uuids}\n')
            f.write(f'CUDA_VISIBLE_DEVICES={indices}\n')
            f.write('KOS_CUDA_IMAGE=nvidia/cuda:12.2.0-base\n')
        if amd_gpus:
            names = ','.join(g['name'] for g in amd_gpus)
            f.write(f'KOS_GPU_NAMES={names}\n')
            f.write('KOS_ROCM_IMAGE=rocm/rocm-terminal:latest\n')
        if apple_gpus:
            f.write('KOS_METAL_IMAGE=apple/metal-base:latest\n')
        # Add more as needed

def main():
    env_dir = os.path.join(os.path.dirname(__file__), '..', 'env')
    env_path = os.path.abspath(os.path.join(env_dir, 'gpu.env'))
    # Clear previous log
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    log("Starting GPU autodetection...")
    nvidia_gpus = detect_nvidia_gpus()
    amd_gpus = detect_amd_gpus()
    intel_gpus = detect_intel_gpus()
    apple_gpus = detect_apple_m_series()
    cuda_ok = check_cuda_support() if nvidia_gpus else False
    rocm_ok = check_rocm_support() if amd_gpus else False
    metal_ok = check_metal_support() if apple_gpus else False
    write_gpu_env(env_path, nvidia_gpus, amd_gpus, intel_gpus, apple_gpus, cuda_ok, rocm_ok, metal_ok)
    log(f"Wrote {env_path} with detection results.")
    if not (nvidia_gpus or amd_gpus or intel_gpus or apple_gpus):
        log("No supported GPU detected. All GPU features will be disabled.")
    elif not (cuda_ok or rocm_ok or metal_ok):
        log("WARNING: GPU(s) detected but no supported compute backend available. ML/AI workloads may not function.")
    else:
        log("GPU autodetection complete. System is ready for GPU-accelerated workloads.")

if __name__ == '__main__':
    main() 