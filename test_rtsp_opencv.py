#!/usr/bin/env python3
"""
Test RTSP streams from TP-Link Tapo camera using OpenCV
"""

import cv2
import time

# Test RTSP stream with OpenCV
CAMERA_IP = "192.168.0.135"

# Try both streams
streams = [
    f"rtsp://{CAMERA_IP}:554/stream1",  # High quality
    f"rtsp://{CAMERA_IP}:554/stream2"   # Low quality
]

def test_rtsp_stream(stream_url, stream_name):
    """Test a single RTSP stream"""
    print(f"Testing {stream_name}: {stream_url}")

    # Open video capture
    cap = cv2.VideoCapture(stream_url)

    if cap.isOpened():
        print(f"   ✓ {stream_name} opened successfully!")

        # Try to read a frame
        ret, frame = cap.read()
        if ret:
            print(f"   ✓ Frame captured: {frame.shape}")
            # Save frame as image
            filename = f"rtsp_test_{stream_name.lower().replace(' ', '_')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"   ✓ Saved frame to {filename}")

            # Get some stream info
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"   ✓ Stream info: {width}x{height} @ {fps} FPS")

            return True
        else:
            print(f"   ✗ Could not capture frame from {stream_name}")
            return False
    else:
        print(f"   ✗ Could not open {stream_name}")
        return False

    cap.release()

def test_with_credentials():
    """Test RTSP streams with common credentials"""
    print("\nTesting with credentials...")

    # Common credentials for Tapo cameras
    credentials = [
        ("admin", "admin"),
        ("admin", "password"),
        ("", ""),  # No auth
    ]

    for username, password in credentials:
        print(f"\nTrying credentials: {username}:{password}")

        for i, base_url in enumerate([f"rtsp://{CAMERA_IP}:554/stream1", f"rtsp://{CAMERA_IP}:554/stream2"], 1):
            if username and password:
                url = f"rtsp://{username}:{password}@{CAMERA_IP}:554/stream{i}"
            else:
                url = base_url

            print(f"  Testing stream {i}: {url}")

            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"    ✓ SUCCESS with credentials {username}:{password}")
                    filename = f"rtsp_auth_test_stream{i}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"    ✓ Saved to {filename}")
                    cap.release()
                    return True
                else:
                    print(f"    ✗ Opened but no frame")
            else:
                print(f"    ✗ Could not open")
            cap.release()

    return False

if __name__ == "__main__":
    print("OpenCV RTSP Test for TP-Link Tapo Camera")
    print("="*50)

    success = False

    # Test basic streams without auth
    for i, stream_url in enumerate(streams, 1):
        stream_name = f"Stream {i} ({'High' if i == 1 else 'Low'} Quality)"
        if test_rtsp_stream(stream_url, stream_name):
            success = True

    # If basic streams don't work, try with credentials
    if not success:
        print("\nBasic streams failed, trying with authentication...")
        success = test_with_credentials()

    print("\n" + "="*50)
    if success:
        print("✓ RTSP test successful!")
        print("Check the saved .jpg files to see captured frames.")
        print("You can now integrate RTSP into the web application.")
    else:
        print("✗ RTSP test failed")
        print("Possible issues:")
        print("- Camera requires authentication (check Tapo app settings)")
        print("- RTSP is disabled on the camera")
        print("- Network connectivity issues")
        print("- Incorrect stream URLs")

    print("\nNext steps if successful:")
    print("1. Update web_app.py to use OpenCV for RTSP capture")
    print("2. Create snapshot endpoint that captures frames from RTSP")
    print("3. Test the updated web interface")
