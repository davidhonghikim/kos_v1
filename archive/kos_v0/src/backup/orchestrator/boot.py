import sys
from src.core.orchestrator.entrypoint import launch

if __name__ == "__main__":
    try:
        sys.exit(launch())
    except Exception as e:
        print(f"[BOOT ERROR] {e}")
        sys.exit(1)
