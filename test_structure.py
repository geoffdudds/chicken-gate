#!/usr/bin/env python3
"""
Test script to verify the new project structure imports work correctly.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        print("Testing shared module imports...")
        import chicken_gate.shared.config
        import chicken_gate.shared.timer
        print("✓ Shared modules imported successfully")

        print("Testing web module imports...")
        import chicken_gate.web.app
        print("✓ Web modules imported successfully")

        print("Testing gate module imports (may fail on non-Pi systems)...")
        try:
            import chicken_gate.gate.main
            print("✓ Gate modules imported successfully")
        except ImportError as e:
            if "RPi" in str(e):
                print("⚠ Gate modules require RPi.GPIO (expected on non-Pi systems)")
            else:
                print(f"✗ Unexpected import error: {e}")

        print("\nProject structure test completed!")

    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
