#!/usr/bin/env python3
"""
compose_gpu_assignment.py
Handles GPU assignment logic for Docker Compose generation.
"""
def assign_gpus_to_services(env_vars, service_names):
    """Assign GPUs to enabled services based on env_vars and hardware detection."""
    assignments = {}
    gpu_enable = env_vars.get('KOS_GPU_ENABLE', '').lower() == 'true'
    nvidia_enable = env_vars.get('KOS_NVIDIA_GPU_ENABLE', '').lower() == 'true'
    amd_enable = env_vars.get('KOS_AMD_GPU_ENABLE', '').lower() == 'true'
    intel_enable = env_vars.get('KOS_INTEL_GPU_ENABLE', '').lower() == 'true'
    apple_enable = env_vars.get('KOS_APPLE_GPU_ENABLE', '').lower() == 'true'
    # Example: assign all GPUs to all AI/ML services if enabled
    ai_ml_services = ['automatic1111', 'comfyui', 'invokeai', 'huggingface']
    for svc in service_names:
        if svc in ai_ml_services and gpu_enable:
            assignments[svc] = {
                'gpu': True,
                'nvidia': nvidia_enable,
                'amd': amd_enable,
                'intel': intel_enable,
                'apple': apple_enable
            }
        else:
            assignments[svc] = {'gpu': False}
    return assignments

if __name__ == "__main__":
    from compose_env_loader import load_env_vars
    from compose_service_config import get_enabled_services
    env_vars = load_env_vars()
    enabled = get_enabled_services(env_vars)
    print(assign_gpus_to_services(env_vars, enabled)) 