#!/usr/bin/env python3
"""
Workaround for gpiozero importlib.metadata issue on Python 3.7
"""

import sys
import os

def fix_importlib_metadata():
    """Create a compatibility shim for importlib.metadata"""

    print("🔧 Applying importlib.metadata workaround for Python 3.7...")

    # Check if we already have importlib_metadata
    try:
        import importlib_metadata
        print("✅ importlib_metadata package found")

        # Create the compatibility module
        import importlib

        # Add metadata as an attribute to importlib
        importlib.metadata = importlib_metadata

        print("✅ Created importlib.metadata compatibility layer")
        return True

    except ImportError:
        print("❌ importlib_metadata package not found")
        print("   Run: pip3 install importlib-metadata")
        return False

def test_gpiozero():
    """Test if gpiozero works with the fix"""
    try:
        print("🧪 Testing gpiozero import...")
        import gpiozero
        print("✅ gpiozero imported successfully!")
        print(f"   Version: {gpiozero.__version__}")
        return True
    except Exception as e:
        print(f"❌ gpiozero import failed: {e}")
        return False

def main():
    print("🔧 gpiozero Compatibility Fix for Python 3.7")
    print("=" * 50)

    # Apply the fix
    if fix_importlib_metadata():
        # Test if it works
        if test_gpiozero():
            print("\n✅ Fix successful! You should now be able to run your gate system.")
        else:
            print("\n❌ Fix didn't work. There might be other issues.")
    else:
        print("\n❌ Fix failed. Install importlib-metadata first.")

if __name__ == "__main__":
    main()
