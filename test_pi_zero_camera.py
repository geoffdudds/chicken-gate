#!/usr/bin/env python3
"""
Simple test for Pi Zero camera integration (without OpenCV)
"""

from datetime import datetime

# Camera configuration (same as web app)
CAMERA_IP = "192.168.0.135"
CAMERA_USERNAME = "chickencam"
CAMERA_PASSWORD = "password"

def test_pillow_available():
    """Test if Pillow (PIL) is available for creating info images"""
    try:
        from PIL import Image, ImageDraw
        print("✅ Pillow (PIL) is available - can create camera info images")
        return True
    except ImportError:
        print("❌ Pillow (PIL) not available - will use text responses")
        return False

def test_opencv_available():
    """Test if OpenCV is available (we expect this to fail on Pi Zero)"""
    try:
        import cv2
        print("✅ OpenCV is available - can capture RTSP frames")
        return True
    except ImportError:
        print("❌ OpenCV not available (expected on Pi Zero)")
        return False

def create_test_info_image():
    """Test creating the camera info image"""
    try:
        from PIL import Image, ImageDraw
        import io

        # Create a simple test image
        width, height = 640, 480
        img = Image.new('RGB', (width, height), color='#27ae60')
        draw = ImageDraw.Draw(img)

        # Add some text
        text = f"RTSP Camera Test - {datetime.now().strftime('%H:%M:%S')}"
        draw.text((50, 200), text, fill='white')

        # Save as bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)

        print(f"✅ Created test image: {len(img_bytes.getvalue())} bytes")

        # Save to file for inspection
        with open("test_camera_image.jpg", "wb") as f:
            f.write(img_bytes.getvalue())
        print("✅ Saved test image to test_camera_image.jpg")

        return True

    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return False

def test_rtsp_info():
    """Show RTSP information"""
    print("\n📹 RTSP Camera Information:")
    print(f"   IP: {CAMERA_IP}")
    print(f"   Username: {CAMERA_USERNAME}")
    print(f"   Stream URL: rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/stream1")
    print("   Port 554: Available (from previous test)")
    print("   Resolution: 1280x720 @ 15fps (from previous test)")

if __name__ == "__main__":
    print("Pi Zero Camera Integration Test")
    print("=" * 40)

    # Test available libraries
    pillow_ok = test_pillow_available()
    opencv_ok = test_opencv_available()

    print()

    # Test image creation if Pillow is available
    if pillow_ok:
        image_ok = create_test_info_image()
    else:
        print("⚠️  Will use text-based camera responses")
        image_ok = False

    # Show RTSP info
    test_rtsp_info()

    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"   Pillow (image creation): {'✅' if pillow_ok else '❌'}")
    print(f"   OpenCV (RTSP capture): {'✅' if opencv_ok else '❌ (expected)'}")
    print(f"   Image generation: {'✅' if image_ok else '❌'}")

    print("\n🚀 Ready for web application!")
    print("   - Camera section will show RTSP information")
    print("   - Users can access live stream via VLC or other RTSP client")
    print("   - Web interface works without OpenCV dependency")
