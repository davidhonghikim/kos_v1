import os
from datetime import datetime
from typing import Optional


def find_project_root_with_logs(start_path=None):
    """Search upward from start_path for a 'logs' directory and return its parent as project root."""
    if start_path is None:
        start_path = os.path.abspath(os.getcwd())
    current = start_path
    while True:
        logs_dir = os.path.join(current, 'logs')
        if os.path.isdir(logs_dir):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(os.getcwd())  # fallback

class Logger:
    def __init__(self, script_name: str, log_mode: Optional[str] = None):
        if log_mode is None:
            log_mode = os.environ.get("LOG_MODE", "daily").lower()
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        # Find project root containing /logs
        project_root = find_project_root_with_logs(os.path.abspath(os.path.dirname(__file__)))
        base_dir = os.path.join(project_root, f"logs/{script_name}/{year}/{month}")
        os.makedirs(base_dir, exist_ok=True)
        if log_mode == "per_run":
            filename = f"{script_name}_{now.strftime('%Y-%m-%dT%H-%M-%S')}.log"
        elif log_mode == "monthly":
            filename = f"{script_name}_{now.strftime('%Y-%m')}.log"
        else:  # daily (default)
            filename = f"{script_name}_{now.strftime('%Y-%m-%d')}.log"
        self.log_file = os.path.join(base_dir, filename)
        self.script_name = script_name

    def log(self, msg: str, level: str = "INFO"):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{now} - {self.script_name} - {level} - {msg}"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry + '\n')
        if level in ('ERROR', 'WARNING', 'SUCCESS'):
            print(entry)

def get_logger(script_name: str, log_mode: Optional[str] = None) -> Logger:
    return Logger(script_name, log_mode) 