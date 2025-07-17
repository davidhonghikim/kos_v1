import os

def parse_env_file(filepath):
    env = {}
    if not os.path.exists(filepath):
        return env
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

def validate_env_vars(env, required_keys=None):
    """Validate that all required keys are present in the env dict."""
    if required_keys is None:
        return True, []
    missing = [k for k in required_keys if k not in env]
    return len(missing) == 0, missing 