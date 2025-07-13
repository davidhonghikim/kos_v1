#!/usr/bin/env python3
"""Test backend imports and basic functionality"""

try:
    from backend.main import app
    print("✓ Backend imports successfully!")
    
    # Test basic app properties
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")
    print(f"✓ App description: {app.description}")
    
except ImportError as e:
    print(f"✗ Backend import failed: {e}")
except Exception as e:
    print(f"✗ Backend error: {e}")

print("\nBackend test completed!") 