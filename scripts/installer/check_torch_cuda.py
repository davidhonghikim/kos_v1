import sys
import subprocess
import os

CUDA_PIP_CMD = [
    sys.executable, '-m', 'pip', 'install',
    'torch==2.1.2', 'torchvision==0.16.2', 'torchaudio==2.1.2',
    '--index-url', 'https://download.pytorch.org/whl/cu118'
]

def has_nvidia_gpu():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True, text=True, check=True)
        gpus = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        return len(gpus) > 0, gpus
    except Exception:
        return False, []

def check_torch_cuda():
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0
        device_names = [torch.cuda.get_device_name(i) for i in range(device_count)] if cuda_available else []
        return cuda_available, device_count, device_names
    except ImportError:
        print('[FATAL] torch is not installed in this environment.')
        sys.exit(1)

def main():
    gpu_present, gpu_names = has_nvidia_gpu()
    cuda_available, device_count, device_names = check_torch_cuda()
    if gpu_present:
        print(f'[INFO] Detected NVIDIA GPU(s): {gpu_names}')
        if cuda_available:
            print(f'[SUCCESS] torch with CUDA support is available. Devices: {device_names}')
            sys.exit(0)
        else:
            print('[WARNING] NVIDIA GPU detected, but torch is not CUDA-enabled!')
            print('Attempting to auto-install CUDA-enabled torch...')
            result = subprocess.run(CUDA_PIP_CMD)
            if result.returncode != 0:
                print('[FATAL] Auto-install of CUDA-enabled torch failed. Please install manually:')
                print('  pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118')
                sys.exit(1)
            # Re-check after install
            cuda_available, device_count, device_names = check_torch_cuda()
            if cuda_available:
                print(f'[SUCCESS] torch with CUDA support is now available. Devices: {device_names}')
                sys.exit(0)
            else:
                print('[FATAL] torch is still not CUDA-enabled after auto-install. Please check your environment.')
                sys.exit(1)
    else:
        if cuda_available:
            print('[WARNING] torch reports CUDA available, but no NVIDIA GPU detected.')
        else:
            print('[INFO] No NVIDIA GPU detected. Running in CPU mode.')
        sys.exit(0)

if __name__ == '__main__':
    main() 