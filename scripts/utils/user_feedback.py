import sys

def user_info(msg):
    print(f"[INFO] {msg}")

def user_warning(msg):
    print(f"[WARNING] {msg}", file=sys.stderr)

def user_error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)

def user_success(msg):
    print(f"[SUCCESS] {msg}") 