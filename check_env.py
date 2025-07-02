#!/usr/bin/env python3
"""
Check what Python packages are installed and where
"""

import sys
import subprocess

def check_python_info():
    print("🔍 Python Environment Diagnostics")
    print("=" * 50)
    
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    print()
    
    # Check if importlib_metadata is installed
    try:
        import importlib_metadata
        print("✅ importlib_metadata is available")
        try:
            print(f"   Version: {importlib_metadata.version('importlib_metadata')}")
        except:
            print("   Version: (version info not available)")
        print(f"   Location: {importlib_metadata.__file__}")
    except ImportError:
        print("❌ importlib_metadata is NOT available")
    
    # Try alternative import
    try:
        from importlib import metadata
        print("✅ importlib.metadata is available (built-in)")
    except ImportError:
        print("❌ importlib.metadata is NOT available")
    
    print()
    
    # Check gpiozero installation
    try:
        import gpiozero
        print("✅ gpiozero is available")
        print(f"   Version: {gpiozero.__version__}")
        print(f"   Location: {gpiozero.__file__}")
    except ImportError as e:
        print(f"❌ gpiozero import failed: {e}")
    
    print()
    
    # Show pip list
    print("📦 Installed packages:")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if any(pkg in line.lower() for pkg in ['gpiozero', 'importlib', 'metadata']):
                print(f"   {line}")
    except Exception as e:
        print(f"   Error getting pip list: {e}")

if __name__ == "__main__":
    check_python_info()
