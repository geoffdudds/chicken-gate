#!/usr/bin/env python3
"""
Quick camera test - run this to see what your camera responds to
"""

import requests

CAMERA_IP = "192.168.0.135"

print(f"Quick test of camera at {CAMERA_IP}")
print("-" * 40)

# Test 1: Basic HTTP connection
try:
    print("1. Testing basic HTTP connection...")
    response = requests.get(f"http://{CAMERA_IP}", timeout=5)
    print(f"   SUCCESS! Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
    print(f"   Size: {len(response.content)} bytes")
    
    # Save response for inspection
    with open("camera_main_page.html", "w") as f:
        f.write(response.text)
    print("   Saved response to camera_main_page.html")
    
except requests.exceptions.ConnectionError:
    print("   FAILED: Connection refused (camera not responding on port 80)")
except requests.exceptions.Timeout:
    print("   FAILED: Timeout")
except Exception as e:
    print(f"   ERROR: {e}")

print()

# Test 2: Try snapshot URLs
print("2. Testing snapshot URLs...")
snapshot_urls = [
    f"http://{CAMERA_IP}/snapshot.jpg",
    f"http://{CAMERA_IP}/image.jpg", 
    f"http://{CAMERA_IP}/tmpfs/auto.jpg",
]

for url in snapshot_urls:
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and len(response.content) > 1000:
            print(f"   SUCCESS! {url}")
            filename = url.split('/')[-1]
            with open(f"test_{filename}", "wb") as f:
                f.write(response.content)
            print(f"   Saved image to test_{filename}")
        else:
            print(f"   No image: {url} (status: {response.status_code})")
    except:
        print(f"   Failed: {url}")

print()

# Test 3: Check what's actually accessible
print("3. Manual check instructions:")
print(f"   - Open browser and go to: http://{CAMERA_IP}")
print(f"   - Try the Tapo app to see camera settings")
print(f"   - Check camera manual for HTTP API documentation")
print(f"   - Look for ONVIF or RTSP stream URLs in camera settings")
