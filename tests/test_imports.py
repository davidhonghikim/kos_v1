#!/usr/bin/env python3
"""Test imports for kos_v1"""

try:
    import fastapi
    print("✓ FastAPI imported successfully")
except ImportError as e:
    print(f"✗ FastAPI import failed: {e}")

try:
    import aiohttp
    print("✓ aiohttp imported successfully")
except ImportError as e:
    print(f"✗ aiohttp import failed: {e}")

try:
    import openai
    print("✓ openai imported successfully")
except ImportError as e:
    print(f"✗ openai import failed: {e}")

try:
    import pydantic
    print("✓ pydantic imported successfully")
except ImportError as e:
    print(f"✗ pydantic import failed: {e}")

print("\nImport test completed!") 