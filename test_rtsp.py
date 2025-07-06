#!/usr/bin/env python3
"""
Test RTSP streams from TP-Link Tapo camera
"""

import socket
import requests

CAMERA_IP = "192.168.0.135"

def test_rtsp_port():
    """Test if RTSP port 554 is accessible"""
    print("Testing RTSP port 554...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((CAMERA_IP, 554))
        sock.close()

        if result == 0:
            print("   ✓ Port 554 is OPEN - RTSP service available")
            return True
        else:
            print("   ✗ Port 554 is CLOSED")
            return False
    except Exception as e:
        print(f"   ✗ Error testing port 554: {e}")
        return False

def test_rtsp_urls():
    """Test the RTSP URLs using basic HTTP requests (won't work but shows response)"""
    print("\nTesting RTSP URLs (basic connectivity)...")

    rtsp_urls = [
        f"rtsp://{CAMERA_IP}/stream1",
        f"rtsp://{CAMERA_IP}/stream2",
        f"rtsp://{CAMERA_IP}:554/stream1",
        f"rtsp://{CAMERA_IP}:554/stream2"
    ]

    for url in rtsp_urls:
        print(f"   RTSP URL: {url}")
        # Note: requests can't handle RTSP protocol, but we list the URLs

    print("   Note: RTSP requires special client (like VLC or OpenCV)")

def create_vlc_test_commands():
    """Create VLC commands to test RTSP streams"""
    print("\nVLC Test Commands:")
    print("   Run these in VLC Media Player (Media > Open Network Stream):")
    print(f"   rtsp://{CAMERA_IP}:554/stream1  (high quality)")
    print(f"   rtsp://{CAMERA_IP}:554/stream2  (low quality)")
    print()
    print("   Or from command line (if VLC is installed):")
    print(f"   vlc rtsp://{CAMERA_IP}:554/stream1")
    print(f"   vlc rtsp://{CAMERA_IP}:554/stream2")

def create_opencv_test():
    """Create OpenCV test code"""
    print("\nOpenCV Test Code:")
    print("   Save this to test_rtsp_opencv.py and run it:")
    print("   " + "="*50)

    opencv_code = f'''
import cv2

# Test RTSP stream with OpenCV
CAMERA_IP = "{CAMERA_IP}"

# Try both streams
streams = [
    f"rtsp://{{CAMERA_IP}}:554/stream1",  # High quality
    f"rtsp://{{CAMERA_IP}}:554/stream2"   # Low quality
]

for i, stream_url in enumerate(streams, 1):
    print(f"Testing stream {{i}}: {{stream_url}}")

    # Open video capture
    cap = cv2.VideoCapture(stream_url)

    if cap.isOpened():
        print(f"   ✓ Stream {{i}} opened successfully!")

        # Try to read a frame
        ret, frame = cap.read()
        if ret:
            print(f"   ✓ Frame captured: {{frame.shape}}")
            # Save frame as image
            cv2.imwrite(f"rtsp_test_stream{{i}}.jpg", frame)
            print(f"   ✓ Saved frame to rtsp_test_stream{{i}}.jpg")
        else:
            print(f"   ✗ Could not capture frame from stream {{i}}")
    else:
        print(f"   ✗ Could not open stream {{i}}")

    cap.release()

print("Test complete!")
'''

    with open("test_rtsp_opencv.py", "w") as f:
        f.write(opencv_code.strip())

    print("   Code saved to test_rtsp_opencv.py")
    print("   Run with: python test_rtsp_opencv.py")
    print("   (Requires: pip install opencv-python)")

if __name__ == "__main__":
    print(f"RTSP Camera Test for {CAMERA_IP}")
    print("="*50)

    port_open = test_rtsp_port()
    test_rtsp_urls()

    if port_open:
        print("\n✓ RTSP port is accessible!")
        create_vlc_test_commands()
        create_opencv_test()

        print("\nNext steps:")
        print("1. Test with VLC first to confirm streams work")
        print("2. If VLC works, install opencv-python and run the OpenCV test")
        print("3. If OpenCV works, we can integrate RTSP into the web app")
    else:
        print("\n✗ RTSP port not accessible")
        print("Check camera settings to enable RTSP streaming")
