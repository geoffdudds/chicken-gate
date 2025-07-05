#!/usr/bin/env python3
"""
Test STOP command processing
"""

import os
import time
import json

def test_stop_command():
    print("🧪 Testing STOP command processing...")

    # Test 1: Create command file manually
    print("📝 Test 1: Creating STOP command file...")
    with open("gate_cmd.txt", "w") as f:
        f.write("STOP")
    print("✅ Created gate_cmd.txt with STOP command")

    # Wait and check if it gets consumed
    print("⏳ Waiting 5 seconds for command to be processed...")
    time.sleep(5)

    if os.path.exists("gate_cmd.txt"):
        print("❌ Command file still exists - not being processed")
        with open("gate_cmd.txt", "r") as f:
            content = f.read()
        print(f"   File content: '{content}'")
    else:
        print("✅ Command file was consumed")

    # Test 2: Check current status
    print("\n📊 Test 2: Checking current gate status...")
    if os.path.exists("gate_status.json"):
        with open("gate_status.json", "r") as f:
            status = json.load(f)

        print("Current status:")
        print(f"  Position: {status.get('position', 'MISSING')}")
        print(f"  Target position: {status.get('target_position', 'MISSING')}")
        print(f"  Is moving: {status.get('is_moving', 'MISSING')}")
        print(f"  Diagnostics: {status.get('diagnostic_messages', [])[-3:]}")  # Last 3 messages
    else:
        print("❌ No status file found")

    # Test 3: Web API command
    print("\n🌐 Test 3: Testing web API...")
    print("Run this command manually:")
    print("curl -X POST -H 'Content-Type: application/json' -d '{\"command\":\"STOP\"}' http://localhost:5000/api/command")

if __name__ == "__main__":
    test_stop_command()
