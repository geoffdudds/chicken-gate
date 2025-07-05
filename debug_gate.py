#!/usr/bin/env python3
"""
Debug script to run the gate process directly and see any errors.
"""

import sys
import os

def main():
    print("🔧 Starting gate control process directly for debugging...")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('src/main.py'):
        print("Error: Please run this script from the chicken-gate directory")
        print(f"Current directory: {os.getcwd()}")
        print("Expected to find: src/main.py")
        sys.exit(1)

    # Change to src directory and run main.py
    try:
        os.chdir('src')
        print(f"Changed to directory: {os.getcwd()}")
        print("Running main.py...")
        print("-" * 30)

        # Import and run main
        import main
        main.main()

    except Exception as e:
        print(f"❌ Error running gate process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
