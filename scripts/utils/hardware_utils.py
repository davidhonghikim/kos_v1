import platform
import subprocess

def detect_nvidia_gpus():
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
            return gpus
    except Exception:
        pass
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
                return gpus
        except Exception:
            pass
    # Fallback: Linux lspci
    if platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            nvidia_gpus = [l for l in lines if 'nvidia' in l.lower()]
            if nvidia_gpus:
                gpus = [{'name': 'NVIDIA GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(nvidia_gpus)]
                return gpus
        except Exception:
            pass
    return []

def detect_amd_gpus():
    try:
        result = subprocess.run(['rocm-smi', '-i'], capture_output=True, text=True, check=True)
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        amd_gpus = [l for l in lines if l.startswith('GPU')]
        if amd_gpus:
            gpus = [{'name': 'AMD GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(amd_gpus)]
            return gpus
    except Exception:
        pass
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
                return gpus
        except Exception:
            pass
    if platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            amd_gpus = [l for l in lines if 'amd' in l.lower() or 'radeon' in l.lower()]
            if amd_gpus:
                gpus = [{'name': 'AMD GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(amd_gpus)]
                return gpus
        except Exception:
            pass
    return []

def detect_intel_gpus():
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
                return gpus
        except Exception:
            pass
    if platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            intel_gpus = [l for l in lines if 'intel' in l.lower()]
            if intel_gpus:
                gpus = [{'name': 'Intel GPU', 'index': str(i), 'uuid': f'unknown-{i}'} for i, _ in enumerate(intel_gpus)]
                return gpus
        except Exception:
            pass
    return []

def detect_apple_m_series():
    if platform.system() == 'Darwin':
        try:
            result = subprocess.run(['sysctl', 'machdep.cpu.brand_string'], capture_output=True, text=True, check=True)
            if 'Apple' in result.stdout:
                return [{'name': 'Apple M Series', 'index': '0', 'uuid': 'unknown-0'}]
        except Exception:
            pass
    return [] 