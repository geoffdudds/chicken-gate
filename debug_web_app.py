#!/usr/bin/env python3
"""
Debug web app status reading
"""

import os
import json
from datetime import datetime

def debug_web_app():
    print("🔍 Debugging web app status reading...")

    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")

    # Check if status file exists
    status_file = "gate_status.json"
    print(f"Looking for file: {status_file}")
    print(f"File exists: {os.path.exists(status_file)}")

    if os.path.exists(status_file):
        # Check file permissions
        stat = os.stat(status_file)
        print(f"File permissions: {oct(stat.st_mode)}")
        print(f"File owner: {stat.st_uid}")
        print(f"File size: {stat.st_size} bytes")

        # Try to read the file
        try:
            with open(status_file, 'r') as f:
                data = json.load(f)
            print("✅ File read successfully")
            print("Keys found:", list(data.keys()))

            # Test the web app function
            from web_app import read_gate_status
            status = read_gate_status()
            print("✅ Web app read_gate_status() works")
            print("Position from web app:", status.get('position', 'MISSING'))

        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print("❌ Status file not found")
        print("Files in current directory:")
        for f in os.listdir('.'):
            if f.endswith('.json'):
                print(f"  {f}")

if __name__ == "__main__":
    debug_web_app()
