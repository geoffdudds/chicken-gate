#!/usr/bin/env python3
"""
Test script to verify gate status is being written correctly
"""

import sys
import time
import json
sys.path.insert(0, 'src')

def test_status_writing():
    print("🧪 Testing gate status writing...")

    try:
        # Import the modules
        from gate import Gate
        from gate_drv import Gate_drv
        from schedule import Schedule
        from main import write_gate_status

        print("✅ Modules imported successfully")

        # Create gate objects
        gate = Gate()
        gate_drv = Gate_drv(gate)

        print("✅ Gate objects created")

        # Test the tick and status
        gate_drv.tick()
        status = gate.get_status()

        print("📊 Current status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Test writing status file
        # Create a schedule object
        schedule = Schedule()

        write_gate_status(gate, schedule)

        print("✅ Status file written")

        # Read it back
        with open("gate_status.json", "r") as f:
            file_status = json.load(f)

        print("📄 Status file contents:")
        for key, value in file_status.items():
            print(f"  {key}: {value}")

        # Check if last_updated is present
        if "last_updated" in file_status:
            print("✅ last_updated field is present")
        else:
            print("❌ last_updated field is MISSING")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_status_writing()
