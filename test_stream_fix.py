#!/usr/bin/env python3
"""
Test script to verify the camera stream endpoint fix.
This should return a static image immediately, not hang.
"""

import requests
import time

def test_camera_endpoints():
    """Test both camera endpoints to ensure they don't hang"""
    base_url = "http://localhost:5000"

    endpoints = [
        "/api/camera/snapshot",
        "/api/camera/stream"
    ]

    for endpoint in endpoints:
        print(f"\nTesting {endpoint}...")
        try:
            start_time = time.time()

            # Set a reasonable timeout to prevent hanging
            response = requests.get(f"{base_url}{endpoint}", timeout=10)

            elapsed = time.time() - start_time
            print(f"✅ {endpoint} responded in {elapsed:.2f} seconds")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")

            # Check if response is reasonable
            if elapsed > 5:
                print(f"⚠️  WARNING: Response took {elapsed:.2f} seconds (might be too slow)")

            if response.status_code == 200:
                print(f"✅ {endpoint} returned successful response")
            else:
                print(f"❌ {endpoint} returned status {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"❌ {endpoint} TIMED OUT after 10 seconds!")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} connection failed - is the server running?")
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")

if __name__ == "__main__":
    print("Testing camera endpoint fixes...")
    print("Make sure the Flask app is running on port 5000")
    print("=" * 50)

    test_camera_endpoints()

    print("\n" + "=" * 50)
    print("Test completed!")
    print("Both endpoints should respond quickly with static images on Pi Zero.")
